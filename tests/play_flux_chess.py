import sys
import os
import random
import copy

# Add bindings
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "bindings", "python"))
from fluxzero import FluidTree

# --- Connect 4 Logic ---
ROWS = 6
COLS = 7

class Connect4:
    def __init__(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.player = 1 # 1 or 2
        
    def get_valid_moves(self):
        moves = []
        for c in range(COLS):
            if self.board[0][c] == 0:
                moves.append(c)
        return moves
        
    def make_move(self, col):
        if self.board[0][col] != 0: return False
        for r in range(ROWS-1, -1, -1):
            if self.board[r][col] == 0:
                self.board[r][col] = self.player
                self.player = 3 - self.player # Switch
                return True
        return False
        
    def check_win(self, p):
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS-3):
                if self.board[r][c] == p and self.board[r][c+1] == p and \
                   self.board[r][c+2] == p and self.board[r][c+3] == p: return True
        # Vertical
        for r in range(ROWS-3):
            for c in range(COLS):
                if self.board[r][c] == p and self.board[r+1][c] == p and \
                   self.board[r+2][c] == p and self.board[r+3][c] == p: return True
        # Diag 1
        for r in range(ROWS-3):
            for c in range(COLS-3):
                if self.board[r][c] == p and self.board[r+1][c+1] == p and \
                   self.board[r+2][c+2] == p and self.board[r+3][c+3] == p: return True
        # Diag 2
        for r in range(3, ROWS):
            for c in range(COLS-3):
                if self.board[r][c] == p and self.board[r-1][c+1] == p and \
                   self.board[r-2][c+2] == p and self.board[r-3][c+3] == p: return True
        return False
        
    def is_full(self):
        return all(self.board[0][c] != 0 for c in range(COLS))

# --- FluxZero Agent ---
class FluxAgent:
    def __init__(self):
        self.tree = FluidTree()
        self.node_map = {} # Python State Object -> Tree Node ID
        self.move_map = {} # Node ID -> [(move, child_id)] mapping (Simple memoization)
        
    def expand(self, node_id, game_state):
        if node_id in self.move_map: return # Already expanded
        
        moves = game_state.get_valid_moves()
        children = []
        for m in moves:
            cid = self.tree.create_node(node_id)
            self.tree.add_child(node_id, cid)
            children.append((m, cid))
            
        self.move_map[node_id] = children

    def get_action(self, game_state, simulations=1000):
        # 1. Map current state to tree node
        state_key = str(game_state.board)
        if state_key not in self.node_map:
            # New root for this search
            # (In a real engine we kept the old tree, here we rebuild for simplicity)
            root_id = self.tree.create_node(-1) 
            self.node_map[state_key] = root_id
            # Expand root immediately
            self.expand(root_id, game_state)
            
        root_id = self.node_map[state_key]
        
        # 2. Fluid Tree Search (Simulation Loop)
        # Ensure root is expanded
        self.expand(root_id, game_state)
        child_ids = self.move_map[root_id]
        
        for _ in range(simulations):
            # 1. Pick Child (Bandit/Flux) using C++ logic
            selected_leaf_id = self.tree.select_leaf(root_id, 1.414)
            
            # If leaf is root (no children yet? shouldn't happen due to expand)
            # Or if leaf needs expansion?
            # For this simple demo (1-ply lookahead with rollouts), we stop at children of root.
            # Real MCTS would expand the leaf if visited enough.
            
            # Find which move this corresponds to (from Root)
            # This is a simplification: We assume the tree depth is handled by C++ 
            # but here we only handle 1-level mapping for the Python Rollout.
            # Ideally: C++ traverses deep, returns a leaf. We rollout from THAT leaf.
            # But we don't have the GameState for deep nodes stored in C++.
            # So we just rollout from the CHILD of root corresponding to the path.
            
            # Map leaf back to a move from root? 
            # No, select_leaf returns a node ID deep in the tree.
            # But since we only expanded the root, select_leaf will return one of the children of root (since they are leaves).
            
            selected_move = -1
            for m, cid in child_ids:
                if cid == selected_leaf_id:
                    selected_move = m
                    break
            
            if selected_move == -1:
                # Should not happen unless leaf is root
                # If leaf is root, pick random child
                 if child_ids:
                    selected_move, selected_leaf_id = random.choice(child_ids)
                 else:
                    break # Game over
                
            # 2. Rollout (Python)
            sim_game = copy.deepcopy(game_state)
            sim_game.make_move(selected_move)
            
            value = 0.5 # Draw
            winner = 0
            
            # Play Randomly until end
            while not sim_game.is_full():
                if sim_game.check_win(1): 
                    winner = 1; break
                if sim_game.check_win(2): 
                    winner = 2; break
                
                valid = sim_game.get_valid_moves()
                if not valid: break
                sim_game.make_move(random.choice(valid))
                
            if winner == 1: value = 1.0 # FluxWin
            elif winner == 2: value = 0.0 # Loss
            
            # 3. Backprop (C++)
            # FluxZero update: Reward = Conductivity
            self.tree.backprop(selected_leaf_id, value, 0.1)
            
        # Pick best move (Most Visited / Highest Flux)
        best_child_id = self.tree.get_best_child(root_id)
        
        for m, cid in child_ids:
            if cid == best_child_id:
                return m
                
        return random.choice(game_state.get_valid_moves()) # Fallback

def play_match():
    print("--- FluxZero vs Random (Connect 4) ---")
    game = Connect4()
    agent = FluxAgent()
    
    while not game.is_full():
        # Check Wins
        if game.check_win(1): print("FluxZero Wins!"); return
        if game.check_win(2): print("Random Wins!"); return
        
        if game.player == 1:
            # FluxZero thinking
            # print("FluxZero Thinking...")
            move = agent.get_action(game, simulations=500)
            game.make_move(move)
            # print(f"FluxZero plays Col {move}")
        else:
            # Random
            moves = game.get_valid_moves()
            move = random.choice(moves)
            game.make_move(move)
            # print(f"Random plays Col {move}")
            
    print("Draw!")

if __name__ == "__main__":
    play_match()
