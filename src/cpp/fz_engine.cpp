#include "fz_engine.hpp"
#include <iostream>
#include <cmath>
#include <cstdlib>
#include <algorithm>

FluidTree::FluidTree() {
    // Root Node (ID = 0)
    nodes.push_back({0, 0, 0.5, {}, -1}); 
}

FluidTree::~FluidTree() {}

int FluidTree::create_node(int parent_id) {
    std::lock_guard<std::mutex> lock(m_mutex);
    // Bounds Check Parent
    if(parent_id >= (int)nodes.size()) throw std::runtime_error("Parent ID out of bounds");
    
    int id = nodes.size();
    nodes.push_back({id, 0, 0.5, {}, parent_id});
    return id;
}

void FluidTree::add_child(int parent_id, int child_id) {
    std::lock_guard<std::mutex> lock(m_mutex);
    if(parent_id < 0 || parent_id >= nodes.size()) throw std::runtime_error("Parent ID invalid");
    if(child_id < 0 || child_id >= nodes.size()) throw std::runtime_error("Child ID invalid");
    
    nodes[parent_id].children.push_back(child_id);
}

int FluidTree::select_leaf(int start_node, double exploration) {
    std::lock_guard<std::mutex> lock(m_mutex);
    if(start_node < 0 || start_node >= nodes.size()) throw std::runtime_error("Start Node Invalid");
    
    int curr = start_node;
    
    while(true) {
        if(curr >= nodes.size()) break;
        Node& n = nodes[curr];
        
        if(n.children.empty()) {
            return curr; // Found a leaf (or terminal)
        }
        
        // Use Fortran to pick child
        int n_child = n.children.size();
        std::vector<double> conds(n_child);
        for(int i=0; i<n_child; ++i) {
            conds[i] = nodes[n.children[i]].conductivity;
        }
        
        std::vector<double> probs(n_child);
        fz_calc_flow_probs(n_child, conds.data(), exploration, probs.data());
        
        // Sample
        double r = (double)rand() / RAND_MAX;
        double cum = 0;
        int next_idx = 0;
        for(int i=0; i<n_child; ++i) {
            cum += probs[i];
            if(r <= cum) {
                next_idx = i;
                break;
            }
        }
        // Safety for float errors
        if(next_idx >= n_child) next_idx = n_child - 1;
        
        curr = n.children[next_idx];
    }
    return curr;
}

void FluidTree::backpropagate(int leaf_node, double reward, double learning_rate) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    int curr = leaf_node;
    while(curr != -1) {
        Node& n = nodes[curr];
        n.visit_count++;
        
        // Update Conductivity (Erosion)
        double new_val;
        fz_update_conductivity(n.conductivity, reward, learning_rate, &new_val);
        n.conductivity = new_val;
        
        curr = n.parent;
    }
}

int FluidTree::get_visit_count(int node_id) {
    if(node_id < nodes.size()) return nodes[node_id].visit_count;
    return 0;
}

double FluidTree::get_conductivity(int node_id) {
     if(node_id < nodes.size()) return nodes[node_id].conductivity;
     return 0.0;
}

int FluidTree::get_best_child(int node_id) {
    std::lock_guard<std::mutex> lock(m_mutex);
    if(node_id >= nodes.size()) return -1;
    
    Node& n = nodes[node_id];
    if(n.children.empty()) return -1;
    
    int best_id = -1;
    int max_visits = -1;
    
    // Robust Move Selection: Pick Most Visited (Standard MCTS practice)
    for(int child_id : n.children) {
        if(nodes[child_id].visit_count > max_visits) {
            max_visits = nodes[child_id].visit_count;
            best_id = child_id;
        }
    }
    return best_id;
}

int FluidTree::get_children(int node_id, int* out_buf, int max_len) {
    std::lock_guard<std::mutex> lock(m_mutex);
    if(node_id < 0 || node_id >= nodes.size()) return -1;
    
    const Node& n = nodes[node_id];
    int count = n.children.size();
    
    if(out_buf && max_len > 0) {
        int copy_len = (count < max_len) ? count : max_len;
        for(int i=0; i<copy_len; ++i) {
            out_buf[i] = n.children[i];
        }
    }
    return count;
}

// --- Persistence (Saving the FluxGraph) ---
#include <fstream>
#include <stdexcept>

void FluidTree::save_to_file(const char* filename) {
    std::lock_guard<std::mutex> lock(m_mutex);
    std::ofstream out(filename, std::ios::binary);
    if(!out) throw std::runtime_error("Failed to open file for writing at " + std::string(filename));
    
    // Header
    char magic[4] = {'F', 'L', 'U', 'X'};
    out.write(magic, 4);
    
    int count = nodes.size();
    out.write((char*)&count, sizeof(int));
    if(!out) throw std::runtime_error("Write failed");
    
    for(const auto& n : nodes) {
        out.write((char*)&n.id, sizeof(int));
        out.write((char*)&n.visit_count, sizeof(int));
        out.write((char*)&n.conductivity, sizeof(double));
        out.write((char*)&n.parent, sizeof(int));
        
        int n_children = n.children.size();
        out.write((char*)&n_children, sizeof(int));
        if(n_children > 0) {
            out.write((char*)n.children.data(), n_children * sizeof(int));
        }
    }
    out.close();
}

void FluidTree::load_from_file(const char* filename) {
    std::lock_guard<std::mutex> lock(m_mutex);
    std::ifstream in(filename, std::ios::binary);
    if(!in.is_open()) return;
    
    char magic[4];
    in.read(magic, 4);
    if(magic[0]!='F' || magic[1]!='L' || magic[2]!='U' || magic[3]!='X') return;
    
    nodes.clear();
    int count;
    in.read((char*)&count, sizeof(int));
    
    for(int i=0; i<count; ++i) {
        Node n;
        in.read((char*)&n.id, sizeof(int));
        in.read((char*)&n.visit_count, sizeof(int));
        in.read((char*)&n.conductivity, sizeof(double));
        in.read((char*)&n.parent, sizeof(int));
        
        int n_children;
        in.read((char*)&n_children, sizeof(int));
        if(n_children > 0) {
            n.children.resize(n_children);
            in.read((char*)n.children.data(), n_children * sizeof(int));
        }
        nodes.push_back(n);
    }
    in.close();
}
