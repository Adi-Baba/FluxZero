import sys
import os
import math
import ctypes

# Add bindings
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "bindings", "python"))
from fluxzero import FluidTree

def sieve_primes(n):
    """Generates first n primes."""
    print(f"Generating {n} primes...")
    limit = int(n * (math.log(n) + math.log(math.log(n)))) + 100
    if n < 10: limit = 50
    
    is_prime = [True] * limit
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            for x in range(i*i, limit, i):
                is_prime[x] = False
                
    primes = []
    for i, p in enumerate(is_prime):
        if p:
            primes.append(i)
            if len(primes) >= n: break
    return primes

def run_prediction():
    print("--- FluxZero Prime Prediction ---\n")
    
    # 1. Generate Data
    TOTAL_PRIMES = 101000
    primes = sieve_primes(TOTAL_PRIMES)
    
    train_primes = primes[:100000]
    test_primes = primes[100000:101000]
    
    # Calculate Gaps
    # Gaps are always even (except 2->3).
    train_gaps = [train_primes[i+1] - train_primes[i] for i in range(len(train_primes)-1)]
    
    print(f"Training on {len(train_gaps)} gaps (100k Primes).")
    
    # 2. Build Flux Neural Net (Markov Graph)
    # Structure: Root -> [Previous_Gap Nodes] -> [Next_Gap Nodes]
    # We learn P(Next | Prev)
    
    tree = FluidTree()
    root = tree.create_node(-1)
    
    # Map GapValue -> NodeID (First Layer)
    # We need a persistent map because we reuse these source nodes
    gap_nodes = {} 
    
    # 3. Train (Erode Pipes)
    print("Training FluxGraph...")
    
    # Pre-Create nodes for observed gaps (Optimization)
    unique_gaps = set(train_gaps)
    for g in unique_gaps:
        nid = tree.create_node(root)
        gap_nodes[g] = nid
        # Tag the node? No, we just store ID in map.
        
    # We also need a map for children of EACH node?
    # Because FluxZero doesn't expose "Get Child by Value", we have to track it in Python.
    # Map: NodeID -> { NextGapVal : ChildNodeID }
    transitions = { nid: {} for nid in gap_nodes.values() }
    
    for i in range(len(train_gaps) - 1):
        prev = train_gaps[i]
        curr = train_gaps[i+1]
        
        # Get Source Node (Prev Gap)
        src_id = gap_nodes[prev]
        
        # Get/Create Target Edge (Next Gap)
        # Check if 'curr' is already a child of 'src_id'
        if curr not in transitions[src_id]:
            # Create child representing outcome 'curr'
            child_id = tree.create_node(src_id)
            tree.add_child(src_id, child_id)
            transitions[src_id][curr] = child_id
        
        target_child_id = transitions[src_id][curr]
        
        # ERODE (Reinforce this transition)
        # Reward 1.0 (It happened)
        # This increases conductivity of Prev->Curr
        tree.backprop(target_child_id, 1.0, 0.5)
        
        if i % 20000 == 0:
            print(f"  Processed {i} gaps...")
            
    print("[Done] Training Complete.")
    
    # 4. Predict
    print("\nPredicting next 1000 primes...")
    
    current_gap = train_gaps[-1]
    current_prime = train_primes[-1]
    
    predictions = []
    
    correct_exact = 0
    correct_prime = 0
    
    print(f"Start Prime: {current_prime}")
    
    for i in range(1000):
        # Lookup Node for current context
        if current_gap not in gap_nodes:
            # Unknown gap seen! Fallback to most common (e.g. 6) or random
            # Just say 6
            next_gap = 6
        else:
            src_id = gap_nodes[current_gap]
            
            # Use Flux Engine to select next state
            # select_leaf traverses from src_id to a leaf (Next Gap)
            # Probabilities are proportional to conductivity (Frequency in training)
            best_leaf = tree.select_leaf(src_id, exploration=0.1) # Low temp for prediction
            
            # Map Leaf ID back to Gap Value
            # Reverse lookup in transitions[src_id]
            next_gap = 0
            for gap_val, child_id in transitions[src_id].items():
                if child_id == best_leaf:
                    next_gap = gap_val
                    break
            
            if next_gap == 0: next_gap = 6 # Fallback
            
        # Record
        next_prime = current_prime + next_gap
        predictions.append(next_prime)
        
        # Validate
        actual_prime = test_primes[i]
        if next_prime == actual_prime:
            correct_exact += 1
            
        # Is it prime at all?
        # Simple trial division for check
        is_p = True
        if next_prime % 2 == 0: is_p = False
        else:
            for d in range(3, int(math.sqrt(next_prime)) + 1, 2):
                if next_prime % d == 0:
                     is_p = False; break
        if is_p: correct_prime += 1
        
        # Update State
        current_prime = next_prime
        current_gap = next_gap
        
    print(f"\n--- Results (Next 1000) ---")
    print(f"Exact Matches:   {correct_exact}/1000 ({correct_exact/10.0}%)")
    print(f"Primes Found:    {correct_prime}/1000 ({correct_prime/10.0}%)")
    
    if correct_exact > 0:
        print("[SUCCESS] FluxZero predicted some primes correctly based on Gap Dynamics!")
    else:
        print("[FAIL] No matches.")

if __name__ == "__main__":
    run_prediction()
