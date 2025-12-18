import sys
import os

# Ensure we can import the local package
sys.path.insert(0, os.path.abspath("."))

print("--- Testing FluxZero Import ---")
try:
    from fluxzero import FluidTree
    print("[PASS] Import Successful.")
    
    # FluidTree constructor already creates Node 0.
    # So creating another node usually returns 1.
    agent = FluidTree()
    root = agent.create_node(-1)
    if root >= 0:
        print(f"[PASS] Core Engine call working. Created Node ID: {root}")
    else:
        print(f"[FAIL] Core Engine returned invalid ID: {root}")
        
except Exception as e:
    print(f"[FAIL] Import Error: {e}")
except OSError as e:
    print(f"[FAIL] Library Load Error: {e}")
