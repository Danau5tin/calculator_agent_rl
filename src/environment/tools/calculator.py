from dataclasses import dataclass
from typing import Any, List, Literal, Union, Dict, Callable


@dataclass
class Expression:
    """Represents a mathematical expression or sub-expression."""

    operation: Literal[
        "add",
        "subtract",
        "multiply",
        "divide",
    ]
    operands: List[Union["Expression", float, int]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Expression':
        """Parse a dictionary to create an Expression object."""
        
        # Extract the operation and ensure it's valid
        operation = data.get("operation")
        if operation not in {
            "add", "subtract", "multiply", "divide",
        }:
            raise ValueError(f"Invalid operation: {operation}")

        # Extract operands, which can be nested expressions or numbers
        operands_data = data.get("operands")
        if not isinstance(operands_data, list):
            raise ValueError("Operands must be a list.")

        operands = []
        for operand in operands_data:
            if isinstance(operand, (int, float)):
                operands.append(operand)
            elif isinstance(operand, dict):
                # Recursively parse nested expressions
                operands.append(cls.from_dict(operand))
            else:
                raise ValueError("Operands must be numbers or dictionaries representing expressions.")

        return cls(operation=operation, operands=operands)




def _add(operands: List[float]) -> float:
    """Adds all operands. Returns 0 for empty list."""
    return sum(operands)

def _subtract(operands: List[float]) -> float:
    """Subtracts subsequent operands from the first.
       Returns 0 for empty list. Returns the operand if only one."""
    if not operands:
        return 0.0
    result = operands[0]
    for operand in operands[1:]:
        result -= operand
    return result

def _multiply(operands: List[float]) -> float:
    """Multiplies all operands. Returns 1 for empty list (identity)."""
    result = 1.0
    for operand in operands:
        result *= operand
    return result

def _divide(operands: List[float]) -> float:
    """Divides the first operand by subsequent operands.
       Returns the operand if only one. Raises error for empty list."""
    if not operands:
        raise ValueError("Division requires at least one operand")
    if len(operands) == 1:
        return operands[0]

    result = operands[0]
    for operand in operands[1:]:
        if operand == 0.0:
            raise ZeroDivisionError("Division by zero")
        result /= operand
    return result

_operations: Dict[str, Callable[[List[float]], float]] = {
    "add": _add,
    "subtract": _subtract,
    "multiply": _multiply,
    "divide": _divide,
}

def calculate(expression: Union[Expression, float, int]) -> float:
    """
    Calculates the result of the given expression recursively.

    Args:
        expression: An Expression object, float, or int to evaluate.

    Returns:
        The calculated result as a float.

    Raises:
        ValueError: If an unsupported operation is encountered or if
                    an operation receives an invalid number of operands.
        ZeroDivisionError: If division by zero occurs.
        TypeError: If the input is not an Expression, float, or int.
    """
    if isinstance(expression, (int, float)):
        return float(expression)

    if isinstance(expression, Expression):
        evaluated_operands: List[float] = [calculate(operand) for operand in expression.operands]

        operation_func = _operations.get(expression.operation)
        if operation_func is None:
            raise ValueError(f"Unsupported operation: {expression.operation}")

        return operation_func(evaluated_operands)

    raise TypeError(f"Unsupported expression type: {type(expression)}")
