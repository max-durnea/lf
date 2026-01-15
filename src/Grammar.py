from .ParseTree import ParseTree

EPSILON = ""

class Grammar:
    @classmethod
    def fromFile(cls, file_name: str):
        """Load grammar from file in format: lhs: rhs1 rhs2|alternative"""
        with open(file_name, 'r') as f:
            V = set()  # all symbols (terminals + non-terminals)
            R = set()  # production rules
            S = None   # start symbol (first rule's left side)
            
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue

                # split at colon: left side is non-terminal, right side is production
                lhs, rhs = line.split(":", 1)
                non_terminal = lhs.strip()
                V.add(non_terminal)
                
                # the first non-terminal we see becomes the start symbol
                if not S:
                    S = non_terminal

                # handle alternatives separated by | (e.g., "A: B C|D E" means two rules)
                alternatives = rhs.split("|")
                for alt in alternatives:
                    alt = alt.strip()
                    symbols = alt.split()  # split by whitespace to get individual symbols
                    
                    # binary rule: A -> B C (exactly two symbols on right side)
                    if len(symbols) == 2:
                        symbol1, symbol2 = symbols
                        V.add(symbol1)
                        V.add(symbol2)
                        R.add((non_terminal, symbol1, symbol2))
                    
                    # unit or terminal rule: A -> B (exactly one symbol on right side)
                    elif len(symbols) == 1:
                        symbol = symbols[0]
                        if symbol == EPSILON:
                            R.add((non_terminal, EPSILON, None))
                        else:
                            V.add(symbol)
                            R.add((non_terminal, symbol, None))
                    
                    # epsilon production: A -> ε (empty right side)
                    #elif len(symbols) == 0 and alt == EPSILON:
                    #    R.add((non_terminal, EPSILON, None))

        return cls(V, R, S)

    def __init__(self, V: set[str], R: set[tuple[str, str, str|None]], S: str):
        self.V = V  # vocabulary (all symbols)
        self.R = R  # rules: (A, B, C) means A -> B C, (A, B, None) means A -> B
        self.S = S  # start symbol

    def cykParse(self, tokens: list[tuple[str, str]]):
        """
        cyk algorithm: bottom-up parsing for cnf grammars
        builds parse tree by combining smaller substrings into larger ones
        """
        n = len(tokens)
        
        # create dp table where table[i][j] is a dictionary {non_terminal: ParseTree}
        # table[i][j] represents all non-terminals that can derive substring from position i to j
        # using 1-indexed positions, so table[1][n] represents the entire input
        table = [[dict() for _ in range(n + 1)] for _ in range(n + 1)]

        # special case: if input is empty, check if grammar has S -> ε rule
        if n == 0:
            for (A, B, C) in self.R:
                if A == self.S and B == EPSILON and C is None:
                    return ParseTree(self.S)
            return None

        # step 1: base case - fill diagonal of table for single tokens (substrings of length 1)
        # each single token can be derived by itself and possibly by rules like A -> TOKEN
        for i in range(1, n + 1):
            token_type, lexeme = tokens[i - 1]  # get token at position i (0-indexed in list)
            
            # first, add the token itself to the table so it can be referenced
            table[i][i][token_type] = ParseTree(token_type, token=(token_type, lexeme))
            
            # second, check for terminal productions: rules like "A -> TOKEN"
            for (A, B, C) in self.R:
                # terminal production: C is None and B matches our token type
                if C is None and B == token_type:
                    if A not in table[i][i]:
                        tree = ParseTree(A)
                        tree.add_children(ParseTree(token_type, token=(token_type, lexeme)))
                        table[i][i][A] = tree

        # step 2: recursive case - fill table for longer substrings (length 2, 3, ..., n)
        # for each substring, try all ways to split it and combine using binary rules
        for length in range(2, n + 1):  # process substrings of increasing length
            for start in range(1, n - length + 2):  # try all starting positions
                end = start + length - 1  # calculate ending position for this substring
                
                # try every way to split substring [start, end] into two parts
                # split k means: left part is [start, k], right part is [k+1, end]
                for split in range(start, end):
                    
                    # try all binary rules A -> B C to see if they apply
                    for (A, B, C) in self.R:
                        # only consider binary rules (C is not None)
                        if C is not None:
                            # get what can derive the left and right parts
                            left_part = table[start][split]
                            right_part = table[split + 1][end]
                            
                            # core cyk logic: if B can derive left part AND C can derive right part,
                            # then A can derive the whole substring [start, end]
                            if B in left_part and C in right_part:
                                # only add A if not already in the table for this substring
                                if A not in table[start][end]:
                                    # create parse tree: A has two children (B's tree and C's tree)
                                    tree = ParseTree(A)
                                    tree.add_children(left_part[B])
                                    tree.add_children(right_part[C])
                                    table[start][end][A] = tree

        # step 3: check if parsing succeeded
        # if start symbol is in table[1][n], it can derive the entire input
        if self.S in table[1][n]:
            return table[1][n][self.S]
        
        # if start symbol not in table[1][n], input doesn't match grammar
        return None