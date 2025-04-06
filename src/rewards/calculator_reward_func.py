import concurrent.futures
import os
from typing import List, Dict, Any, Optional

from model_exec.claude import Claude35HaikuExec
from rewards.exec_judge import JudgeExecutor
from rewards.verifiers.answer_verifier import is_correct_answer


llm_judge = Claude35HaikuExec()
current_dir_of_this_file = os.path.dirname(os.path.abspath(__file__))
tool_judge = JudgeExecutor(
    model_exec=llm_judge,
    sys_msg_path=os.path.join(current_dir_of_this_file, "tool_judge.md"),
)

def _format_conversation_for_judge(prompt_msgs: List[Dict[str, str]], completion_msgs: List[Dict[str, str]]) -> Optional[str]:
    """Formats a single conversation into the required string format for the judge."""
    user_message = None
    # Find the *last* user message in the prompt section as the primary question
    for msg in reversed(prompt_msgs):
        if msg.get("role") == "user":
            user_message = msg.get("content")
            break

    if user_message is None:
        print(f"Warning: Could not find user message in prompt_msgs: {prompt_msgs}")
        return None

    conversation_parts = [f"By: user\n{user_message.strip()}"]

    all_messages = completion_msgs
    for msg in all_messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "").strip()
        conversation_parts.append(f"By: {role}\n{content}")

    # Join with the separator
    return "\n-\n".join(conversation_parts) if conversation_parts else None

def _process_single_conversation_for_judge(prompt_msgs: List[Dict[str, str]], completion_msgs: List[Dict[str, str]]) -> float:
    """Formats and judges a single conversation."""
    conversation_str = _format_conversation_for_judge(prompt_msgs, completion_msgs)

    if conversation_str is None:
        print(f"Warning: Skipping judge for conversation due to formatting error. Prompt: {prompt_msgs}, Completion: {completion_msgs}")
        return 0.0

    try:
        judge_result = tool_judge.run_judge(conversation_as_str=conversation_str)
        return judge_result.score if judge_result and hasattr(judge_result, 'score') else 0.3
    except Exception as e:
        print(f"Error during judging conversation: {e}\nConversation:\n{conversation_str}")
        return 0.0

def judge_tool_use(
    prompts: List[List[Dict[str, str]]],
    completions: List[List[Dict[str, str]]],
    **kwargs: Any
) -> List[float]:
    """
    Judges the tool usage quality for a batch of conversations using an LLM judge.

    Args:
        prompts: List of conversation starts (each a list of message dicts).
        completions: List of conversation continuations (each a list of message dicts).
        **kwargs: Catches extra arguments passed by the trainer.

    Returns:
        List of scores between 0.0 and 1.0.
    """
    if not prompts or not completions:
        return []
    if len(prompts) != len(completions):
         raise ValueError(f"Prompts ({len(prompts)}) and completions ({len(completions)}) must have the same length.")

    rewards = [0.0] * len(prompts)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {
            executor.submit(_process_single_conversation_for_judge, p, c): i
            for i, (p, c) in enumerate(zip(prompts, completions))
        }

        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                score = future.result()
                rewards[index] = score
            except Exception as exc:
                print(f'Conversation at index {index} generated an exception during judging: {exc}')
                rewards[index] = 0.0 # Assign default score on exception

    return rewards

def verify_correctness(
    prompts: List[List[Dict[str, str]]],
    completions: List[List[Dict[str, str]]],
    **kwargs: Any 
) -> List[float]:
    """
    Verifies if the final assistant answer in each conversation is correct
    using the ground truth answer provided in kwargs.

    Args:
        prompts: List of conversation starts (each a list of message dicts).
        completions: List of conversation continuations (each a list of message dicts).
        **kwargs: Catches extra arguments passed by the trainer, expected
                  to contain an "answer" key with a list of correct answers.

    Returns:
        List of scores (1.0 for correct, 0.0 for incorrect).
    """
    if not prompts or not completions:
        return []
    if len(prompts) != len(completions):
        raise ValueError(f"Prompts ({len(prompts)}) and completions ({len(completions)}) must have the same length.")

    correct_answers = kwargs.get("answer")

    if correct_answers is None:
        raise ValueError("Missing 'answer' key in kwargs for verify_correctness.")
    if len(correct_answers) != len(prompts):
         raise ValueError(f"Length mismatch: prompts ({len(prompts)}) vs kwargs['answer'] ({len(correct_answers)}).")

    results = []
    for i, (prompt_msgs, completion_msgs) in enumerate(zip(prompts, completions)):
        if not completion_msgs:
            results.append(0.0)
            continue

        last_message = completion_msgs[-1]

        if last_message.get("role") == "assistant":
            final_assistant_response = last_message.get("content", "")
            correct_answer_for_this_prompt = correct_answers[i]
            try:
                is_correct = is_correct_answer(
                    agent_answer=final_assistant_response,
                    correct_answer=correct_answer_for_this_prompt
                )
                results.append(1.0 if is_correct else 0.0)
            except Exception as e:
                 print(f"Error during verification for index {i}: {e}. Agent answer: '{final_assistant_response}', Correct answer: '{correct_answer_for_this_prompt}'")
                 results.append(0.0)
        else:
            results.append(0.0)

    return results
