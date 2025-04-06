import json
import re
from typing import Any, Dict, List, Optional, Tuple
from rewards.calculator_reward_func import judge_tool_use, verify_correctness
from verifiers import RewardFunc
from verifiers.envs.multiturn_env import MultiTurnEnv

from environment.tools.calculator import Expression, calculate



class CalculatorEnv(MultiTurnEnv):
    def get_reward_funcs(self, **kwargs: Any) -> List[RewardFunc]:
        return [judge_tool_use, verify_correctness]

    def get_reward_weights(self, **kwargs: Any) -> List[float]:
       return [0.80, 0.20]

    def is_completed(self, messages: List[Dict[str, str]], **kwargs: Any) -> bool:       
        """Checks if the response is complete. The response is considered complete if it contains a valid action."""       
        content = messages[-1]["content"]       
        action_id, _ = self._extract_agent_action(content)

        if action_id == "calculator":
            return False
        return True
    
    def _build_env_resp_dict(self, content: str) -> Dict[str, str]:
        return {"role": "user", "content": content}

    def env_response(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, str]:
        content = messages[-1]["content"]
        action_id, action_content = self._extract_agent_action(content)
        if action_id == "calculator":

            try:
                expression = Expression.from_dict(json.loads(action_content))
            except Exception as e:
                self.logger.error(f"Failed to parse calculator expression: {e}")
                return self._build_env_resp_dict("Error: Unable to parse yaml expression inside <calculator> tag.")
            
            try:
                result = calculate(expression)
                result_str = f"<output>{result}</output>"
                return self._build_env_resp_dict(result_str)
            except Exception as e:
                self.logger.error(f"Failed to calculate expression: {e}")
                return self._build_env_resp_dict(f"Error: Unable to calculate the expression. Details: {str(e)[0:100]}")
            
        return self._build_env_resp_dict("Error: No <calculator> tag found in the response.")


    def _extract_agent_action(self, content: str) -> Tuple[Optional[str], Optional[str]]:
        """Finds all instances of <identifier>content</identifier> """
        pattern = r'<([^>]+)>(.*?)</\1>'
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            return None, None
        
        if len(matches) > 1:
            self.logger.warning("Multiple tags found in a single response. Using only the first tag. Consider using stop strings to prevent this.")
            self.logger.debug(f"All tags found: {[match[0] for match in matches]}")
        
        return matches[0]