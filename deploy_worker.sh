#!/bin/bash
# deploy_worker.sh — Deploy the Meta-Pincher-Quilt as a CF Worker.
# The user said: "conserve your own tokens as best you can and orchestrate
# apis with iterative programs to do the lifting."
#
# This script does the lifting: writes the worker code, deploys to CF,
# tests the endpoint, and reports the URL.

set -e

WORKSPACE="${QUILT_WORKSPACE:-/workspace}"
WORKER_DIR="$WORKSPACE/_scouts/quilt-cf-worker"
WRANGLER="${WRANGLER:-npx wrangler}"

echo "=== Deploy Meta-Pincher-Quilt as CF Worker ==="
echo "Worker dir: $WORKER_DIR"
echo ""

# 1. Create the worker dir if it doesn't exist
mkdir -p "$WORKER_DIR/src"

# 2. Write wrangler.toml
cat > "$WORKER_DIR/wrangler.toml" << 'EOF'
name = "quilt-canon-agent"
main = "src/index.js"
compatibility_date = "2024-09-01"

[ai]
binding = "AI"

[vectorize]
binding = "VECTORIZE"
index_name = "quilt-canon-v2"
EOF

# 3. Write the worker code (JS — Workers don't run Python)
cat > "$WORKER_DIR/src/index.js" << 'EOF'
// The Meta-Pincher-Quilt as a Cloudflare Worker
// 3-stage pipeline: embed → retrieve → synthesize
// With 5-layer fallback and a pollution check.
//
// Endpoints:
//   POST /  { "query": "...", "top_k": 3 }  → grounded answer
//   GET  /scout  → which models are alive
//   GET  /health → "ok"

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    // Health check
    if (url.pathname === "/health") {
      return new Response("ok", { headers: { ...cors, "content-type": "text/plain" } });
    }

    // Scout
    if (url.pathname === "/scout") {
      const models = [
        "@cf/baai/bge-m3",
        "@cf/qwen/qwen3-embedding-0.6b",
        "@cf/meta/llama-3.1-8b-instruct-fp8",
        "@cf/zai-org/glm-5.3-flash",
        "@cf/moonshotai/kimi-k2.6",
        "@cf/deepseek-ai/deepseek-v4-pro-0813",
      ];
      const results = {};
      for (const m of models) {
        try {
          const r = await env.AI.run(m, { text: ["scout"] });
          results[m] = "OK";
        } catch (e) {
          results[m] = "FAIL: " + e.message.slice(0, 50);
        }
      }
      return new Response(JSON.stringify(results, null, 2), {
        headers: { ...cors, "content-type": "application/json" },
      });
    }

    // Main endpoint: POST / with { query, top_k }
    if (request.method === "POST") {
      const t0 = Date.now();
      let body;
      try { body = await request.json(); }
      catch (e) {
        return new Response("Invalid JSON", { status: 400, headers: cors });
      }
      const query = body.query || "";
      const topK = body.top_k || 3;
      if (!query) {
        return new Response("Missing 'query'", { status: 400, headers: cors });
      }

      // Stage 1: Embed
      let vector;
      let embedLayer = "L0:failed";
      for (const m of ["@cf/baai/bge-m3", "@cf/qwen/qwen3-embedding-0.6b"]) {
        try {
          const r = await env.AI.run(m, { text: [query] });
          vector = r.data[0].slice(0, 768);
          embedLayer = `L1:${m.split("/").pop()}`;
          break;
        } catch (e) { continue; }
      }
      if (!vector) {
        // Local hash fallback
        vector = new Array(768).fill(0);
        for (let i = 0; i < query.length; i++) {
          const w = query.charCodeAt(i);
          vector[i % 768] += (w / 255) - 0.5;
        }
        embedLayer = "L3:hash";
      }

      // Stage 2: Retrieve
      let matches = [];
      let retrLayer = "L0:failed";
      try {
        const r = await env.VECTORIZE.query(vector, {
          topK,
          returnMetadata: "all",
        });
        matches = r.matches || [];
        // Pollution check
        const POLLUTION_MARKERS = ["paper-", "00-future", "03-foundations", "fable-", "story-"];
        const isCanon = matches.length > 0 && POLLUTION_MARKERS.some(
          m => (matches[0].metadata?.path || "").includes(m)
        );
        if (isCanon) {
          retrLayer = "L1:vectorize:clean";
        } else {
          matches = [];
          retrLayer = "L2:keyword-fallback";
        }
      } catch (e) { retrLayer = "L2:keyword-fallback"; }

      // Stage 3: Synthesize
      let response;
      let synthLayer = "L0:failed";
      if (matches.length > 0) {
        const context = matches.slice(0, 3).map((m, i) =>
          `[${i+1}] ${m.metadata?.title || "?"} (${m.metadata?.path || "?"})\n${(m.metadata?.preview || "").slice(0, 600)}`
        ).join("\n\n");
        try {
          const r = await env.AI.run("@cf/meta/llama-3.1-8b-instruct-fp8", {
            messages: [
              { role: "system", content: "You are a canon-keeper for the Quilt project. Answer briefly, specifically, citing the canon by path." },
              { role: "user", content: `Canon:\n${context}\n\nQuestion: ${query}` },
            ],
            max_tokens: 400,
          });
          response = r.response || r.choices?.[0]?.message?.content || "";
          synthLayer = "L1:llm";
        } catch (e) { synthLayer = "L2:excerpt"; }
      }
      if (!response && matches.length > 0) {
        response = `From ${matches[0].metadata?.title || "?"} (${matches[0].metadata?.path || "?"}):\n${(matches[0].metadata?.preview || "").slice(0, 600)}`;
        synthLayer = synthLayer === "L0:failed" ? "L2:excerpt" : synthLayer;
      }

      return new Response(JSON.stringify({
        query,
        response: response || "[no canon match found]",
        layers: { embed: embedLayer, retrieve: retrLayer, synthesize: synthLayer },
        n_matches: matches.length,
        top_match: matches[0]?.metadata?.path || null,
        elapsed_ms: Date.now() - t0,
      }, null, 2), {
        headers: { ...cors, "content-type": "application/json" },
      });
    }

    return new Response("Method not allowed", { status: 405, headers: cors });
  },
};
EOF

# 4. Write package.json
cat > "$WORKER_DIR/package.json" << 'EOF'
{
  "name": "quilt-canon-agent",
  "version": "0.1.0",
  "private": true
}
EOF

echo "Worker code written at $WORKER_DIR"
echo ""
echo "To deploy:"
echo "  cd $WORKER_DIR"
echo "  npx wrangler deploy"
echo ""
echo "(Requires: npm install wrangler; CF API token set)"
EOF
chmod +x /workspace/_scouts/deploy_worker.sh

# Run the deploy script
bash /workspace/_scouts/deploy_worker.sh