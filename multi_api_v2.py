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
    """Cloudflare Workers AI — free fallback."""
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
        return data.get("result", {}).get("response", "")
    except urllib.error.HTTPError as e:
        return f"[cf HTTP {e.code}: {e.read()[:80]!r}]"
    except Exception as e:
        return f"[cf err: {e}]"


# ─── 7-VOICE MAP ───
VOICES = {
    "zai":     {"name": "ZAI GLM-4.5",       "model": "GLM-4.5", "kind": "zai"},
    "llama70b":{"name": "Llama 70B",         "model": "meta-llama/Meta-Llama-3.1-70B-Instruct", "kind": "di"},
    "llama405b":{"name": "Llama 405B",       "model": "meta-llama/Meta-Llama-3.1-405B-Instruct", "kind": "di"},
    "hermes":  {"name": "Hermes 405B",       "model": "NousResearch/hermes-3-llama-3.1-405b",   "kind": "di"},
    "wizard":  {"name": "Wizard 8x22B",      "model": "microsoft/WizardLM-2-8x22B",            "kind": "di"},
    "mixtral": {"name": "Mixtral 8x7B",      "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",  "kind": "di"},
    "deepseek":{"name": "DeepSeek",          "model": "deepseek-chat",                          "kind": "ds"},
    "qwen32b": {"name": "Qwen 2.5 Coder 32B","model": "@cf/qwen/qwen2.5-coder-32b-instruct",    "kind": "cf"},
    "cf8b":    {"name": "Cloudflare Llama 8B","model": "@cf/meta/llama-3.1-8b-instruct",         "kind": "cf"},
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
        return name, call_cloudflare(prompt, system, model=v["model"], max_tokens=max_tokens)
    return name, "[unreachable]"
