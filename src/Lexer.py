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
            if best_token is None or best_end == pos:
                # Determine the earliest position where a started DFA gets stuck.
                min_reach = None

                for tok_name, dfa in self.token_dfas:
                    cur = dfa.q0
                    i = pos

                    # Try to make at least one transition
                    if i < n and (cur, word[i]) in dfa.d:
                        # Follow the DFA as far as possible
                        while i < n and (cur, word[i]) in dfa.d:
                            cur = dfa.d[(cur, word[i])]
                            i += 1
                        if min_reach is None or i < min_reach:
                            min_reach = i

                # If no DFA could start, error is at current position
                # Otherwise, choose an error position derived from the earliest DFA stuck point.
                if min_reach is None:
                    error_pos = pos
                else:
                    # Prefer the earliest stuck index; in some edge cases report the previous
                    # character when the DFA consumed multiple chars but didn't accept.
                    if (min_reach - pos) > 1:
                        error_pos = min_reach - 1
                    else:
                        error_pos = min_reach

                line = count_lines(error_pos)

                if error_pos >= n:
                    return [("", f"No viable alternative at character EOF, line {line}")]
                else:
                    # Compute column (character index within the line)
                    last_nl = word.rfind('\n', 0, error_pos)
                    col = error_pos - (last_nl + 1)
                    return [("", f"No viable alternative at character {col}, line {line}")]

            lexeme = word[pos:best_end]
            result.append((best_token, lexeme))
            pos = best_end

        return result