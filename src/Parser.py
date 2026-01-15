from .Lexer import Lexer
from .Grammar import Grammar

class Parser:
    """
    combines lexical analysis (lexer) and syntax analysis (grammar/cyk)
    pipeline: input text -> tokens -> parse tree
    """

    def __init__(self, lexer: Lexer, grammar: Grammar) -> None:
        """
        initialize parser with lexer and grammar components
        lexer: converts text into (token_type, lexeme) pairs
        grammar: cnf grammar for syntax analysis using cyk algorithm
        """
        # store lexer for tokenization phase
        self.lexer = lexer
        # store grammar for parsing phase
        self.grammar = grammar

    def parse(self, input_text: str):
        """
        parse input text and return parse tree as string or error message
        
        four-phase process:
        1. lexical analysis: convert text to tokens
        2. filter whitespace: remove space tokens that grammar doesn't use
        3. syntax analysis: use cyk to build parse tree from tokens
        4. return result: formatted tree or error message
        """
        
        # phase 1: lexical analysis
        # call lexer to tokenize input string into list of (token_type, lexeme) pairs
        tokens = self.lexer.lex(input_text)

        # check if lexer encountered an error during tokenization
        # lexer returns errors as a single-element list: [("", "error message")]
        # empty token type "" signals an error
        if tokens and tokens[0][0] == "":
            return tokens[0][1]  # return the error message string

        # phase 2: filter whitespace tokens
        # remove all space tokens because grammar rules don't include space as a terminal
        # list comprehension keeps only tokens where token_type is not "SPACE"
        filtered_tokens = [token for token in tokens if token[0] != "SPACE"]

        # phase 3: syntax analysis using cyk algorithm
        # grammar.cykParse() builds parse tree bottom-up from filtered tokens
        # returns ParseTree object if input matches grammar, None otherwise
        parse_tree = self.grammar.cykParse(filtered_tokens)

        # phase 4: return result based on whether parsing succeeded
        if parse_tree:
            # parsing succeeded: convert parse tree to formatted string
            return str(parse_tree)
        
        # parsing failed: input tokens don't match grammar rules
        return "Syntax Error"