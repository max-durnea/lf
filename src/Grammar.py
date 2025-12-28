from .ParseTree import ParseTree

EPSILON = ""

class Grammar:
    @classmethod
    def fromFile(cls, file_name: str):
        with open(file_name, 'r') as f:
            V = set()
            R = set()
            S = None
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue

                # Robust split: Find first colon, ignore surrounding whitespace
                lhs, rhs = line.split(":", 1)
                v = lhs.strip()
                V.add(v)
                if not S:
                    S = v

                # Handle alternatives
                alternatives = rhs.split("|")
                for alt in alternatives:
                    alt = alt.strip()
                    # Robust split for tokens (handles spaces, tabs, etc.)
                    parts = alt.split()
                    
                    if len(parts) == 2:
                        n1, n2 = parts
                        V.add(n1)
                        V.add(n2)
                        R.add((v, n1, n2))
                    elif len(parts) == 1:
                        val = parts[0]
                        if val == EPSILON:
                            R.add((v, EPSILON, None))
                        else:
                            V.add(val)
                            R.add((v, val, None))
                    elif len(parts) == 0 and alt == EPSILON:
                         R.add((v, EPSILON, None))

        return cls(V, R, S)

    def __init__(self, V: set[str], R: set[tuple[str, str, str|None]], S: str):
        self.V = V
        self.R = R
        self.S = S

    def cykParse(self, w: list[tuple[str, str]]):
        n = len(w)
        # DP[i][j] = dict { non-terminal : ParseTree }
        # Indices are 1-based to match standard CYK notation
        DP = [[dict() for _ in range(n + 1)] for _ in range(n + 1)]

        if n == 0:
            for (A, B, C) in self.R:
                if A == self.S and B == EPSILON and C is None:
                    return ParseTree(self.S)
            return None

        # Helper function to apply unit productions
        def apply_unit_productions(cell):
            """Apply all unit productions (A -> B) until no new non-terminals added"""
            changed = True
            while changed:
                changed = False
                for (A, B, C) in self.R:
                    # Unit production: A -> B (where B is a non-terminal)
                    if C is None and B != EPSILON and B in cell and A not in cell:
                        node = ParseTree(A)
                        node.add_children(cell[B])
                        cell[A] = node
                        changed = True

        # Base case: Substrings of length 1 (Terminals)
        for i in range(1, n + 1):
            token_type, lexeme = w[i-1]
            
            # 1. Add the actual token as a leaf
            DP[i][i][token_type] = ParseTree(token_type, token=(token_type, lexeme))
            
            # 2. Add Unit Productions for terminals (A -> token_type)
            for (A, B, C) in self.R:
                if C is None and B == token_type and A not in DP[i][i]:
                    node = ParseTree(A)
                    node.add_children(ParseTree(token_type, token=(token_type, lexeme)))
                    DP[i][i][A] = node
            
            # 3. Apply unit productions (A -> B where B is non-terminal)
            apply_unit_productions(DP[i][i])

        # Recursive Step: Substrings of length 2 to n
        for l in range(2, n + 1):  # Length
            for i in range(1, n - l + 2):  # Start index
                j = i + l - 1  # End index
                for k in range(i, j):  # Split position
                    # Try all binary rules A -> B C
                    for (A, B, C) in self.R:
                        if C is not None:
                            if B in DP[i][k] and C in DP[k+1][j] and A not in DP[i][j]:
                                node = ParseTree(A)
                                node.add_children(DP[i][k][B])
                                node.add_children(DP[k+1][j][C])
                                DP[i][j][A] = node
                
                # Apply unit productions after all binary rules for this cell
                apply_unit_productions(DP[i][j])

        # Return Result
        if self.S in DP[1][n]:
            return DP[1][n][self.S]
        
        return None