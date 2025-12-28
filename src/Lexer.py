from .Regex import Regex, parse_regex
from .NFA import NFA, EPSILON

class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        self.spec = spec
        AFNs = []
        for token, regex_str in spec:
            regex = parse_regex(regex_str)
            afn = regex.thompson()
            AFNs.append((token, afn))
        self.AFNs = AFNs
        
        self.token_dfas = []
        for token, afn in AFNs:
            dfa = afn.subset_construction()
            self.token_dfas.append((token, dfa))
    
    def lex(self, word: str) -> list[tuple[str, str]]:
        result = []
        pos = 0
        n = len(word)
        
        def count_lines(up_to_pos):
            # Calculate lines (0-indexed)
            return word[:up_to_pos].count('\n')

        while pos < n:
            best_idx = None
            best_token = None
            best_end = pos

            # Find longest matching token
            for idx, (tok_name, dfa) in enumerate(self.token_dfas):
                cur = dfa.q0
                i = pos
                last_accept = None
                
                # Check for epsilon acceptance (length 0)
                if cur in dfa.F:
                    last_accept = i

                while i < n and (cur, word[i]) in dfa.d:
                    cur = dfa.d[(cur, word[i])]
                    i += 1
                    if cur in dfa.F:
                        last_accept = i
                
                if last_accept is not None and last_accept > best_end:
                    best_end = last_accept
                    best_token = tok_name
                    best_idx = idx
                elif last_accept is not None and last_accept == best_end and best_token is not None:
                    # Tie-break: prefer earlier definition
                    if idx < best_idx:
                        best_token = tok_name
                        best_idx = idx
            # Right before "if best_token is None or best_end == pos:"
            if best_token is None or best_end == pos:
                print(f"DEBUG: Failed at pos={pos}, char='{word[pos] if pos < n else 'EOF'}'")
                print(f"DEBUG: best_token={best_token}, best_end={best_end}")
                # Show what each DFA could match
                for idx, (tok_name, dfa) in enumerate(self.token_dfas):
                    print(f"  {tok_name}: checking from pos {pos}")
            # Error Handling
            if best_token is None or best_end == pos:
                max_reach = pos
                # Check all DFAs to see how far we COULD have gone
                for _, dfa in self.token_dfas:
                    i = pos
                    cur = dfa.q0
                    while i < n and (cur, word[i]) in dfa.d:
                        cur = dfa.d[(cur, word[i])]
                        i += 1
                    if i > max_reach:
                        max_reach = i
                
                line = count_lines(max_reach)
                
                if max_reach == n and pos < n:
                     return [("", f"No viable alternative at character EOF, line {line}")]
                else:
                     return [("", f"No viable alternative at character {max_reach}, line {line}")]

            lexeme = word[pos:best_end]
            result.append((best_token, lexeme))
            pos = best_end

        return result