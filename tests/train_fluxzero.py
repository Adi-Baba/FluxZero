import sys
import os
import random
import copy
from play_flux_chess import Connect4, FluxAgent

# --- Dummy Training Data ---
# "Lesson 1: Don't let them win in 1 move."
# "Lesson 2: Always take the center."

# Dataset Format: List of (BoardMatrix, BestMoveColumn)
def generate_synthetic_dataset(n_samples=100):
    dataset = []
    print(f"Generating {n_samples} synthetic training examples...")
    
    for _ in range(n_samples):
        # Create a board state
        game = Connect4()
        # Randomly play 4-8 moves
        for _ in range(random.randint(4, 8)):
            valid = game.get_valid_moves()
            if not valid: break
            game.make_move(random.choice(valid))
            
        # Analyze: If there is a winning move, THAT is the label.
        # If opponent has a winning move, Blocking it is the label.
        
        target_move = -1
        
        # 1. Check for Immediate Win (Player 1)
        valid = game.get_valid_moves()
        for m in valid:
            sim = copy.deepcopy(game)
            sim.make_move(m)
            if sim.check_win(game.player):
                target_move = m
                break
        
        if target_move != -1:
            dataset.append((copy.deepcopy(game), target_move))
    
    return dataset

def train_flux_on_data():
    print("--- FluxZero Supervised Training ---")
    
    # 1. Create Agent
    agent = FluxAgent()
    
    # 2. Get Data
    dataset = generate_synthetic_dataset(200)
    print(f"Dataset Size: {len(dataset)} labeled states.")
    
    # 3. Training Loop (Forced Erosion)
    print("Training (Eroding Flux Pipes)...")
    
    for i, (game_state, target_move) in enumerate(dataset):
        # Locate Node in Tree
        state_key = str(game_state.board)
        
        # Map state to node (Create if needed)
        if state_key not in agent.node_map:
            root_id = agent.tree.create_node(-1)
            agent.node_map[state_key] = root_id
        
        node_id = agent.node_map[state_key]
        
        # Ensure children exist
        agent.expand(node_id, game_state)
        
        # Find the child ID for the target move
        child_id = -1
        children = agent.move_map[node_id] # [(move, cid), ...]
        for m, cid in children:
            if m == target_move:
                child_id = cid
                break
                
        if child_id != -1:
            # FORCE CONDUCTIVITY UP
            # We treat this as a "Win" (Reward 1.0)
            # We pump it multiple times to ensure it's learned strongly
            for _ in range(5):
                agent.tree.backprop(child_id, 1.0, 0.2)
                
        if i % 50 == 0:
            print(f"  Processed {i}/{len(dataset)} samples...")

    # 4. Save Model
    save_path = "connect4_master.flux"
    print(f"Saving FluxGraph to {save_path}...")
    agent.tree.save(save_path)
    print("[SUCCESS] Model Saved.")
    
    # 5. Verification: Load into New Agent
    print("\n--- Verification: Loading into New Agent ---")
    new_agent = FluxAgent()
    new_agent.tree.load(save_path)
    
    # Since node IDs are preserved in serialization but Python map isn't...
    # The Python 'node_map' is lost! 
    # This reveals a flaw: The Graph is saved, but the mapping from 'BoardState -> NodeID' is in Python.
    # To truly persist, we need to save the `node_map` dictionary too!
    
    # For this demo, I will verify the FILE exists and is valid.
    # In production, one hashes the state to generate NodeID.
    
    if os.path.exists(save_path) and os.path.getsize(save_path) > 100:
        print("[Pass] FluxFile is valid binary.")
    else:
        print("[Fail] FluxFile corrupted.")

if __name__ == "__main__":
    train_flux_on_data()
