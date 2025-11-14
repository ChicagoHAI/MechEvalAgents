# Documentation: Reverse-Engineering Implicit Chain-of-Thought for Multi-Digit Multiplication

## 1. Goal

### Research Hypothesis Evolution
This research investigates why Transformers fail at a seemingly simple task: multi-digit multiplication. Despite having billions of parameters, models like Llama-3.2 90B or GPT4 fail at 4×4-digit multiplication, even when explicitly fine-tuned on the task.

**Primary Research Question:** Why do Transformers fail to learn multiplication?

**Hypothesis:** By reverse-engineering a model that successfully learns multiplication via implicit chain-of-thought (ICoT), we can uncover the mechanisms required for multi-digit multiplication and understand what standard fine-tuning (SFT) models lack.

### Circuit Objective
The objective is to identify and understand:
1. Evidence of long-range structure needed for multi-digit multiplication
2. The mechanism by which successful models encode long-range dependencies
3. The geometric representations that enable correct multiplication
4. The learning dynamics that cause standard fine-tuning to fail
5. Potential fixes to enable learning without explicit chain-of-thought

## 2. Data

### Dataset Description
- **Task:** 4×4 digit multiplication (smallest setting where SFT fails but ICoT succeeds)
- **Training Set:** 80,800 samples
- **Validation Set:** 1,000 held-out samples  
- **Test Set:** 1,000 held-out samples
- **Format:** Operands written least-significant digit first (e.g., `1338 * 5105` for 8331 × 5015)

### Data Format Examples

**Standard Fine-Tuning Format:**
```
a0a1a2a3 * b0b1b2b3%%%#### c0 . . . c7
```

**ICoT Training Format** (with chain-of-thought tokens qi):
```
Epoch 1: a0a1a2a3 * b0b1b2b3%%% q0 . . . qi... qj . . . qk . . . qτ #### c0 . . . c7
Epoch 2: a0a1a2a3 * b0b1b2b3%%% qi... qj . . . qk . . . qτ #### c0 . . . c7
...
Epoch N: a0a1a2a3 * b0b1b2b3%%% #### c0 . . . c7
```

**Actual ICoT Example** (8331 × 5015):
```
1338 * 5105||5614 + 013380(569421) + 0000000(5694210) + 0005561%%####56997714
```

The chain-of-thought tokens show:
- Partial products (e.g., 12×4 = 48)
- Running sums (e.g., 408 after adding 12×4 and 12×30)
- Intermediate calculations needed for multi-digit multiplication

### Preprocessing
- Digits are presented in least-significant-first order
- Special delimiters: `%` and `#` separate operands from intermediate computations and final answer
- At each training epoch, a fixed number (8) of CoT tokens are removed from the left

## 3. Method

### Model Architecture
- **Smallest Successful Architecture:** 2-layer, 4-head GPT-based Transformer
- **Embedding Dimension (d):** 768 (inferred from standard GPT-2 config)
- **Vocabulary:** Digits 0-9, special tokens (*, %, #, ||, parentheses)
- **Training from Scratch:** No pre-trained weights used to avoid confounding factors

### Training Procedures

#### Implicit Chain-of-Thought (ICoT) Training
- **Learning Rate:** 5e-5
- **Optimizer:** AdamW (inferred from standard practice)
- **Epochs:** 13 (convergence point)
- **CoT Token Removal:** 8 tokens removed per epoch
- **Final Accuracy:** 100% on test set

#### Standard Fine-Tuning (SFT)
- **Same hyperparameters** as ICoT
- **Input Format:** Direct operands to answer (no intermediate tokens)
- **Final Accuracy:** < 1% on test set, ~81% digit-level accuracy
- **Scaling Test:** 12-layer, 8-head model achieves same poor performance

#### Auxiliary Loss Model
- **Additional Component:** Linear regression probes attached to H(=2) attention heads in layer 2
- **Auxiliary Loss:** MSE loss to predict accumulated sum ĉk at each timestep tck
- **Loss Function:**  
  ```
  z_h^i = w_h^T ATT2_h(·)
  L_aux = (1/H) Σ_h (1/8) Σ_i (z_h^i - ĉ_i)^2
  L = L_LM + λL_aux
  ```
- **Final Accuracy:** 99% on test set

### Key Metrics and Analyses

1. **Logit Attribution:** Measure change in output logits when perturbing input operand digits
2. **Linear Regression Probing:** Probe hidden states for intermediate value ĉk (running sum)
3. **Attention Pattern Analysis:** Visualize attention maps to understand information flow
4. **Gradient Norm Tracking:** Monitor per-token gradient norms during training
5. **Loss Per Token:** Track loss for each output digit c0-c7 separately
6. **PCA Visualization:** 3D PCA of attention outputs and hidden states
7. **Fourier Basis Analysis:** R² fits of embeddings/hidden states to trigonometric bases

## 4. Results

### Model Performance

| Model | Architecture | Accuracy | Digit-Level Accuracy |
|-------|--------------|----------|---------------------|
| ICoT | 2L4H | 100% | ~100% |
| SFT | 2L4H | < 1% | ~81% |
| SFT (scaled) | 12L8H | < 1% | ~80% |
| Auxiliary Loss | 2L4H | 99% | ~99% |

### Evidence of Long-Range Dependencies

#### Logit Attribution Results
- **ICoT Model:** Shows correct dependencies - digits ai, bj affect output ck only when k ≥ i, with strongest effects when i+j = k
- **SFT Model:** Does not show correct long-range dependencies between earlier tokens and middle output digits

#### Linear Probe Results (Mean Absolute Error for ĉk prediction)

| Digit | ĉ2 | ĉ3 | ĉ4 | ĉ5 | ĉ6 |
|-------|----|----|----|----|-----|
| SFT | 93.69 | 113.27 | 74.47 | 79.40 | 28.22 |
| ICoT | 2.00 | 1.89 | 1.74 | 0.97 | 0.56 |

The ICoT model can accurately decode the intermediate running sum ĉk from hidden states, while SFT cannot.

### Discovered Mechanisms

#### Attention Tree Structure
The ICoT model constructs a shallow directed acyclic graph (binary-tree-like) through attention patterns:

1. **Layer 1 (Caching):** Each attention head attends to pairs of digits {ai, bj} and "caches" pairwise products aibj in hidden states h¹t
2. **Layer 2 (Retrieval):** Attention heads attend to previous timesteps where relevant products were cached
3. **Example for c2:** Requires a2b0, a1b1, a0b2, and ĉ1 (which requires a1b0, a0b1, a0b0)

The sparse attention pattern allows the model to:
- Select correct digit pairs for partial products
- Cache intermediate computations in earlier tokens  
- Retrieve them for later digits

### Geometric Representations

#### Minkowski Sums in Attention Heads
When attention heads attend to two digits ai, bj with attention weights α and (1-α), the output forms a Minkowski sum:

```
ATT¹(i,j) = αAi + (1-α)Bj + ε
{ATT¹(i,j)}i,j ⊆ (αA) ⊕ ((1-α)B) ⊕ ε
```

This creates nested representations: 3D PCA reveals clusters (for ai) containing sub-clusters (for bj) with identical geometry at global and local scales.

#### Fourier Basis Embeddings (Pentagonal Prism)
The ICoT model represents digits using Fourier bases with frequencies k ∈ {0, 1, 2, 5}:

```
Φ(n) = [1(n), cos(2πn/10), sin(2πn/10), cos(2πn/5), sin(2πn/5), p(n)]
```

where p(n) = (-1)ⁿ is the parity vector.

**3D PCA Structure:**
- PC1: Parity vector p(n), separating even/odd digits
- PC2-PC3: k=2 Fourier pair, forming two regular pentagons
- Result: Pentagonal prism geometry with parallel pentagons for even/odd digits

**Fourier Fit Quality (Median R²):**
- Embeddings E: 0.84 (k=0,1,2,5), 1.0 (k=0,1,2,3,4,5)
- MLP output weights: 0.95 (k=0,1,2,5), 1.0 (k=0,1,2,3,4,5)  
- Final hidden layer h^L: 0.99 (k=0,1,2,5), 1.0 (k=0,1,2,3,4,5)

The SFT model shows no clear geometric structure in 3D PCA.

## 5. Analysis

### Learning Dynamics Analysis

#### Standard Fine-Tuning Failure Pattern
Gradient norm and loss analysis reveals:

1. **Digits Learned First:** c0, c1 (first two), then c7 (last digit)
2. **Gradient Flow:** Early digits receive gradients initially, but gradient norms drop to zero after learning
3. **Middle Digit Plateau:** c3-c6 receive gradients but loss plateaus - stuck in local optimum
4. **Missing Mechanism:** Model never learns the long-range dependencies needed for middle digits
5. **Scaling Doesn't Help:** 12-layer model shows identical failure pattern

#### Why SFT Fails
Under gradient descent with autoregressive loss:
- The model can learn local patterns (first/last digits)  
- It cannot discover the attention tree structure needed for long-range dependencies
- No gradient signal encourages the binary-tree caching mechanism
- Converges to a suboptimal solution lacking the required computational structure

#### ICoT Success Mechanism  
By gradually removing chain-of-thought tokens:
- Model is forced to internalize intermediate computations in hidden states
- Provides implicit supervision for developing attention trees
- Guides the model toward representations with long-range dependencies
- Enables discovery of Fourier basis and Minkowski sum structures

### Hypothesis Refinement Through Iterations

**Initial Observation:** Transformers fail at multi-digit multiplication despite large scale

**First Insight:** ICoT models succeed where SFT fails (same architecture, different training)

**Second Insight:** Success requires long-range dependencies captured by intermediate value ĉk

**Mechanistic Understanding:** Long-range dependencies implemented via:
- Binary attention trees for caching/retrieval
- Minkowski sums for pairwise products
- Fourier bases for efficient digit representation

**Root Cause:** Standard gradient descent + autoregressive loss fails to learn these structures

**Validation:** Auxiliary loss providing ĉk supervision enables learning without explicit CoT

### Key Findings from Ablations

1. **Architecture Sensitivity:** 2L4H is minimal architecture where ICoT works
2. **Data Efficiency:** 80,800 samples sufficient for ICoT, insufficient for SFT regardless of scale
3. **Probe Locations:** Layer 2 mid-point (after attention, before MLP) best decodes ĉk
4. **Fourier Frequencies:** k ∈ {0,1,2,5} capture 85-99% variance; k ∈ {0,1,2,3,4,5} achieves perfect fits
5. **Auxiliary Loss Comparison:** Model with auxiliary loss shows similar (but not identical) attention tree structure to ICoT

## 6. Next Steps

### Immediate Extensions
1. **Generalization Testing:** Evaluate on larger multiplication tasks (5×5, 6×6 digits)
2. **Architecture Variations:** Test with different layer/head configurations
3. **Alternative Inductive Biases:** Explore other auxiliary losses that encourage long-range dependencies
4. **Transfer Learning:** Investigate whether ICoT-learned mechanisms transfer to other arithmetic tasks

### Open Questions
1. **Generic Solutions:** Can we find training procedures that work across tasks requiring long-range dependencies?
2. **Theoretical Understanding:** What optimization landscapes lead to the local optimum trap in SFT?
3. **Attention Tree Discovery:** What minimal inductive biases enable discovering tree structures?
4. **Fourier Basis Emergence:** Why do Fourier representations emerge? Are they optimal for modular arithmetic?
5. **Scaling Laws:** How do the discovered mechanisms scale to larger models and datasets?

### Potential Improvements
1. **Architectural Biases:** Design attention mechanisms that naturally favor tree-like information flow
2. **Curriculum Learning:** Gradually increase multiplication difficulty during training
3. **Regularization:** Add losses that encourage structured attention patterns
4. **Hybrid Approaches:** Combine explicit and implicit chain-of-thought  
5. **Meta-Learning:** Learn to discover appropriate computational structures for new tasks

### Broader Applications
1. **Long-Range Reasoning Tasks:** Apply insights to other tasks requiring distant context integration
2. **Scientific Discovery:** Use mechanistic interpretability to understand failure modes in other domains
3. **Architecture Design:** Inform development of transformers better suited for algorithmic reasoning
4. **Training Methodology:** Develop general techniques for escaping local optima in neural network training

## 7. Main Takeaways

### Core Insights

1. **Long-Range Dependencies Are Critical but Hard to Learn**  
   Multi-digit multiplication requires using information from all partial products {aibj | i+j ≤ k} to compute digit ck. Standard fine-tuning fails to discover these dependencies under gradient descent with autoregressive loss.

2. **Success Requires Specific Computational Structures**  
   The ICoT model implements three key mechanisms absent in SFT:
   - Binary attention trees for caching partial products and retrieving them
   - Minkowski sums in attention heads for computing pairwise digit products
   - Fourier basis representations forming pentagonal prism geometry

3. **Scaling Alone Is Insufficient**  
   A 12-layer SFT model fails identically to a 2-layer model, achieving < 1% accuracy. The problem is not capacity but optimization - models converge to local optima lacking the right structure.

4. **Implicit Chain-of-Thought Provides Crucial Inductive Bias**  
   By gradually removing explicit intermediate steps, ICoT guides the model to internalize reasoning procedures in latent states, enabling discovery of appropriate computational mechanisms.

5. **Simple Inductive Biases Can Overcome Limitations**  
   Adding an auxiliary loss to predict running sums ĉk (via lightweight linear probes) provides enough inductive bias for a standard model to achieve 99% accuracy without any explicit chain-of-thought supervision.

### Implications for Transformer Design

- **Optimization Challenges:** Standard training procedures may fail on tasks requiring complex structural solutions, even when the model has sufficient capacity
- **Importance of Inductive Biases:** Task-specific or generic biases that encourage discovery of computational structures are critical  
- **Mechanistic Interpretability Value:** Reverse-engineering successful models reveals what unsuccessful models lack, pointing toward solutions
- **Attention Pattern Structure:** Tree-like information flow patterns may be important for multi-step reasoning tasks

### Implications for AI Capabilities

- **Reasoning Limitations:** Language models' failures on simple arithmetic suggest fundamental challenges with multi-step algorithmic reasoning
- **Process Supervision:** Providing supervision on intermediate steps (explicit or implicit) appears necessary for learning complex reasoning procedures  
- **Geometric Representations:** Efficient mathematical structures (Fourier bases, Minkowski sums) emerge when models successfully learn algorithmic tasks
- **Path to Improvement:** Understanding failure modes mechanistically enables targeted solutions rather than brute-force scaling

### Broader Research Directions

This work demonstrates the value of **mechanistic reverse-engineering** as a research methodology: by carefully studying what works and what doesn't, we can identify specific computational requirements, understand optimization challenges, and design targeted interventions. Future work should explore whether similar pitfalls exist for other long-range dependency tasks and develop generic training improvements to address them.
