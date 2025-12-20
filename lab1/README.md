# Python Calculator Project

A simple calculator module with comprehensive unit tests, perfect for demonstrating CI/CD with GitHub Actions.

## Features

The calculator supports the following operations:
- Addition
- Subtraction
- Multiplication
- Division (with zero-division protection)
- Power/Exponentiation
- Square Root (with negative number protection)

## Project Structure

```
lab1/
├── calculator.py           # Main calculator module
├── test_calculator.py      # Unit tests
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Running the Calculator

To run the calculator demo:

```bash
python calculator.py
```

## Running Tests

### Using unittest (built-in)

```bash
python -m unittest test_calculator.py
```

Or with verbose output:

```bash
python -m unittest test_calculator.py -v
```

### Using pytest (optional)

If you have pytest installed:

```bash
pytest test_calculator.py
```

With coverage report:

```bash
pytest test_calculator.py --cov=calculator --cov-report=term-missing
```

## Installing Dependencies

```bash
pip install -r requirements.txt
```

Note: The calculator itself has no external dependencies. The `requirements.txt` includes optional testing tools (pytest, pytest-cov).

## GitHub Actions CI/CD

This project is ready for GitHub Actions integration. You can create a workflow that:
1. Runs tests on every push/pull request
2. Checks code coverage
3. Tests against multiple Python versions
4. Reports test results

Example workflow features:
- ✅ Automated testing
- ✅ Multi-version Python support (3.8, 3.9, 3.10, 3.11)
- ✅ Code coverage reporting
- ✅ Linting with pylint or flake8
- ✅ Format checking with black

## Test Coverage

The test suite includes:
- 8 test methods
- 25+ individual assertions
- Edge case testing (zero, negative numbers, division by zero)
- Exception handling validation

## Example Usage

```python
from calculator import Calculator

calc = Calculator()

# Basic operations
result = calc.add(5, 3)        # 8
result = calc.subtract(10, 4)  # 6
result = calc.multiply(6, 7)   # 42
result = calc.divide(20, 4)    # 5.0

# Advanced operations
result = calc.power(2, 8)      # 256
result = calc.square_root(16)  # 4.0

# Error handling
try:
    calc.divide(10, 0)  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")
```

## License

This is a demo project for learning purposes.
