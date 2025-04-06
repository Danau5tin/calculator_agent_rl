import re
import math

def is_correct_answer(agent_answer: str, correct_answer: str, tolerance: float = 0.1) -> bool:
    """
    Check if the agent's answer is correct by extracting the last numerical value
    and comparing it to the correct answer within a given tolerance using math.isclose
    for robust floating-point comparison.

    Args:
        agent_answer: The agent's answer (string containing at least one numerical value).
        correct_answer: The correct answer (string that can be converted to float).
        tolerance: The allowed absolute difference between the agent's numerical
                   answer and the correct numerical answer. Defaults to 1e-6.

    Returns:
        True if the last numerical value in the agent's answer is close enough
        to the correct answer based on the absolute tolerance, False otherwise.
    """
    # Revised Pattern: Captures the entire number string including potential exponent
    # and optional trailing percentage sign. Handles commas.
    pattern = r"(-?[\d,]*\.?\d+(?:[eE][-+]?\d+)?%?|-?\.\d+(?:[eE][-+]?\d+)?%?)"
    matches = re.findall(pattern, agent_answer)

    valid_numbers = []
    for match_str in matches:
        num = _clean_number_string(match_str)
        if not math.isnan(num):
             valid_numbers.append(num)

    if not valid_numbers:
        return False

    try:
        agent_numerical = valid_numbers[-1]
        correct_numerical = _clean_number_string(correct_answer)

        if math.isnan(agent_numerical) or math.isnan(correct_numerical):
             return False

        return math.isclose(agent_numerical, correct_numerical, rel_tol=0.0, abs_tol=tolerance)

    except (ValueError, TypeError) as e:
        print(f"Error processing answers: {e}")
        return False
    except IndexError:
        return False

def _clean_number_string(number_str: str) -> float:
    """Removes thousand separators, handles percentages, and converts to float."""
    if not isinstance(number_str, str):
        number_str = str(number_str)

    cleaned_str = number_str.replace(',', '')
    is_percentage = False
    if cleaned_str.endswith('%'):
        if len(cleaned_str) > 1: # Ensure it's not just "%"
            cleaned_str = cleaned_str[:-1]
            is_percentage = True
        else:
             return float('nan')

    try:
        value = float(cleaned_str)
        if is_percentage:
            value /= 100.0
        return value
    except ValueError:
        return float('nan')