from .Regex import Regex, parse_regex
from .NFA import NFA, EPSILON

class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        """
        initialize lexer with token specifications
        spec: list of (token_name, regex_string) pairs like [("NUMBER", "[0-9]+"), ("PLUS", "\\+")]
        """
        self.spec = spec
        
        # convert each regex pattern to a dfa (deterministic finite automaton)
        # dfas are state machines that can efficiently check if text matches a pattern
        self.token_dfas = []
        for token_name, regex_string in spec:
            # three-step conversion: regex string -> regex object -> nfa -> dfa
            regex = parse_regex(regex_string)  # parse the regex string
            nfa = regex.thompson()  # thompson's construction: regex -> nfa
            dfa = nfa.subset_construction()  # subset construction: nfa -> dfa
            self.token_dfas.append((token_name, dfa))
    
    def lex(self, word: str) -> list[tuple[str, str]]:
        """
        tokenize input string using longest match principle (maximal munch)
        returns list of (token_name, lexeme) pairs or error message in format [("", "error...")]
        """
        tokens = []
        position = 0
        input_length = len(word)
        
        # main loop: process input character by character until we reach the end
        while position < input_length:
            
            # step 1: try all token patterns at current position to find longest match
            # we track: end position of match, which token matched, and its index for tie-breaking
            longest_match_end = position  # how far the best match extends
            longest_match_token = None  # which token type matched best
            longest_match_index = None  # index in spec (for tie-breaking)

            # try each token's dfa to see which one matches longest
            for token_index, (token_name, dfa) in enumerate(self.token_dfas):
                current_state = dfa.q0  # start at dfa's initial state
                current_pos = position  # start at current input position
                last_accepting_pos = None  # tracks last position where dfa was in accepting state
                
                # check if initial state is accepting (some patterns match empty string)
                if current_state in dfa.F:
                    last_accepting_pos = current_pos

                # follow dfa transitions as far as possible by reading characters
                while current_pos < input_length:
                    char = word[current_pos]
                    
                    # check if transition exists for this character from current state
                    # dfa.d is transition function: (state, character) -> next_state
                    if (current_state, char) not in dfa.d:
                        break  # no transition exists, dfa is stuck, stop here
                    
                    # transition exists, take it to move to next state
                    current_state = dfa.d[(current_state, char)]
                    current_pos += 1  # advance position in input
                    
                    # check if new state is accepting (dfa.F is set of accepting states)
                    if current_state in dfa.F:
                        last_accepting_pos = current_pos  # remember this as valid match point
                
                # update longest match if this token matched something
                if last_accepting_pos is not None:
                    # if this match is longer than current best, it wins
                    if last_accepting_pos > longest_match_end:
                        longest_match_end = last_accepting_pos
                        longest_match_token = token_name
                        longest_match_index = token_index
                    # if same length as current best, tie-break: prefer earlier in spec
                    elif last_accepting_pos == longest_match_end:
                        if longest_match_token is not None and token_index < longest_match_index:
                            longest_match_token = token_name
                            longest_match_index = token_index

            # step 2: check if any token matched
            # if nothing matched or we didn't advance, we have a lexical error
            if longest_match_token is None or longest_match_end == position:
                error_position = self._find_error_position(word, position, input_length)
                error_message = self._format_error_message(word, error_position, input_length)
                return [("", error_message)]  # return error in format [("", "error message")]

            # step 3: add matched token to result list
            lexeme = word[position:longest_match_end]  # extract matched text
            tokens.append((longest_match_token, lexeme))  # add (token_type, lexeme) pair
            position = longest_match_end  # jump to end of matched token and continue

        return tokens

    def _find_error_position(self, word: str, position: int, input_length: int) -> int:
        """
        find where lexical error occurred by seeing where dfas got stuck
        returns the earliest position where all dfas failed to continue
        """
        earliest_stuck_position = None

        # try each dfa to see how far it could go before getting stuck
        for token_name, dfa in self.token_dfas:
            current_state = dfa.q0
            current_pos = position

            # check if dfa can make at least one transition from current position
            if current_pos < input_length and (current_state, word[current_pos]) in dfa.d:
                # follow dfa as far as it can go (even if not accepting)
                while current_pos < input_length and (current_state, word[current_pos]) in dfa.d:
                    current_state = dfa.d[(current_state, word[current_pos])]
                    current_pos += 1
                
                # track the earliest position where any dfa got stuck
                if earliest_stuck_position is None or current_pos < earliest_stuck_position:
                    earliest_stuck_position = current_pos

        # if no dfa could start (no transitions from initial state), error is at current position
        if earliest_stuck_position is None:
            return position
        
        # if dfa consumed multiple characters before getting stuck,
        # report error at the previous character 
        if (earliest_stuck_position - position) > 1:
            return earliest_stuck_position - 1
        else:
            return earliest_stuck_position

    def _format_error_message(self, word: str, error_position: int, input_length: int) -> str:
        """
        format error message with line and column numbers
        format: "No viable alternative at character X, line Y" or "...at character EOF, line Y"
        """
        # count newlines before error position to get line number (0-indexed)
        line_number = word[:error_position].count('\n')
        
        # special case: error at end of file
        if error_position >= input_length:
            return f"No viable alternative at character EOF, line {line_number}"
        
        # calculate column number: position within current line
        # find last newline before error, column is distance from there
        last_newline_pos = word.rfind('\n', 0, error_position)
        column_number = error_position - (last_newline_pos + 1)
        
        return f"No viable alternative at character {column_number}, line {line_number}"