#ifndef FZ_ENGINE_HPP
#define FZ_ENGINE_HPP

#include <vector>
#include <map>
#include <mutex>

extern "C" {
    void fz_calc_flow_probs(int n, const double* conds, double expl, double* probs);
    void fz_update_conductivity(double old, double reward, double lr, double* new_val);
}

struct Node {
    int id;
    int visit_count;
    double conductivity; // Win Rate / Quality
    std::vector<int> children; // IDs of children
    int parent;
};

class FluidTree {
public:
    FluidTree();
    ~FluidTree();

    // Tree Management
    int create_node(int parent_id); // Returns new ID
    void add_child(int parent_id, int child_id);
    
    // Core FTS (Fluid Tree Search) Logic
    // Selects a path from start_node to a leaf based on Fluid Dynamics
    // Returns the ID of the leaf node selected
    int select_leaf(int start_node, double exploration);
    
    // Learning
    void backpropagate(int leaf_node, double reward, double learning_rate);
    
    // Diagnostics
    int get_visit_count(int node_id);
    double get_conductivity(int node_id);
    int get_best_child(int node_id); // Most visited
    int get_children(int node_id, int* out_buf, int max_len); // robust access
    
    // Persistence
    void save_to_file(const char* filename);
    void load_from_file(const char* filename);

private:
    std::vector<Node> nodes;
    std::mutex m_mutex;
};

#endif
