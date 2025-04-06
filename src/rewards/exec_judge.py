from typing import Optional

from model_exec.model_executor import Message, ModelExecutor
from rewards.judge_resp import JudgeResponse
from rewards.judge_yaml_response_parser import YAMLResponseParser



class JudgeExecutor:
    def __init__(
        self, 
        model_exec: ModelExecutor,
        sys_msg_path: str,
        max_retries: int = 1,
    ):
        self.model_exec = model_exec
        self.max_retries = max_retries

        with open(sys_msg_path, 'r', encoding='utf-8') as f:
            self.relevant_sys_msg = f.read()
    
    def run_judge(
            self,
            conversation_as_str: str
    ) -> Optional[JudgeResponse]:
        """Run the judge to evaluate a conversation with fallback mechanisms."""
        
        user_msg = f'# Conversation\n```{conversation_as_str}\n```\nPlease now provide your output in the yaml format specified.'
        judge_response_str = self.model_exec.execute(
            sys_msg=self.relevant_sys_msg,
            messages=[Message(role="user", content=user_msg)]
        )
        
        # Try to parse the response
        try:
            return YAMLResponseParser.parse_judge_response(judge_response_str)
        except ValueError as e:
            # First fallback: Try to extract just the score
            fallback_response = YAMLResponseParser.extract_score_fallback(judge_response_str)
            if fallback_response:
                return fallback_response
            
            # Second fallback: Retry with error details
            retry_count = 0
            while retry_count < self.max_retries:
                retry_response = self._retry_with_error_details(conversation_as_str, judge_response_str, str(e))
                try:
                    return YAMLResponseParser.parse_judge_response(retry_response)
                except ValueError:
                    # If score extraction works on retry, use that
                    fallback_response = YAMLResponseParser.extract_score_fallback(retry_response)
                    if fallback_response:
                        return fallback_response
                    retry_count += 1
            
            # Ultimate fallback: Return best-effort response
            # If we can extract a score but parsing fails, return with empty thoughts
            score = YAMLResponseParser.extract_score_only(judge_response_str)
            if score is not None:
                return JudgeResponse(thoughts="", score=score)
            
            # Last resort: Return None
            return None

    def _retry_with_error_details(
            self,
            conversation_as_str: str,
            previous_response: str,
            error_message: str
    ) -> str:
        """Retry the judge with error details to guide correction."""
        error_prompt = (
            f"# Previous Failed Response\n\n"
            f"Your previous response failed to parse correctly with this error:\n"
            f"```\n{error_message}\n```\n\n"
            f"Your previous response was:\n"
            f"```\n{previous_response}\n```\n\n"
            f"# Conversation to Judge\n\n"
            f"```\n{conversation_as_str}\n```\n\n"
            f"Please provide a valid YAML response following this exact format:\n"
            f"```yaml\n"
            f"thoughts: \"Your detailed evaluation here\"\n"
            f"score: 0.75  # A float between 0 and 1\n"
            f"```\n"
            f"Ensure valid YAML by:\n"
            f"1. Using proper quote escaping for any quotes in the thoughts text\n"
            f"2. Making sure the score is a valid float number\n"
            f"3. Maintaining correct indentation"
        )
        
        return self.model_exec.execute(
            sys_msg=self.relevant_sys_msg,
            messages=[Message(role="user", content=error_prompt)]
        )