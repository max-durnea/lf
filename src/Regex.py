
from typing import Any, List

from .NFA import NFA

EPSILON = ''

stare = 0

class Regex:
    
    def thompson(self) -> NFA[int]:
        pass
# kleene star operator class (zero or more repetitions)
class Kleene(Regex):
    # initialize with the inner regex to apply kleene star to
    def __init__(self, reg:Regex):
        # store the inner regex expression
        self.reg = reg
    # construct nfa for kleene star using thompson's construction
    def thompson(self) -> NFA[int]:
        # access global state counter
        global stare
        # create new initial state
        q0 = stare
        # increment state counter
        stare+=1
        # recursively build nfa for inner expression
        n = self.reg.thompson()
        # copy transition function from inner nfa
        d = n.d.copy()
        # create new final state
        f = stare
        # increment state counter
        stare+=1
        # add epsilon transition from new start to inner start
        d[(q0, EPSILON)] = {n.q0}
        # add epsilon transition from new start to new final (allows zero repetitions)
        d[(q0, EPSILON)].update({f})
        # for each final state of inner nfa
        for final in n.F:
            # if no epsilon transitions exist from this final state
            if (final,EPSILON) not in d:   
                # add epsilon transitions back to inner start and to new final
                d[(final,EPSILON)]={n.q0,f}
            # if epsilon transitions already exist
            else:
                # add to existing epsilon transitions back to start and to final
                d[(final,EPSILON)].update({n.q0,f})
        # combine all states: inner states plus new start and final
        K=n.K | {q0,f}
        # return nfa with same alphabet, combined states, new start, modified transitions, new final
        return NFA(n.S,K,q0,d,{f})
# optional operator class (zero or one occurrence)
class Optional(Regex):
    # initialize with the inner regex to make optional
    def __init__(self, reg:Regex):
        # store the inner regex expression
        self.reg = reg
    # construct nfa for optional using thompson's construction
    def thompson(self) -> NFA[int]:
        # access global state counter
        global stare
        # create new initial state
        q0 = stare
        # increment state counter
        stare+=1
        # recursively build nfa for inner expression
        n = self.reg.thompson()
        # copy transition function from inner nfa
        d = n.d.copy()
        # create new final state
        f = stare
        # increment state counter
        stare+=1
        # add epsilon transitions from new start to both inner start and new final (allows skipping)
        d[(q0, EPSILON)] = {n.q0, f} 
        # for each final state of inner nfa
        for final in n.F:
            # if no epsilon transitions exist from this final state
            if (final,EPSILON) not in d:   
                # add epsilon transition to new final
                d[(final,EPSILON)]={f}
            # if epsilon transitions already exist
            else:
                # add to existing epsilon transitions to new final
                d[(final,EPSILON)].update({f})
        # combine all states: inner states plus new start and final
        K=n.K | {q0,f}
        # return nfa with same alphabet, combined states, new start, modified transitions, new final
        return NFA(n.S,K,q0,d,{f})
# plus operator class (one or more repetitions)
class Plus(Regex):
    # initialize with the inner regex to apply plus to
    def __init__(self, reg:Regex):
        # store the inner regex expression
        self.reg = reg
    # construct nfa for plus using thompson's construction
    def thompson(self) -> NFA[int]:
        # access global state counter
        global stare
        # create new initial state
        q0 = stare
        # increment state counter
        stare+=1
        # recursively build nfa for inner expression
        n = self.reg.thompson()
        # copy transition function from inner nfa
        d = n.d.copy()
        # create new final state
        f = stare
        # increment state counter
        stare+=1
        # add epsilon transition from new start to inner start (must match at least once)
        d[(q0, EPSILON)] = {n.q0}
        # for each final state of inner nfa
        for final in n.F:
            # if no epsilon transitions exist from this final state
            if (final,EPSILON) not in d:   
                # add epsilon transitions back to inner start and to new final (allows repetition)
                d[(final,EPSILON)]={n.q0,f}
            # if epsilon transitions already exist
            else:
                # add to existing epsilon transitions back to start and to final
                d[(final,EPSILON)].update({n.q0,f})
        # combine all states: inner states plus new start and final
        K=n.K | {q0,f}
        # return nfa with same alphabet, combined states, new start, modified transitions, new final
        return NFA(n.S,K,q0,d,{f})
# concatenation operator class (matches left then right)
class Concat(Regex):
    # initialize with left and right regex expressions to concatenate
    def __init__(self, left:Regex,right:Regex):
        # store left regex expression
        self.left = left
        # store right regex expression
        self.right = right
    # construct nfa for concatenation using thompson's construction
    def thompson(self) -> NFA[int]:
        # recursively build nfa for left expression
        nl = self.left.thompson()
        # recursively build nfa for right expression
        nr = self.right.thompson()
        # copy transition function from left nfa
        delta = nl.d.copy()
        # add all transitions from right nfa to combined transition function
        for k,v in nr.d.items():
            delta[k]=v
        # connect left and right nfas by adding epsilon transitions from left finals to right start
        for f in nl.F:
            # if epsilon transitions already exist from this left final state
            if (f, EPSILON) in delta:
                # add right start to existing epsilon transitions
                delta[(f, EPSILON)].add(nr.q0)
            # if no epsilon transitions exist
            else:
                # create new epsilon transition to right start
                delta[(f, EPSILON)] = {nr.q0}
        # combine all states from both nfas
        K = nl.K | nr.K
        # combine alphabets from both nfas
        S = nl.S | nr.S
        # start state is the left nfa's start
        start = nl.q0
        # final states are the right nfa's finals
        end = nr.F
        # return nfa with combined alphabet, states, left start, merged transitions, right finals
        return NFA(S,K,start,delta,end)

# union operator class (matches left or right)
class Union(Regex):
    # initialize with left and right regex expressions to union
    def __init__(self, left:Regex, right:Regex):
        # store left regex expression
        self.left = left
        # store right regex expression
        self.right = right
    # construct nfa for union using thompson's construction
    def thompson(self) -> NFA[int]:
        # access global state counter
        global stare
        # create new initial state
        q0=stare
        # increment state counter
        stare+=1
        # recursively build nfa for left expression
        nl = self.left.thompson()
        # recursively build nfa for right expression
        nr = self.right.thompson()
        # copy transition function from left nfa
        d = nl.d.copy()
        # if epsilon transitions already exist from new start
        if (q0,EPSILON) in d:
            # add epsilon transitions to both left and right starts
            d[(q0, EPSILON)].update({nl.q0, nr.q0})
        # if no epsilon transitions exist from new start
        else:
            # create epsilon transitions to both left and right starts
            d[(q0,EPSILON)]={nl.q0,nr.q0}
        # create new single final state
        F = {stare}
        # increment state counter
        stare+=1
        # connect all left final states to new final with epsilon transitions
        for f in nl.F:
            # if epsilon transitions already exist from this left final
            if (f, EPSILON) in d:
                # add new final to existing epsilon transitions
                d[(f, EPSILON)].update(F)
            # if no epsilon transitions exist
            else:
                # create epsilon transition to new final
                d[(f, EPSILON)] = F
        # connect all right final states to new final with epsilon transitions
        for f in nr.F:
            # if epsilon transitions already exist from this right final
            if (f, EPSILON) in d:
                # add new final to existing epsilon transitions
                d[(f, EPSILON)].update(F)
            # if no epsilon transitions exist
            else:
                # create epsilon transition to new final
                d[(f, EPSILON)] = F
        # merge all transitions from right nfa into combined transition function
        for k, v in nr.d.items():
            # if transition already exists in combined function
            if k in d:
                # add right nfa's target states to existing transition
                d[k].update(v)
            # if transition doesn't exist
            else:
                # copy transition from right nfa
                d[k] = v.copy()
        # combine alphabets from both nfas
        S = nl.S | nr.S
        # combine all states from both nfas plus new start and final
        K = nl.K | nr.K
        # return nfa with combined alphabet and states, new start, merged transitions, new final
        return NFA(S,K,q0,d,F)


# character class represents a single literal character in regex
class Character(Regex):
    # initialize with a character
    def __init__(self,c:str):
        # store the character
        self.c = c
    # construct nfa for single character using thompson's construction
    def thompson(self) -> NFA[int]:
        # access global state counter
        global stare
        # if character is not epsilon (actual character)
        if self.c != EPSILON:
            # alphabet contains just this character
            S = {self.c}
            # create start state
            start = stare
            # increment state counter
            stare+=1
            # create end state
            end = stare
            # increment state counter
            stare+=1
            # states are start and end
            K = {start,end}
            # initial state is start
            q0 = start
            # final state is end
            F = {end}
            # single transition from start to end on character c
            d = {(start, self.c):{end}}
            # return nfa for single character
            return NFA(S,K,q0,d,F)
        # if character is epsilon (empty string)
        else:
            # empty alphabet for epsilon
            S = set()
            # create single state
            start = stare
            # increment state counter
            stare+=1
            # only one state exists
            K = {start}
            # initial state
            q0 = start
            # same state is also final (accepts empty string)
            F = {start}
            # no transitions needed for epsilon
            d = {}
            # return nfa that accepts empty string
            return NFA(S,K,q0,d,F)

# main function to parse regex string into regex object tree
def parse_regex(s:str):
    # access global state counter
    global stare
    # reset state counter to 0 for new regex
    stare = 0
    # preprocess string to handle escape sequences and create token list
    processed = preprocess(s)
    # parse tokens starting with lowest precedence (union) from position 0
    expr, pos_final = parse_union(processed, 0)
    # return parsed regex tree
    return expr

# parse union operator (lowest precedence, right associative)
def parse_union(s:list, pos:int):
    # parse left operand using higher precedence function (concat)
    left, pos = parse_concat(s, pos)
    # check if current position has union operator and it's not escaped
    if pos < len(s) and s[pos][0] == '|' and not s[pos][1]:
        # skip past the union operator
        pos += 1
        # recursively parse right side to handle chained unions (a|b|c)
        right, pos = parse_union(s, pos)
        # create union node with left and right subtrees
        return Union(left, right), pos
    # no union operator found, return what concat parsed
    return left, pos
# parse concatenation (medium precedence, left associative, implicit operator)
def parse_concat(s:list, pos:int):
    # list to collect all consecutive terms to concatenate
    terms = []
    # keep parsing terms until we hit a delimiter (union, close paren, or end)
    while pos < len(s) and not (s[pos][0] in '|)' and not s[pos][1]):
        # parse each term using higher precedence function (postfix)
        term, pos = parse_postfix(s, pos)
        # add parsed term to list
        terms.append(term)
    # if no terms were parsed, return epsilon (empty string)
    if not terms:
        return Character(EPSILON), pos
    # start with first term
    result = terms[0]
    # left-associate all remaining terms: ((a.b).c).d
    for term in terms[1:]:
        result = Concat(result, term)
    # return left-associated concatenation tree
    return result, pos

# parse postfix operators (high precedence: star, plus, optional)
def parse_postfix(s:list, pos:int):
    # first parse the base element using highest precedence function
    base, pos = parse_base(s, pos)
    # keep applying postfix operators while they exist and aren't escaped
    while pos < len(s) and s[pos][0] in '*+?' and not s[pos][1]:
        # get the operator character
        op = s[pos][0]
        # skip past the operator
        pos += 1
        # apply kleene star (zero or more)
        if op == '*':
            base = Kleene(base)
        # apply plus (one or more)
        elif op == '+':
            base = Plus(base)
        # apply optional (zero or one)
        elif op == '?':
            base = Optional(base)
    # return base with all postfix operators applied
    return base, pos

# parse base elements (highest precedence: characters, parentheses, character ranges)
def parse_base(s:str, pos:int):
    # if reached end of input, return epsilon
    if pos >= len(s):
        return Character(EPSILON), pos
    # get current character and whether it's escaped (literal)
    char, is_literal = s[pos]
    # if opening parenthesis and not escaped
    if char == '(' and not is_literal:
        # skip past opening paren
        pos += 1
        # recursively parse inner expression starting from lowest precedence (union)
        inner, pos = parse_union(s, pos)
        # if closing paren exists and not escaped
        if pos < len(s) and s[pos][0] == ')' and not s[pos][1]:
            # skip past closing paren
            pos += 1
        # return parsed subexpression
        return inner, pos
    # if opening bracket and not escaped (character range like [a-z])
    if char == '[' and not is_literal:
        # skip past opening bracket
        pos += 1
        # get first character of range
        start_char = s[pos][0]
        # skip past start character
        pos += 1
        # if dash exists (indicates range)
        if pos < len(s) and s[pos][0] == '-':
            # skip past dash
            pos += 1
            # get end character of range
            end_char = s[pos][0]
            # skip past end character
            pos += 1
            # if closing bracket exists
            if pos < len(s) and s[pos][0] == ']':
                # skip past closing bracket
                pos += 1
                # generate list of all characters in range using ascii values
                chars = [chr(c) for c in range(ord(start_char), ord(end_char) + 1)]
                # start with first character
                result = Character(chars[0])
                # union all remaining characters (a|b|c|d...)
                for ch in chars[1:]:
                    result = Union(result, Character(ch))
                # return union of all characters in range
                return result, pos
    # if regular character (or escaped special character)
    # skip past current character
    pos += 1
    # return character node
    return Character(char), pos

# preprocess regex string to handle escape sequences and create token list
def preprocess(s:str):
    # list to store processed tokens as (character, is_literal) tuples
    processed = []
    # index to iterate through input string
    i = 0
    # process each character in input
    while i < len(s):
        # if backslash exists and there's a character after it (escape sequence)
        if i < len(s) - 1 and s[i] == '\\':
            # get the character being escaped
            next_char = s[i + 1]
            # if escaped open paren, treat as literal
            if next_char == '(':
                processed.append(('(', True))  
            # if escaped close paren, treat as literal
            elif next_char == ')':
                processed.append((')', True)) 
            # if escaped space, treat as literal
            elif next_char == ' ':
                processed.append((' ', True))  
            # if escaped backslash, treat as literal
            elif next_char == '\\':
                processed.append(('\\', True))  
            # for any other escaped character, treat as literal
            else:
                processed.append((next_char, True))  
            # skip both backslash and escaped character
            i += 2
        # if space, skip it (spaces are ignored in regex)
        elif s[i] == ' ':
            i += 1
        # regular character, not escaped
        else:
            # add character with is_literal=False (can be operator)
            processed.append((s[i], False))
            # move to next character
            i += 1
    # return list of processed tokens
    return processed
    