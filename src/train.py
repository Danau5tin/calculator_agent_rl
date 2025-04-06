import datetime
import logging
import os
from typing import Literal
from verifiers import GRPOEnvTrainer
from verifiers import get_model_and_tokenizer

from environment.calculator_env import CalculatorEnv

from datasets import load_dataset, Dataset
from trl import GRPOConfig
from dotenv import load_dotenv
load_dotenv()


logger = logging.getLogger(__name__)
current_file_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
NUM_SAMPLES = 8

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
model_short_name = MODEL_NAME.split('/')[-1]
run_name = f"{model_short_name}_calculator_samples{NUM_SAMPLES}_{timestamp}"

def load_sys_msg(file_path: str) -> str:
    """Loads the system message from a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        sys_msg = f.read()
    return sys_msg


def load_csv_dataset(file_path: str, ds_type: Literal["train", "eval"]) -> Dataset:
    """Loads a CSV dataset from the given file path."""
    train_dataset = load_dataset("csv", data_files=file_path)[ds_type]
    logger.info(f"Dataset loaded with {len(train_dataset['question'])} prompts")
    return train_dataset

train_dset = load_csv_dataset(os.getenv("TRAIN_DSET_PATH"), ds_type="train")
system_msg = load_sys_msg(os.getenv("SYS_MSG_PATH"))


# TODO: Fully implement the CalculatorEnv class
calc_env = CalculatorEnv(
    dataset=train_dset,
    system_prompt=system_msg,
    max_steps=5,
)

training_args=GRPOConfig(
    output_dir=f"outputs/{run_name}",
    run_name=run_name,
    learning_rate=1e-6,
    lr_scheduler_type="constant_with_warmup",
    warmup_steps=10,
    num_train_epochs=1,
    temperature=0.9,
    bf16=True,
    max_grad_norm=0.1,
    num_iterations=2,
    beta=0.002,
    max_prompt_length=1024,
    max_completion_length=500,
    per_device_train_batch_size=12,
    num_generations=8,
    gradient_accumulation_steps=1,
    gradient_checkpointing=True,
    save_strategy="steps",
    save_steps=100,
    save_only_model=True,
    use_vllm=True,
    vllm_server_host="0.0.0.0",
    vllm_server_port=8000,
    vllm_gpu_memory_utilization=0.9,
    logging_steps=5,
    log_completions=True,
    report_to="wandb",
    reward_weights=calc_env.get_reward_weights()
)

model, tokenizer = get_model_and_tokenizer(MODEL_NAME)

trainer = GRPOEnvTrainer(
    model=model,
    processing_class=tokenizer,
    reward_funcs=calc_env.get_reward_funcs(),
    env=calc_env,
    args=training_args,
    train_dataset=train_dset,
)

trainer.train()