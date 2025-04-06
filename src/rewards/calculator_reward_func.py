import concurrent.futures
import os
from typing import List

from model_exec.claude import Claude35HaikuExec
from rewards.exec_judge import JudgeExecutor
from rewards.verifiers.answer_verifier import is_correct_answer


llm_judge = Claude35HaikuExec()

current_dir_of_this_file = os.path.dirname(os.path.abspath(__file__))

tool_judge = JudgeExecutor(
    model_exec=llm_judge,
    sys_msg_path=os.path.join(current_dir_of_this_file, "tool_judge.md"),
)

def judge_tool_use(prompts: List[str], completions: List[str]) -> List[float]:
    """
    Judge the tool usage by the agent.

    Args:
        prompts: List of prompts
        completions: List of completions

    Returns:
        List of scores between 0.0 and 1.0
    """
    assert len(prompts) == len(completions), "Prompts and completions must have the same length"

    # TODO: View the args so I can turn into a str for the judge.

    # with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    #     rewards = list(executor.map(process_single_conversation, tool_sample_results))

    return []

def verify_correctness(prompts: List[str], completions: List[str]) -> List[float]:
    answers = []
    for prompt, completion in zip(prompts, completions):
        answer = 1.0 if is_correct_answer(prompt, completion) else 0.0
        answers.append(answer)