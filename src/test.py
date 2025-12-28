import sys
import os
import importlib

try:
    from src.Lexer import Lexer
except Exception:
    # If running the script directly, ensure project root is on sys.path
    pkg_root = os.path.dirname(os.path.dirname(__file__))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    Lexer = importlib.import_module('src.Lexer').Lexer

spec = [
    ("SPACE", "( |\\n|\\t|\\r)+"),
    ("LAMBDA", "\\\\"),
    ("POINT", "\\."),
    ("LPAREN", "\\("),
    ("RPAREN", "\\)"),
    ("OP", "(\\+|\\-|\\*|/)"),
    ("VAR", "[a-z]"),
    ("NUMBER", "[0-9]+")
]

lexer = Lexer(spec)

# Test 1: Simple expression
result1 = lexer.lex("(a+b)")
print("Test 1 - (a+b):", result1)

# Test 2: Just the operator
result2 = lexer.lex("+")
print("Test 2 - +:", result2)

# Test 3: Step by step
result3 = lexer.lex("(")
print("Test 3 - (:", result3)

result4 = lexer.lex("a")
print("Test 4 - a:", result4)

result5 = lexer.lex("a+")
print("Test 5 - a+:", result5)