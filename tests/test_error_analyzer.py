import pytest
from jarvisx.capabilities.coding.error_analyzer import ErrorAnalyzer

def test_error_analyzer_traceback():
    analyzer = ErrorAnalyzer()
    sample_stderr = (
        'Traceback (most recent call last):\n'
        '  File "main.py", line 18, in calculate\n'
        '    return a / b\n'
        'ZeroDivisionError: division by zero\n'
    )

    ctx = analyzer.analyze_traceback(stderr_output=sample_stderr)

    assert ctx.exception_type == "ZeroDivisionError"
    assert "division by zero" in ctx.error_message
    assert ctx.failing_file == "main.py"
    assert ctx.line_number == 18
    assert ctx.function_name == "calculate"
    assert "Division by zero" in ctx.likely_root_cause

def test_error_analyzer_empty():
    analyzer = ErrorAnalyzer()
    ctx = analyzer.analyze_traceback(stderr_output="")
    assert ctx.exception_type == "UnknownError"
