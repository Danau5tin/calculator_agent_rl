import unittest

from src.rewards.verifiers.answer_verifier import is_correct_answer


class TestAnswerChecker(unittest.TestCase):
    
    def test_exact_match(self):
        """Test when the last number exactly matches the correct answer."""
        self.assertTrue(is_correct_answer(agent_answer="The result is 42", correct_answer="42"))
        self.assertTrue(is_correct_answer(agent_answer="Let me calculate: 10, 20, 30, 42", correct_answer="42"))
    
    def test_non_match(self):
        """Test when the last number doesn't match the correct answer."""
        self.assertFalse(is_correct_answer(agent_answer="The result is 42", correct_answer="43"))
        self.assertFalse(is_correct_answer(agent_answer="Let me calculate: 42, 43, 44", correct_answer="42"))
        self.assertFalse(is_correct_answer(agent_answer="The answer is 42.0", correct_answer="42.1"))
        
    
    def test_number_formats(self):
        """Test different number formats."""
        # Integer
        self.assertTrue(is_correct_answer(agent_answer="The answer is 42", correct_answer="42"))
        
        # Decimal
        self.assertTrue(is_correct_answer(agent_answer="The answer is 42.5", correct_answer="42.5"))
        
        # Leading decimal
        self.assertTrue(is_correct_answer(agent_answer="The answer is .5", correct_answer="0.5"))
        
        # Scientific notation
        self.assertTrue(is_correct_answer(agent_answer="The answer is 4.2e1", correct_answer="42"))
        self.assertTrue(is_correct_answer(agent_answer="The answer is 4.2E1", correct_answer="42"))
        
        # Negative numbers
        self.assertTrue(is_correct_answer(agent_answer="The answer is -42", correct_answer="-42"))
    
    def test_thousand_separators(self):
        """Test numbers with commas as thousand separators."""
        self.assertTrue(is_correct_answer(agent_answer="The answer is 1,000", correct_answer="1000"))
        self.assertTrue(is_correct_answer(agent_answer="The answer is 1,234,567", correct_answer="1234567"))
        self.assertTrue(is_correct_answer(agent_answer="The answer is -1,234.56", correct_answer="-1234.56"))
    
    def test_multiple_numbers(self):
        """Test responses with multiple numbers."""
        self.assertTrue(is_correct_answer(agent_answer="I tried 10, then 20, finally got 30", correct_answer="30"))
        self.assertTrue(is_correct_answer(agent_answer="First I calculated 42, but then I realized it was 43", correct_answer="43"))
        self.assertFalse(is_correct_answer(agent_answer="First I calculated 43, but then I realized it was 42", correct_answer="43"))
    
    def test_answer_format(self):
        """Test old 'Answer:' format still works but isn't required."""
        self.assertTrue(is_correct_answer(agent_answer="Answer: 42", correct_answer="42"))
        self.assertTrue(is_correct_answer(agent_answer="The final answer is: 42", correct_answer="42"))
        self.assertTrue(is_correct_answer(agent_answer="I think the answer: 42", correct_answer="42"))
    
    def test_edge_cases(self):
        """Test edge cases."""
        # No numbers
        self.assertFalse(is_correct_answer(agent_answer="I don't know the answer", correct_answer="42"))
        
        # Empty strings
        self.assertFalse(is_correct_answer(agent_answer="", correct_answer="42"))
        
        # Invalid answer format that should now work
        self.assertTrue(is_correct_answer(agent_answer="The answer comes to exactly 42 dollars.", correct_answer="42"))

    def test_tolerance(self):
        """Test the tolerance parameter."""
        # Within tolerance
        self.assertTrue(is_correct_answer(agent_answer="Approx 3.14", correct_answer="3.14159"))
        an = is_correct_answer(agent_answer="It's 100.01", correct_answer="100")
        self.assertTrue(an)
        self.assertTrue(is_correct_answer(agent_answer="It's 99.99", correct_answer="100"))
        self.assertTrue(is_correct_answer(agent_answer="Value: -5.55", correct_answer="-5.5"))
        self.assertTrue(is_correct_answer(agent_answer="Approx 3.1", correct_answer="3.14159"))
        self.assertTrue(is_correct_answer(agent_answer="It's 100.02", correct_answer="100"))

        # Outside tolerance
        self.assertFalse(is_correct_answer(agent_answer="It's 99.2", correct_answer="100"))
        self.assertFalse(is_correct_answer(agent_answer="Value: -5.65", correct_answer="-5.5"))

if __name__ == '__main__':
    unittest.main()