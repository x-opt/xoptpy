# Calculator Module

A simple calculator module for xopt that evaluates mathematical expressions safely.

## Features

- Safe evaluation of mathematical expressions
- Support for basic math functions (sin, cos, tan, log, sqrt, etc.)
- Built-in constants (pi, e)
- Input validation to prevent code injection

## Usage

```python
import xopt

# Start the calculator module
calc = xopt.start("xopt/calculator@0.1.0")

# Use it for calculations
result = calc.call("sqrt(2 * pi)")
print(result.content)
```