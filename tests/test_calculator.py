import unittest

from src.environment.tools.calculator import Expression, calculate

class TestCalculator(unittest.TestCase):

    def test_simple_number(self):
        self.assertEqual(calculate(5), 5.0)
        self.assertEqual(calculate(10.5), 10.5)
        self.assertEqual(calculate(0), 0.0)
        self.assertEqual(calculate(-3.14), -3.14)

    def test_simple_operations(self):
        expr_add = Expression(operation="add", operands=[5, 3, 2])
        self.assertEqual(calculate(expr_add), 10.0)

        expr_subtract = Expression(operation="subtract", operands=[10, 3, 1])
        self.assertEqual(calculate(expr_subtract), 6.0)

        expr_multiply = Expression(operation="multiply", operands=[2, 3, 4])
        self.assertEqual(calculate(expr_multiply), 24.0)

        expr_divide = Expression(operation="divide", operands=[20, 2, 5])
        self.assertAlmostEqual(calculate(expr_divide), 2.0)

    def test_nested_expressions(self):
        # (5 + 3) * (10 / 2) = 8 * 5 = 40
        expr1 = Expression(operation="add", operands=[5, 3])
        expr2 = Expression(operation="divide", operands=[10, 2])
        main_expr = Expression(operation="multiply", operands=[expr1, expr2])
        self.assertAlmostEqual(calculate(main_expr), 40.0)

        # (100 - (4 * (5 + 2))) / 2 = (100 - (4 * 7)) / 2 = (100 - 28) / 2 = 72 / 2 = 36
        complex_expr = Expression(
            operation="divide",
            operands=[
                Expression(
                    operation="subtract",
                    operands=[
                        100,
                        Expression(
                            operation="multiply",
                            operands=[
                                4,
                                Expression(operation="add", operands=[5, 2])
                            ]
                        )
                    ]
                ),
                2
            ]
        )
        self.assertAlmostEqual(calculate(complex_expr), 36.0)

    def test_mixed_operands(self):
        # 10 + (8 / 2) - 1 = 10 + 4 - 1 = 13
        expr = Expression(
            operation="subtract",
            operands=[
                Expression(operation="add", operands=[10, Expression(operation="divide", operands=[8, 2])]),
                1
            ]
        )
        self.assertAlmostEqual(calculate(expr), 13.0)

    def test_edge_cases_empty_operands(self):
        self.assertEqual(calculate(Expression(operation="add", operands=[])), 0.0)
        self.assertEqual(calculate(Expression(operation="subtract", operands=[])), 0.0)
        self.assertEqual(calculate(Expression(operation="multiply", operands=[])), 1.0)
        # Division with empty operands should raise ValueError
        with self.assertRaisesRegex(ValueError, "Division requires at least one operand"):
            calculate(Expression(operation="divide", operands=[]))

    def test_edge_cases_single_operand(self):
        self.assertEqual(calculate(Expression(operation="add", operands=[7])), 7.0)
        self.assertEqual(calculate(Expression(operation="subtract", operands=[7])), 7.0)
        self.assertEqual(calculate(Expression(operation="multiply", operands=[7])), 7.0)
        self.assertEqual(calculate(Expression(operation="divide", operands=[7])), 7.0)

    def test_error_division_by_zero(self):
        expr_zero_direct = Expression(operation="divide", operands=[10, 0])
        with self.assertRaisesRegex(ZeroDivisionError, "Division by zero"):
            calculate(expr_zero_direct)

        # Nested division by zero: 10 / (5 - 5)
        expr_zero_nested = Expression(
            operation="divide",
            operands=[10, Expression(operation="subtract", operands=[5, 5])]
        )
        with self.assertRaisesRegex(ZeroDivisionError, "Division by zero"):
            calculate(expr_zero_nested)

    def test_error_unsupported_operation(self):
        with self.assertRaises(ValueError):
            expr_bad_op = Expression(operation="modulo", operands=[10, 3])
            calculate(expr_bad_op)

    def test_error_invalid_input_type(self):
        with self.assertRaisesRegex(TypeError, "Unsupported expression type: <class 'str'>"):
            calculate("not an expression")
        with self.assertRaisesRegex(TypeError, "Unsupported expression type: <class 'list'>"):
            calculate([1, 2, 3])

if __name__ == "__main__":
    unittest.main()
