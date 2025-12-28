from collections.abc import Callable
from dataclasses import dataclass
from itertools import product
from typing import TypeVar
from functools import reduce

STATE = TypeVar('STATE')

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]
    

    def accept(self, word: str) -> bool:
        # begin by setting final state to the starting state
        final_state = self.q0
        # while word was not processed
        while(word):
            # extract character and rest of the word
            a, word = word[0], word[1:]
            # if there is no transition from the current state and character return false
            if((final_state, a) not in self.d):
                return False
            # make the transition
            final_state = self.d[(final_state, a)]
        return final_state in self.F

    def minimize(self) -> 'DFA[STATE]':
       # check if there exists final states and create the W and P lists
       if self.F:
           W = [set(self.F)]
           P = [set(self.F)]
       else:
           W = []
           P = []
       # non final states is the difference between all states and the final ones
       non_final = self.K - self.F
       # add the non_final states to both lists
       if non_final:
           W.append(set(non_final))
           P.append(set(non_final))
       # while partitions exist in Working set
       while W:
           # pop a partition into Q
           Q = W.pop()
           # for all characters in the alphabet
           for c in self.S:
               # X is the set of all states that have a transition on char c in partition Q
               X = set()
               for s in self.K:
                   if self.d.get((s,c),None) in Q:
                       X.add(s)
               # update P and W
               new_P = []
               new_W = []
               # for all partitions in P
               for R in P:
                   # this checks if that partition has states that behave differently on the same character
                   if R & X and R-X:
                       # states that go to Q
                       R1 = set(R & X)
                       # state that don't go to Q
                       R2 = set(R - X)
                       # add them to the new_P
                       new_P.append(R1)
                       new_P.append(R2)
                       # if R is already in W, add both R1 and R2 else add the smaller split
                       if R in W:
                           new_W.append(R1)
                           new_W.append(R2)
                       elif len(R1)<=len(R2):
                           new_W.append(R1)
                       else:
                           new_W.append(R2)
                   else:
                       new_P.append(R)
                #update P  and extend W with new_W
               P = new_P
               W.extend(new_W)
        # After creating the partitions, create the new minimized DFA
       state_to_group = {}
       # For all blocks and their index
       for i, block in enumerate(P):
           # go through each state in block and assign the state to the index of the group
           for s in block:
               state_to_group[s] = i
        # then call remap_states
       return self.remap_states(lambda s: state_to_group[s])
        
    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        new_K = {f(s) for s in self.K}
        new_q0 = f(self.q0)
        new_F = {f(s) for s in self.F}
        new_d = {(f(s), c): f(nxt) for (s, c), nxt in self.d.items()}
        return DFA(S=self.S, K=new_K, q0=new_q0, d=new_d, F=new_F)

    
    