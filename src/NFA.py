from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # create a stack of states where we will push the next state on the epsilon closure
        stack = [state]
        # the closure will be a set where initially we have the starting state
        closure = {state}
        # Keep a visited set to skip visited nodes
        visited = set()
        # while there are elements on the stack
        while stack:
            # pop the first element
            current = stack.pop()
            # check all states that are reached from an epsilon transition from this state
            for next_state in self.d.get((current, EPSILON), set()):
                # add it to the closure
                closure.add(next_state)
                # check if this state was already added and skip adding to the stack if it was
                if next_state not in visited:
                    # else add the state to visited and push to the stack
                    visited.add(next_state)
                    stack.append(next_state)
                
        return closure
        
    def subset_construction(self) -> DFA[frozenset[STATE]]:
        # initial closure will be the epsilon_closure on the starting state
        initial_closure = self.epsilon_closure(self.q0)
        # initial_state is a frozenset with initial closure (to be hashable we use frozenset)
        initial_state = frozenset(initial_closure)
        # dfa_states is initially simply the initial_state which as we know is a frozenset
        dfa_states = {initial_state}
        # no transitions initially have been processed
        dfa_transitions = {}
        # same with final_states
        dfa_final_states = set()
        # didn't process the final_state yet
        unprocessed_states = [initial_state]
        # we need a sink_state in case there is a case where a transition on a character does not exist
        sink_state = frozenset()
        sink_needed = False
        # while there are unprocessed_states
        while unprocessed_states:
            # pop the first state group
            current = unprocessed_states.pop()
            # for all characters in alfabet
            for symbol in self.S:
                # check the transitions for all states in the group and update next_states
                next_states = set()
                for nfa_state in current:
                    next_states.update(self.d.get((nfa_state, symbol), set()))
                epsilon_closure_next = set()
                # after that apply the epsilon closure on each added state
                for ns in next_states:
                    epsilon_closure_next.update(self.epsilon_closure(ns))
                # if there is at least one transition on this character
                if epsilon_closure_next:
                    # create a fronzenset from the epsilon_closure_next
                    next_frozenset = frozenset(epsilon_closure_next)
                    # update the dfa_transitions with this next_frozenset
                    dfa_transitions[(current, symbol)] = next_frozenset
                    # if next_frozenset was not in the dfa states, add it and add it to unprocessed states
                    if next_frozenset not in dfa_states:
                        dfa_states.add(next_frozenset)
                        unprocessed_states.append(next_frozenset)
                # If there is no transition from any element in current group on this symbol
                else:
                    # update transitions on this symbol for this group to sink_state 
                    dfa_transitions[(current, symbol)] = sink_state
                    # add sink_state to the states, and append it to unprocessed_states
                    if not sink_needed:
                        sink_needed = True
                        dfa_states.add(sink_state)
                        unprocessed_states.append(sink_state)
        # the groups with final states will be the final groups
        for dfa_state in dfa_states:
            if any(s in self.F for s in dfa_state):
                dfa_final_states.add(dfa_state)
        # return the new DFA
        return DFA(
            S=self.S,
            K=dfa_states,
            q0=initial_state,
            d=dfa_transitions,
            F=dfa_final_states
        )

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        new_K = {f(s) for s in self.K}
        new_q0 = f(self.q0)
        new_F = {f(s) for s in self.F}
        new_d = {}
        for (s, symbol), nxt_set in self.d.items():
            new_nxt_set = {f(nxt_state) for nxt_state in nxt_set}
            new_d[(f(s), symbol)] = new_nxt_set
        return NFA(S=self.S, K=new_K, q0=new_q0, d=new_d, F=new_F)
