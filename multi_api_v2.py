"""
multi_api_v2.py — Updated orchestrator with verified working voices.

7 voices, 7 specialties:
  ZAI GLM-4.5 (not Air) — flagship creative
  DeepInfra Llama 70B   — practitioner whiteboard
  DeepInfra Hermes 405B — hidden-symmetry seeker
  DeepInfra Wizard 8x22B — landscape-ecologist
  DeepInfra Mixtral 8x7B — multidisciplinary blender
  DeepSeek Reasoner     — code/dense technical
  Cloudflare Workers AI — 8B Mistral / Llama (free fallback)
"""
import json
import os
import urllib.error
import urllib.request
from typing import Optional

ZAI_TOKEN = os.environ.get("ZAI_TOKEN", "")
DEEPSEEK_TOKEN = os.environ.get("DEEPSEEK_TOKEN", "")
DEEPINFRA_TOKEN = os.environ.get("DEEPINFRA_TOKEN", "")
CLOUDFLARE_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
ANTHROPIC_TOKEN = os.environ.get("ANTHROPIC_TOKEN", "")  # not currently funded

# Resolve CF account ID once
CF_ACCOUNT_ID = ""
if CLOUDFLARE_TOKEN:
    try:
        req = urllib.request.Request(
            "https://api.cloudflare.com/client/v4/accounts",
            headers={"Authorization": f"Bearer {CLOUDFLARE_TOKEN}"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.load(r)
        if data.get("result"):
            CF_ACCOUNT_ID = data["result"][0]["id"]
    except Exception:
        pass


def call_zai(prompt: str, system: str = "", model: str = "GLM-4.5", max_tokens: int = 4096) -> Optional[str]:
    """ZAI flagship creative writing. Use GLM-4.5 (NOT Air — Air is exhausted)."""
    if not ZAI_TOKEN:
        return None
    url = "https://api.z.ai/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZAI_TOKEN}", "Content-Type": "application/json"}
    messages = []
    if system: messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.load(r)
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"[zai HTTP {e.code}: {e.read()[:80]!r}]"
    except Exception as e:
        return f"[zai err: {e}]"


def call_deepseek(prompt: str, system: str = "", model: str = "deepseek-chat", max_tokens: int = 4096) -> Optional[str]:
    """DeepSeek — code/dense technical."""
    if not DEEPSEEK_TOKEN:
        return None
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_TOKEN}", "Content-Type": "application/json"}
    messages = []
    if system: messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"[deepseek HTTP {e.code}: {e.read()[:80]!r}]"
    except Exception as e:
        return f"[deepseek err: {e}]"


def call_deepinfra(prompt: str, system: str = "", model: str = "meta-llama/Meta-Llama-3.1-70B-Instruct", max_tokens: int = 4096) -> Optional[str]:
    """DeepInfra — many models. Switch with model= parameter."""
    if not DEEPINFRA_TOKEN:
        return None
    url = "https://api.deepinfra.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPINFRA_TOKEN}", "Content-Type": "application/json"}
    messages = []
    if system: messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"[deepinfra HTTP {e.code}: {e.read()[:80]!r}]"
    except Exception as e:
        return f"[deepinfra err: {e}]"


def call_cloudflare(prompt: str, system: str = "", model: str = "@cf/meta/llama-3.1-8b-instruct", max_tokens: int = 1024) -> Optional[str]:
    """Cloudflare Workers AI — free fallback. Supports both
    raw-response (Llama-style) and OpenAI-style (Kimi) outputs."""
    if not CLOUDFLARE_TOKEN or not CF_ACCOUNT_ID:
        return None
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{model}"
    headers = {"Authorization": f"Bearer {CLOUDFLARE_TOKEN}", "Content-Type": "application/json"}
    messages = []
    if system: messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = {"messages": messages, "max_tokens": max_tokens}
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        result = data.get("result", {})
        # OpenAI style (Kimi, GPT-OSS)
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        # Raw style (Llama)
        if "response" in result:
            return result["response"]
        return str(result)[:200]
    except urllib.error.HTTPError as e:
        return f"[cf HTTP {e.code}: {e.read()[:80]!r}]"
    except Exception as e:
        return f"[cf err: {e}]"


# ─── 7-VOICE MAP ───
VOICES = {
    "zai":      {"name": "ZAI GLM-4.5",         "model": "GLM-4.5",                                            "kind": "zai"},
    "llama70b": {"name": "Llama 70B",           "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",             "kind": "di"},
    "llama33":  {"name": "Llama 3.3 70B",       "model": "meta-llama/Llama-3.3-70B-Instruct",                  "kind": "di"},
    "llama4":   {"name": "Llama 4 Scout 17B",   "model": "meta-llama/Llama-4-Scout-17B-16E-Instruct",         "kind": "di"},
    "llama405b":{"name": "Llama 405B",          "model": "meta-llama/Meta-Llama-3.1-405B-Instruct",           "kind": "di"},
    "hermes":   {"name": "Hermes 405B",         "model": "NousResearch/hermes-3-llama-3.1-405b",               "kind": "di"},
    "wizard":   {"name": "Wizard 8x22B",        "model": "microsoft/WizardLM-2-8x22B",                         "kind": "di"},
    "mixtral":  {"name": "Mixtral 8x7B",        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",               "kind": "di"},
    "deepseek": {"name": "DeepSeek",            "model": "deepseek-chat",                                       "kind": "ds"},
    "qwq":      {"name": "QwQ 32B Reasoner",    "model": "Qwen/QwQ-32B-Preview",                                "kind": "di"},
    "qwen72":   {"name": "Qwen 2.5 72B",        "model": "Qwen/Qwen2.5-72B-Instruct",                           "kind": "di"},
    "gemma3":   {"name": "Gemma 3 27B",         "model": "google/gemma-3-27b-it",                               "kind": "di"},
    "phi4":     {"name": "Phi-4",               "model": "microsoft/phi-4",                                     "kind": "di"},
    "seed2":    {"name": "Seed 2.0-mini",       "model": "ByteDance/Seed-2.0-mini",                             "kind": "di"},
    "kimi":     {"name": "Kimi K2 (via CF)",    "model": "@cf/moonshotai/kimi-k2.7-code",                       "kind": "cf"},
    "kimi26":   {"name": "Kimi K2.6 (via CF)",  "model": "@cf/moonshotai/kimi-k2.6",                            "kind": "cf"},
    "gptoss":   {"name": "GPT-OSS 120B",        "model": "@cf/openai/gpt-oss-120b",                             "kind": "cf"},
    "cf8b":     {"name": "Cloudflare Llama 8B", "model": "@cf/meta/llama-3.1-8b-instruct",                       "kind": "cf"},
    "qwen32b":  {"name": "Qwen 2.5 Coder 32B",  "model": "@cf/qwen/qwen2.5-coder-32b-instruct",                 "kind": "cf"},
    "qwen38":   {"name": "Qwen 3.8 27B",        "model": "@cf/qwen/qwen3.8-27b",                                "kind": "cf"},
    "qwen3":    {"name": "Qwen 3 30B",          "model": "@cf/qwen/qwen3-30b-a3b-fp8",                          "kind": "cf"},
    "dsr1":     {"name": "DeepSeek R1 (distill)","model": "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",       "kind": "cf"},
    "dsv4p":    {"name": "DeepSeek V4 Pro",     "model": "@cf/deepseek-ai/deepseek-v4-pro-0813",                "kind": "cf"},
    "dsv4f":    {"name": "DeepSeek V4 Flash",   "model": "@cf/deepseek-ai/deepseek-v4-flash-0731",              "kind": "cf"},
    "glm53f":   {"name": "GLM 5.3-flash",       "model": "@cf/zai-org/glm-5.3-flash",                           "kind": "cf"},
    "glm52":    {"name": "GLM 5.2",             "model": "@cf/zai-org/glm-5.2",                                 "kind": "cf"},
    "glm47f":   {"name": "GLM 4.7-flash",       "model": "@cf/zai-org/glm-4.7-flash",                           "kind": "cf"},
    "gemma4":   {"name": "Gemma 4 26B",         "model": "@cf/google/gemma-4-26b-a4b-it",                       "kind": "cf"},
    "mistral31":{"name": "Mistral Small 3.1",   "model": "@cf/mistralai/mistral-small-3.1-24b-instruct",        "kind": "cf"},
}


def call_voice(name: str, prompt: str, system: str = "", max_tokens: int = 4096) -> tuple:
    if name not in VOICES:
        return name, f"[unknown voice {name}]"
    v = VOICES[name]
    if v["kind"] == "zai":
        return name, call_zai(prompt, system, model=v["model"], max_tokens=max_tokens)
    if v["kind"] == "di":
        return name, call_deepinfra(prompt, system, model=v["model"], max_tokens=max_tokens)
    if v["kind"] == "ds":
        return name, call_deepseek(prompt, system, model=v["model"], max_tokens=max_tokens)
    if v["kind"] == "cf":
        # Reasoning models (Kimi, GLM 5.x, DeepSeek V4, Qwen 3.8) need 8x
        # tokens for thinking. Non-reasoning need 1x.
        reasoning = name in ("kimi", "kimi26", "glm53f", "glm52", "glm47f",
                             "dsv4p", "dsv4f", "qwen38")
        actual_max = max_tokens * 8 if reasoning else max_tokens
        return name, call_cloudflare(prompt, system, model=v["model"], max_tokens=actual_max)
    return name, "[unreachable]"
