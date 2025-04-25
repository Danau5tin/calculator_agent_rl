# Calculator agent training

## For local dev
As a temp solution whilst [verifiers](https://github.com/willccbb/verifiers) is not on PyPI, clone verifiers at the same level as calculator_agent_rl.
```
 -
  |
   -- calculator_agent_rl/
   -- verfifers/
```
This is required in order to access the verifiers lib.

Use the devcontainer and Dockerfile for development. If using VSCode this should popup automatically.

## Deployment
0. Rent GPU from somewhere like runpod and connect via SSH
1. Install uv `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Open workspace dir & Clone repo into `/workspace` `git clone https://{githubaccess_token}@github.com/AiTuning-Ltd/{repo}.git`
3. Clone verifiers into `/workspace` `git clone https://github.com/willccbb/verifiers.git`
4. Follow when deployed steps below

### When deployed onto a training node
**The below example code runs Qwen 2.5 3B on 8x GPUs (x4 for inference, x4 for training)**
1. Run `uv sync` after the verifiers repo is cloned too as mentioned above.
2. Run `uv add flash-attn --no-build-isolation`
3. Ensure .env file is set at the root of the project
4. Run vLLM server (Example for a x4 GPUs):
    a. `cd ../verifiers`
    b. `CUDA_VISIBLE_DEVICES=0,1,2,3 python verifiers/inference/vllm_serve.py --model "Qwen/Qwen2.5-3B-Instruct" --tensor_parallel_size 4 --max_model_len 8192  --gpu_memory_utilization 0.9 --enable_prefix_caching True`
5. Run train.py using accelerate (Example on x4 GPUs):
`CUDA_VISIBLE_DEVICES=4,5,6,7 accelerate launch --num-processes 4 --config-file ../verifiers/configs/zero3.yaml src/train.py`

### Deployment issue fixes

**If GPUs hang at 100% utilisation for both vLLM or training script initialisation**
0. Ensure you are using CUDA version 12.4+
1. Stop the processes
2. In the terminal: `export NCCL_P2P_DISABLE=1`. Fix found [here](https://github.com/vllm-project/vllm/issues/14449#issuecomment-2739372704)
3. Re-run script

**If error in verfiers package about `"question"`**
1. Go to `data_utils.py` in verifiers and change `"question"` to `'question'` on lines 118 & 132

**If Anthropic API key is not loading onto each GPU for judge**
1. Go to `claude.py` & change `Anthropic()` to `Anthropic(api_key="{api_key}")`