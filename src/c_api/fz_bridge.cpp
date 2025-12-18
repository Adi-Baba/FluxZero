#include "fz_engine.hpp"
#include <string>
#include <cstring>

// Global Error Buffer (Thread Local would be better but KISS for now)
static char last_error[256] = {0};

void set_error(const char* msg) {
    strncpy(last_error, msg, 255);
}

extern "C" {
    
    // --- Error Handling ---
    const char* FZ_GetLastError() {
        return last_error;
    }

    void* FZ_CreateTree() {
        try {
            return new FluidTree();
        } catch(const std::exception& e) {
            set_error(e.what());
            return nullptr;
        }
    }
    
    void FZ_DestroyTree(void* ptr) {
        if(!ptr) return;
        try {
             delete static_cast<FluidTree*>(ptr);
        } catch(...) {}
    }
    
    int FZ_CreateNode(void* ptr, int parent) {
        if(!ptr) { set_error("Null Pointer"); return -1; }
        try {
            return static_cast<FluidTree*>(ptr)->create_node(parent);
        } catch(const std::exception& e) {
            set_error(e.what());
            return -1;
        }
    }
    
    void FZ_AddChild(void* ptr, int parent, int child) {
        if(ptr) {
             try {
                 static_cast<FluidTree*>(ptr)->add_child(parent, child);
             } catch(const std::exception& e) {
                 set_error(e.what());
             }
        }
    }
    
    int FZ_SelectLeaf(void* ptr, int start, double expl) {
        if(!ptr) return -1;
        try {
            return static_cast<FluidTree*>(ptr)->select_leaf(start, expl);
        } catch(const std::exception& e) {
            set_error(e.what());
            return -1;
        }
    }
    
    void FZ_Backprop(void* ptr, int leaf, double reward, double lr) {
         if(ptr) {
             try {
                 static_cast<FluidTree*>(ptr)->backpropagate(leaf, reward, lr);
             } catch(...) {}
         }
    }
    
    int FZ_GetVisits(void* ptr, int node) {
        if(ptr) return static_cast<FluidTree*>(ptr)->get_visit_count(node);
        return 0;
    }
    
    double FZ_GetCond(void* ptr, int node) {
        if(ptr) return static_cast<FluidTree*>(ptr)->get_conductivity(node);
        return 0.0;
    }
    
    int FZ_GetBestChild(void* ptr, int node) {
        if(ptr) return static_cast<FluidTree*>(ptr)->get_best_child(node);
        return -1;
    }
    
    int FZ_GetChildren(void* ptr, int node, int* out_buf, int max_len) {
        if(ptr) return static_cast<FluidTree*>(ptr)->get_children(node, out_buf, max_len);
        return -1;
    }
    
    void FZ_Save(void* ptr, const char* filename) {
        if(ptr) {
            try {
                static_cast<FluidTree*>(ptr)->save_to_file(filename);
            } catch(const std::exception& e) {
                set_error(e.what());
            }
        }
    }
    
    void FZ_Load(void* ptr, const char* filename) {
        if(ptr) {
            try {
                static_cast<FluidTree*>(ptr)->load_from_file(filename);
            } catch(const std::exception& e) {
                set_error(e.what());
            }
        }
    }
}
