from .Lexer import Lexer
from .Grammar import Grammar

class Parser:
    def __init__(self, lexer: Lexer, grammar: Grammar) -> None:
        self.lexer = lexer
        self.grammar = grammar

    def parse(self, input: str):
        tokens = self.lexer.lex(input)

        # 1. Check for Lexer errors
        if tokens and tokens[0][0] == "":
            return tokens[0][1] # Return the error string

        # 2. Filter out SPACE tokens
        non_space_tokens = [tok for tok in tokens if tok[0] != "SPACE"]

        # 3. Parse the filtered tokens
        parse_tree = self.grammar.cykParse(non_space_tokens)

        # 4. Return the result
        if parse_tree:
            return str(parse_tree)
        
        return "Syntax Error"