import itertools
from collections import deque
from dataclasses import dataclass
from typing import Tuple

#---------- Board & State ----------
BOARD_SIZE = 5
Coord = Tuple[int,int]

@dataclass(frozen=True)
class State:
    wk: Coord   # White King
    wr: Coord   # White Rook
    bk: Coord   # Black King
    white: bool # True if it's White's move

def in_bounds(p): return 0 <= p[0] < BOARD_SIZE and 0 <= p[1] < BOARD_SIZE
def coord_to_alg(c): return "--" if not in_bounds(c) else f"{'abcde'[c[0]]}{'12345'[c[1]]}"
def kings_adjacent(a,b): return max(abs(a[0]-b[0]), abs(a[1]-b[1])) <= 1

#---------- Move Generation ----------
def rook_attacks(wr, wk, bk):
    if not in_bounds(wr): return set()
    attacks = set()
    rx,ry = wr
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        x,y = rx+dx, ry+dy
        while in_bounds((x,y)):
            attacks.add((x,y))
            if (x,y) in (wk,bk): break
            x += dx; y += dy
    return attacks

def legal_black_moves_all(state):
    wk,wr,bk = state.wk, state.wr, state.bk
    moves = []
    for dx,dy in itertools.product([-1,0,1], repeat=2):
        if dx==0 and dy==0: continue
        np_ = (bk[0]+dx, bk[1]+dy)
        if not in_bounds(np_): continue
        if np_ == wk: continue
        if kings_adjacent(wk, np_): continue
        new_wr = wr
        if in_bounds(wr) and np_ == wr:
            new_wr = (-1,-1)  # rook captured
        if in_bounds(new_wr):
            if np_ in rook_attacks(new_wr, wk, np_):
                continue
        moves.append((f"k{coord_to_alg(bk)}->{coord_to_alg(np_)}", State(wk, new_wr, np_, True)))
    return moves

def legal_white_moves(state):
    wk,wr,bk = state.wk, state.wr, state.bk
    moves = []
    # King moves
    for dx,dy in itertools.product([-1,0,1], repeat=2):
        if dx==0 and dy==0: continue
        np_ = (wk[0]+dx, wk[1]+dy)
        if not in_bounds(np_): continue
        if np_ == wr or np_ == bk: continue
        if kings_adjacent(np_, bk): continue
        moves.append((f"K{coord_to_alg(wk)}->{coord_to_alg(np_)}", State(np_, wr, bk, False)))
    # Rook moves (safe only)
    if in_bounds(wr):
        rx,ry = wr
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            x,y = rx+dx, ry+dy
            while in_bounds((x,y)):
                np_ = (x,y)
                if np_ == wk or np_ == bk: break
                candidate = State(wk, np_, bk, False)
                capturable = False
                for _, ns in legal_black_moves_all(candidate):
                    if ns.wr == (-1,-1):
                        capturable = True; break
                if not capturable:
                    moves.append((f"R{coord_to_alg(wr)}->{coord_to_alg(np_)}", candidate))
                x += dx; y += dy
    return moves

#--------- Goal Test ----------
def is_checkmate(state):
    if state.white: return False
    if not in_bounds(state.wr): return False
    if state.bk not in rook_attacks(state.wr, state.wk, state.bk): return False
    return len(legal_black_moves_all(state)) == 0

#---------- Black Policy ----------
center = (BOARD_SIZE//2, BOARD_SIZE//2)
def black_policy(state):
    moves = legal_black_moves_all(state)
    if not moves: return None
    cx,cy = center
    return min(moves, key=lambda m: abs(m[1].bk[0]-cx)+abs(m[1].bk[1]-cy))[1]

#---------- DFS ----------
def dfs(start):
    stack = [(start, [])]  # state, path
    visited = set()
    expanded = 0

    while stack:
        state, path = stack.pop()
        if state in visited: continue
        visited.add(state)
        expanded += 1

        if is_checkmate(state):
            return expanded, len(path), path

        if state.white:
            for move, ns in reversed(legal_white_moves(state)):
                stack.append((ns, path + [move]))
        else:
            nxt = black_policy(state)
            if nxt:
                move = f"Black→{coord_to_alg(state.bk)}->{coord_to_alg(nxt.bk)}"
                stack.append((nxt, path + [move]))
    return expanded, None, None

#---------- Run ----------
start = State((0,0),(0,2),(4,4), True)
expanded, length, path = dfs(start)

print("\nΑΠΟΤΕΛΕΣΜΑΤΑ ΑΛΓΟΡΙΘΜΟΥ DFS")
print("--------------------------------")
print(f"• Μήκος λύσης: {length} βήματα")
print(f"• Κόστος (κόμβοι που επεκτάθηκαν): {expanded}")

if path:
    print("• Ακολουθία κινήσεων:")
    for step, move in enumerate(path, start=1):
        print(f"   {step}. {move}")
else:
    print(" Δεν βρέθηκε λύση.")
