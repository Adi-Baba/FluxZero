import ctypes
import os

# Load DLL
# When installed via pip, the DLL should be in the same directory as this __init__.py
_dll_path = os.path.join(os.path.dirname(__file__), "fluxzero.dll")

try:
    _lib = ctypes.CDLL(_dll_path)
except OSError:
    # Fallback for development/manual layout
    try:
        # Try local first
         _lib = ctypes.CDLL(os.path.abspath("fluxzero.dll"))
    except OSError:
         # Try parent dir (old layout)
         _lib = ctypes.CDLL(os.path.abspath("../../fluxzero.dll"))

# Define Arg Types
_lib.FZ_CreateTree.restype = ctypes.c_void_p
_lib.FZ_DestroyTree.argtypes = [ctypes.c_void_p]

_lib.FZ_CreateNode.argtypes = [ctypes.c_void_p, ctypes.c_int]
_lib.FZ_CreateNode.restype = ctypes.c_int

_lib.FZ_AddChild.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

_lib.FZ_SelectLeaf.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double]
_lib.FZ_SelectLeaf.restype = ctypes.c_int

_lib.FZ_Backprop.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_double]

_lib.FZ_GetVisits.argtypes = [ctypes.c_void_p, ctypes.c_int]
_lib.FZ_GetVisits.restype = ctypes.c_int

_lib.FZ_GetBestChild.argtypes = [ctypes.c_void_p, ctypes.c_int]
_lib.FZ_GetBestChild.restype = ctypes.c_int

_lib.FZ_GetChildren.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int]
_lib.FZ_GetChildren.restype = ctypes.c_int

class FluidTree:
    def __init__(self):
        self._ptr = _lib.FZ_CreateTree()
        
    def __del__(self):
        if hasattr(self, '_ptr') and self._ptr:
            _lib.FZ_DestroyTree(self._ptr)
            
    def create_node(self, parent_id):
        return _lib.FZ_CreateNode(self._ptr, parent_id)
        
    def add_child(self, parent_id, child_id):
        _lib.FZ_AddChild(self._ptr, parent_id, child_id)
        
    def select_leaf(self, start_node, exploration=1.414):
        return _lib.FZ_SelectLeaf(self._ptr, start_node, exploration)
        
    def backprop(self, leaf_node, reward, lr=0.1):
        _lib.FZ_Backprop(self._ptr, leaf_node, reward, lr)
        
    # Persistence
    _lib.FZ_Save.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    _lib.FZ_Save.restype = None

    _lib.FZ_Load.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    _lib.FZ_Load.restype = None

class FluidTree:
    def __init__(self):
        self._ptr = _lib.FZ_CreateTree()
        
    def __del__(self):
        if hasattr(self, '_ptr') and self._ptr:
            _lib.FZ_DestroyTree(self._ptr)
            
    def create_node(self, parent_id):
        return _lib.FZ_CreateNode(self._ptr, parent_id)
        
    def add_child(self, parent_id, child_id):
        _lib.FZ_AddChild(self._ptr, parent_id, child_id)
        
    def select_leaf(self, start_node, exploration=1.414):
        return _lib.FZ_SelectLeaf(self._ptr, start_node, exploration)
        
    def backprop(self, leaf_node, reward, lr=0.1):
        _lib.FZ_Backprop(self._ptr, leaf_node, reward, lr)
        
    def get_best_child(self, node_id):
        return _lib.FZ_GetBestChild(self._ptr, node_id)
        
    def get_visits(self, node_id):
        return _lib.FZ_GetVisits(self._ptr, node_id)
        
    def get_children(self, node_id):
        # 1. Get Count
        count = _lib.FZ_GetChildren(self._ptr, node_id, None, 0)
        if count <= 0: return []
        
        # 2. Get Data
        ArrayType = ctypes.c_int * count
        buf = ArrayType()
        _lib.FZ_GetChildren(self._ptr, node_id, buf, count)
        return list(buf)
        
    def save(self, filename):
        b_name = filename.encode('utf-8')
        _lib.FZ_Save(self._ptr, b_name)
        
        # PERSISTENCE UPGRADE: Save Metadata/Map if exists
        # We look for a 'metadata' attribute or 'node_map' attribute on the instance
        import pickle
        meta = {}
        if hasattr(self, 'node_map'): meta['node_map'] = self.node_map
        if hasattr(self, 'root'): meta['root'] = self.root
        
        if meta:
            try:
                with open(filename + ".meta", "wb") as f:
                    pickle.dump(meta, f)
            except Exception as e:
                print(f"[FluxZero] Warning: Failed to save metadata: {e}")
        
    def load(self, filename):
        b_name = filename.encode('utf-8')
        _lib.FZ_Load(self._ptr, b_name)
        
        # PERSISTENCE UPGRADE: Load Metadata/Map
        import pickle
        meta_path = filename + ".meta"
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "rb") as f:
                    meta = pickle.load(f)
                    if 'node_map' in meta: self.node_map = meta['node_map']
                    if 'root' in meta: self.root = meta['root']
            except Exception as e:
                print(f"[FluxZero] Warning: Failed to load metadata: {e}")

    # --- Robustness Features ---
    def traverse_fuzzy(self, start_node, moves, move_map_access_func, tolerance=1):
        """
        Traverses the tree following 'moves' but allows for fuzzy matching.
        
        Args:
            start_node (int): Starting Node ID.
            moves (list): List of moves (integers 0-7 for directions).
            move_map_access_func (func): Function(node_id) -> {move: child_id}.
                                         Ideally this uses self.node_map[node_id].
            tolerance (int): Max difference in direction to accept (e.g. 1 means +/- 45 deg).
            
        Returns:
            int: The node ID reached, or -1 if lost.
        """
        curr = start_node
        for m in moves:
            # Get available children and their moves for current node
            children_map = move_map_access_func(curr) # {move: child_id}
            if not children_map: return -1
            
            if m in children_map:
                curr = children_map[m]
            else:
                # Fuzzy Search
                candidates = children_map.keys()
                # Sort by distance
                # Dist(a, b) = min(|a-b|, 8-|a-b|) for 8-dir
                # Generalize len check? Assume 8.
                
                best_cand = -1
                best_dist = 999
                
                for cand in candidates:
                    dist = min(abs(cand-m), 8-abs(cand-m))
                    if dist <= tolerance and dist < best_dist:
                        best_dist = dist
                        best_cand = cand
                
                if best_cand != -1:
                    curr = children_map[best_cand]
                else:
                    return -1
        return curr
