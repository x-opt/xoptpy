from pydantic import BaseModel
from typing import Dict, Any
import sys
import os
# Add the xopt package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
import xopt
from xopt.models import Module
import math


@xopt.module
def calculator() -> Module:
    module = Module(
        name="xopt/calculator",
        version="0.1.0",
        description="A simple calculator module that evaluates mathematical expressions.",
        long_description="This module evaluates mathematical expressions using Python syntax. Use the pow function for any powers. Available functions: sin, cos, tan, exp, log, sqrt, pow, abs, floor, ceil, pi, e. Input the mathematical expression directly without quotes. Example: sqrt(2 * pi) or sin(3.14159).",
    )

    @xopt.step
    def calculate(step_input) -> float:
        # Handle both dict and string inputs for backwards compatibility
        if isinstance(step_input, dict):
            input_expr = step_input.get("input", "")
        else:
            input_expr = str(step_input)
        if 'import' in input_expr:
            raise ValueError("Import statements are not allowed")
        
        allowed_chars = set('0123456789.+-*/() ')
        allowed_funcs = {
            'sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 
            'pow', 'abs', 'floor', 'ceil', 'pi', 'e'
        }
        
        # Create safe namespace for eval
        safe_dict = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'exp': math.exp, 'log': math.log, 'sqrt': math.sqrt,
            'pow': pow, 'abs': abs, 'floor': math.floor, 'ceil': math.ceil,
            'pi': math.pi, 'e': math.e
        }
        
        try:
            result = eval(input_expr, {"__builtins__": {}}, safe_dict)
            return float(result)
        except Exception as e:
            raise ValueError(f"Invalid calculation: {input_expr}") from e
        
    module.register(
        name="calculate", 
        step=calculate, 
        input_type=dict, 
        output_type=float)
    
    module.set_start_step("calculate")

    return module


# Register the module
xopt.register(calculator)