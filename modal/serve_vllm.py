"""Serve an open-weight model as an OpenAI-compatible endpoint on Modal with vLLM.

    modal secret create neuronbench-vllm VLLM_API_KEY=<any random string>
    MODEL=openai/gpt-oss-120b modal deploy modal/serve_vllm.py
    MODEL=Qwen/Qwen3-32B      modal deploy modal/serve_vllm.py
    MODEL=Qwen/Qwen3-0.6B GPU=L4 modal deploy modal/serve_vllm.py

Each deploy prints a URL like https://<workspace>--nb-vllm-gpt-oss-120b-serve.modal.run. Point mini-SWE-agent at
<URL>/v1 with model `hosted_vllm/<MODEL>` and api key VLLM_API_KEY (see README). Containers scale to zero after 15 idle
minutes; the first request after that waits for a cold start (several minutes for the weights to load).
"""

import os
import re
import subprocess

import modal

MODEL = os.environ.get("MODEL", "openai/gpt-oss-120b")
GPU = os.environ.get("GPU", "H100")
MAX_LEN = int(os.environ.get("MAX_MODEL_LEN", "32768"))
PORT = 8000

image = (
    modal.Image.from_registry("nvidia/cuda:12.8.1-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm==0.11.0", "huggingface_hub[hf_transfer]")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "NB_MODEL": MODEL, "NB_MAX_LEN": str(MAX_LEN)})
)
hf_cache = modal.Volume.from_name("nb-hf-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("nb-vllm-cache", create_if_missing=True)

app = modal.App("nb-vllm-" + re.sub(r"[^a-z0-9-]", "-", MODEL.split("/")[-1].lower()))


@app.function(image=image, gpu=GPU, timeout=24 * 60 * 60, scaledown_window=15 * 60,
              volumes={"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache},
              secrets=[modal.Secret.from_name("neuronbench-vllm")])
@modal.concurrent(max_inputs=32)
@modal.web_server(port=PORT, startup_timeout=30 * 60)
def serve():
    cmd = ["vllm", "serve", os.environ["NB_MODEL"], "--host", "0.0.0.0", "--port", str(PORT),
           "--max-model-len", os.environ["NB_MAX_LEN"], "--served-model-name", os.environ["NB_MODEL"]]
    # mini-SWE-agent always sends a bash tool, so every model needs a tool-call parser.
    if "Qwen3" in os.environ["NB_MODEL"]:
        cmd += ["--enable-auto-tool-choice", "--tool-call-parser", "hermes", "--reasoning-parser", "qwen3"]
    elif "gpt-oss" in os.environ["NB_MODEL"]:
        cmd += ["--enable-auto-tool-choice", "--tool-call-parser", "openai"]
    # vLLM reads VLLM_API_KEY from the environment and requires it as a bearer token on every request.
    subprocess.Popen(cmd)
