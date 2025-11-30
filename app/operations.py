# app/operations.py
import logging
log = logging.getLogger(__name__)

def add(a: float, b: float) -> float:
    res = a + b
    log.debug("add(%s, %s)=%s", a, b, res)
    return res

def sub(a: float, b: float) -> float:
    res = a - b
    log.debug("sub(%s, %s)=%s", a, b, res)
    return res

def mul(a: float, b: float) -> float:
    res = a * b
    log.debug("mul(%s, %s)=%s", a, b, res)
    return res

def div(a: float, b: float) -> float:
    if b == 0:
        log.error("Attempted division by zero: div(%s, %s)", a, b)
        raise ZeroDivisionError("Division by zero")
    res = a / b
    log.debug("div(%s, %s)=%s", a, b, res)
    return res


def compute(a: float, b: float, operation_type: str) -> float:
    """
    Compute the result of an operation.
    
    Args:
        a: First operand
        b: Second operand
        operation_type: Type of operation (Add, Sub, Multiply, Divide)
        
    Returns:
        Result of the computation
        
    Raises:
        ValueError: If operation_type is invalid
        ZeroDivisionError: If dividing by zero
    """
    operation_map = {
        "Add": add,
        "Sub": sub,
        "Multiply": mul,
        "Divide": div
    }
    
    operation_func = operation_map.get(operation_type)
    if operation_func is None:
        raise ValueError(f"Invalid operation type: {operation_type}")
    
    return operation_func(a, b)
