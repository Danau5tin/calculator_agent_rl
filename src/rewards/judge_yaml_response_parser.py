import re
from typing import Optional

import yaml

from rewards.judge_resp import JudgeResponse



class YAMLResponseParser:
    """Class responsible for parsing YAML responses from judge models."""
    
    @staticmethod
    def parse_judge_response(response: str) -> JudgeResponse:
        """Parse the judge response with improved error handling."""
        # Find the YAML block with or without markdown code blocks
        yaml_pattern = r"(?:```(?:yaml)?\n)?(thoughts:.+?score:\s*([0-9]*\.?[0-9]+))(?:\n```)?$"
        match = re.search(yaml_pattern, response, re.DOTALL | re.MULTILINE)

        if not match:
            raise ValueError("Could not find valid YAML block in judge response")

        try:
            yaml_content = match.group(1)
            # Pre-process the YAML to handle common formatting issues
            yaml_content = YAMLResponseParser._preprocess_yaml(yaml_content)
            
            parsed_yaml = yaml.safe_load(yaml_content)

            if not isinstance(parsed_yaml, dict):
                raise ValueError(f"Parsed YAML is not a dictionary object: {parsed_yaml}")

            if 'score' not in parsed_yaml or 'thoughts' not in parsed_yaml:
                raise ValueError(f"Parsed YAML does not contain 'score' or 'thoughts' keys: {parsed_yaml}")

            score = float(parsed_yaml['score'])
            thoughts = parsed_yaml['thoughts']

            return JudgeResponse(thoughts=thoughts, score=score)

        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML content: {str(e)}. Response: {response}")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Error processing score value: {str(e)}. Response: {response}")

    @staticmethod
    def _preprocess_yaml(yaml_content: str) -> str:
        """Preprocess YAML content to fix common issues."""
        # Fix issues with unescaped quotes in thoughts value
        lines = yaml_content.split('\n')
        processed_lines = []
        
        in_thoughts = False
        thoughts_value = ""
        
        for line in lines:
            if line.startswith('thoughts:'):
                in_thoughts = True
                if '"' in line[len('thoughts:'):]:
                    # Extract the value and ensure proper quoting
                    value = line[len('thoughts:'):].strip()
                    if value.startswith('"') and value.endswith('"'):
                        # Already quoted, just need to make sure internal quotes are escaped
                        value = value[1:-1].replace('"', '\\"')
                        thoughts_value = f'thoughts: "{value}"'
                    else:
                        # Add quotes
                        escaped_value = value.replace('"', '\\"') 
                        thoughts_value = f'thoughts: "{escaped_value}"' 
                    processed_lines.append(thoughts_value)
                else:
                    processed_lines.append(line)
            elif in_thoughts and line.startswith('score:'):
                in_thoughts = False
                processed_lines.append(line)
            elif in_thoughts:
                # This is a continuation of thoughts
                thoughts_value += " " + line.strip().replace('"', '\\"')
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    @staticmethod
    def extract_score_fallback(response: str) -> Optional[JudgeResponse]:
        """Extract just the score as a fallback when YAML parsing fails."""
        score = YAMLResponseParser.extract_score_only(response)
        if score is not None:
            # Get any text that might be thoughts from a pattern match
            thoughts = YAMLResponseParser.extract_thoughts_fallback(response)
            return JudgeResponse(thoughts=thoughts, score=score)
        return None
    
    @staticmethod
    def extract_score_only(response: str) -> Optional[float]:
        """Extract just the score value from the response."""
        # Try to find a score: X.X pattern
        score_pattern = r'score:\s*([0-9]*\.?[0-9]+)'
        score_match = re.search(score_pattern, response, re.IGNORECASE)
        
        if score_match:
            try:
                return float(score_match.group(1))
            except (ValueError, TypeError):
                pass
        return None
    
    @staticmethod
    def extract_thoughts_fallback(response: str) -> str:
        """Extract thoughts text as best effort when YAML parsing fails."""
        # Try to extract thoughts content
        thoughts_pattern = r'thoughts:\s*(?:"|\')?([^"\']*(?:"[^"]*"[^"\']*)*(?:"[^"]*")?[^"\']*)(?:"|\')?'
        thoughts_match = re.search(thoughts_pattern, response, re.IGNORECASE | re.DOTALL)
        
        if thoughts_match:
            return thoughts_match.group(1).strip()
        return ""

