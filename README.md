# Calculator agent training

## Setup
As a temp solution whilst [verifiers](https://github.com/willccbb/verifiers) is not on PyPI, clone verifiers at the same level as calculator_agent_rl.
```
 -
  |
   -- calculator_agent_rl/
   -- verfifers/
```
This is required in order to access the verifiers lib.

## For local dev
Use the devcontainer and Dockerfile for development. If using VSCode this should popup automatically.

## When deployed onto a training node
**The below example code runs Qwen 2.5 3B on 8x GPUs (x4 for inference, x4 for training)**
1. Run `uv sync` after the verifiers repo is cloned too as mentioned above.
2. Run `uv add flash-attn --no-build-isolation`
3. Ensure .env file is set at the root of the project
4. Run vLLM server (Example for a x4 GPUs):
    a. `cd ../verifiers`
    b. `CUDA_VISIBLE_DEVICES=0,1,2,3 python verifiers/inference/vllm_serve.py --model "Qwen/Qwen2.5-3B-Instruct" --tensor_parallel_size 4 --max_model_len 8192  --gpu_memory_utilization 0.9 --enable_prefix_caching True`
5. Run train.py using accelerate (Example on x4 GPUs):
`CUDA_VISIBLE_DEVICES=4,5,6,7 accelerate launch --num-processes 4 --config-file ../verifiers/configs/zero3.yaml src/train.py`