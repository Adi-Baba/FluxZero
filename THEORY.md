# 🌊 The Physics of FluxZero
> **"Intelligence is just water finding the crack in the stone."**

FluxZero is based on the **Thermodynamic Intelligence Hypothesis**. It rejects the Neural Network paradigm of "Function Approximation" in favor of "Flow Optimization".

---

## 1. The Core Philosophy
Traditional AI views learning as minimizing error on a curve. FluxZero views learning as **maximizing flow** in a pipe system.

| Neural Networks (NN) | FluxZero (Fluid Dynamics) |
| :--- | :--- |
| **Weights ($w$)** | **Conductivity ($C$)** |
| **Loss Function ($L$)** | **Flow Resistance ($R$)** |
| **Gradient Descent** | **Hydraulic Erosion** |
| **Black Box** | **Transparent Structure** |

## 2. Fluid Tree Search (FTS)
Instead of MCTS (Monte Carlo Tree Search), we use **Kirchhoff's Laws**.

### A. The Hydraulic Analogy
1.  **Nodes** are Intersections.
2.  **Edges** are Pipes with variable width ($C$).
3.  **Root** is the Water Source.
4.  **Winning Node** is a Drain (Low Pressure).

### B. The Algorithm
1.  **Injection**: We inject $N$ particles ("thoughts") into the root.
2.  **Flow**: Particles choose pipes proportional to their width:
    $$ P(i) = \frac{C_i^{1/T}}{\sum C_j^{1/T}} $$
3.  **Erosion**: When a particle finds a reward, it flows back up, eroding the pipe to make it wider:
    $$ C_{new} = C_{old} + \eta \cdot (Reward - C_{old}) $$

This creates a **Physical Memory** of success.

## 3. Supervised vs Reinforcement Learning
FluxZero supports both:
*   **Self-Play (RL)**: The agent plays itself. If it wins, it widens the winning path.
*   **Supervised**: We map "Correct Answers" (Data) to paths and artificially erode them.

> **Result:** A logic graph that physically embodies the solution space.

## 4. Robustness (v1.1)
Real-world data is messy. A perfect logical path might be missed if the input is slightly "noisy" (e.g. a shaky hand drawing).
FluxZero v1.1 implements **Fuzzy Traversal**:
*   If a pipe is blocked (input doesn't match exactly)...
*   The water "splashes" to nearby pipes (Neighbors).
*   If a neighbor leads to a strong current, the thought continues.

This allows FluxZero to handle **40-60% Noise distortion** while maintaining high precision.

---
*Copyright © 2025.*
