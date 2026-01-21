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
    ("SPACE", "\\ "),
    ("NEWLINE", "\n"),
    ("ABC", "a(b+)c"),
    ("AS", "a+"),
    ("BCS", "(bc)+"),
    ("DORC", "(d|c)+")
]

lexer = Lexer(spec)

input_str = "abcbcbcaabaad dccbca"
expected = [("", "No viable alternative at character 10, line 0")]

result = lexer.lex(input_str)
print(f"Input: {repr(input_str)}")
print(f"Expected: {expected}")
print(f"Got:      {result}")
print(f"Match: {result == expected}")