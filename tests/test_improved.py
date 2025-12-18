import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fluxzero import FluidTree
import os

def test_improvements():
    print("--- Testing FluxZero Improvements ---")
    tree = FluidTree()
    
    # 1. Test get_children support
    root = tree.create_node(-1)
    c1 = tree.create_node(root)
    c2 = tree.create_node(root)
    tree.add_child(root, c1)
    tree.add_child(root, c2)
    
    children = tree.get_children(root)
    print(f"Children of Root ({root}): {children}")
    
    if set(children) == {c1, c2}:
        print("[PASS] get_children returned correct IDs.")
    else:
        print(f"[FAIL] Expected {{{c1}, {c2}}}, got {set(children)}")
        
    # 2. Test Persistence with Metadata
    tree.root = root
    tree.node_map = {'root': root, 'c1': c1, 'c2': c2}
    
    print("Saving with metadata...")
    tree.save("test_robust.flux")
    
    # Load into new tree
    tree2 = FluidTree()
    tree2.load("test_robust.flux")
    
    if hasattr(tree2, 'root') and tree2.root == root:
         print(f"[PASS] Metadata 'root' loaded: {tree2.root}")
    else:
         print("[FAIL] Metadata 'root' lost.")
         
    if hasattr(tree2, 'node_map') and len(tree2.node_map) == 3:
         print(f"[PASS] Metadata 'node_map' loaded: {tree2.node_map}")
    else:
         print("[FAIL] Metadata 'node_map' lost.")
         
    # 3. Test Fuzzy Traversal (Mock)
    # mock accessor
    def get_moves(nid):
        if nid == root: return {0: c1, 2: c2} # 0=N, 2=E
        return {}
    
    # Exact match
    res = tree.traverse_fuzzy(root, [0], get_moves)
    if res == c1: print("[PASS] Fuzzy Traversal (Exact) worked.")
    
    # fuzzy match (1 is NE, close to 0=N)
    res = tree.traverse_fuzzy(root, [1], get_moves, tolerance=1)
    if res == c1: print("[PASS] Fuzzy Traversal (Fuzzy 1->0) worked.")
    else: print(f"[FAIL] Fuzzy 1->0 failed. Got {res}")

if __name__ == "__main__":
    test_improvements()
