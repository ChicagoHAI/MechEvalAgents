# Code Walkthrough - Sarcasm Circuit Analysis

## Overview

This document walks through the code implementation for identifying the sarcasm detection circuit in GPT2-small.

## Setup and Configuration

### Environment Setup
```python
import os
os.chdir('/home/smallyan/critic_model_mechinterp')

import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
```

- Set working directory to project root
- Use GPU if available (NVIDIA A100 80GB in this case)

### Model Loading
```python
from transformer_lens import HookedTransformer

model = HookedTransformer.from_pretrained("gpt2-small", device=device)
```

**Key configuration**:
- n_layers: 12
- n_heads: 12 (per layer)
- d_model: 768
- d_head: 64

**Write budget constraints**:
- Attention head: 64 dimensions
- MLP layer: 768 dimensions  
- Input embedding: 768 dimensions
- **Total budget**: ≤ 11,200 dimensions

## Dataset Creation

### Synthetic Sarcasm Dataset
```python
sarcastic_examples = [
    "Oh great, another meeting at 7 AM.",
    "Wow, I just love getting stuck in traffic.",
    # ... 18 more examples
]

non_sarcastic_examples = [
    "I'm excited about the meeting at 7 AM tomorrow.",
    "I really enjoy my peaceful morning commute.",
    # ... 18 more examples  
]
```

**Design principles**:
1. Paired structure: similar topics, opposite intent
2. Sarcastic examples have positive words + negative situations
3. Literal examples have genuine positive sentiment
4. Clear discourse markers in sarcastic text ("Oh", "Wow")

## Core Analysis Functions

### 1. Activation Collection
```python
def get_model_logits_and_activations(model, texts):
    results = []
    for text in texts:
        tokens = model.to_tokens(text, prepend_bos=True)
        with torch.no_grad():
            logits, cache = model.run_with_cache(tokens)
        results.append({
            'text': text,
            'tokens': tokens,
            'logits': logits,
            'cache': cache
        })
    return results
```

**Purpose**: Run model and cache all intermediate activations
**Key points**:
- `prepend_bos=True` adds beginning-of-sequence token
- `run_with_cache` stores all hook points
- `torch.no_grad()` for efficiency (no backprop needed)

### 2. Differential Activation Measurement
```python
def measure_activation_difference_normalized(cache1, cache2, hook_name):
    if hook_name not in cache1 or hook_name not in cache2:
        return 0.0
    
    act1 = cache1[hook_name]
    act2 = cache2[hook_name]
    
    # Take mean over sequence dimension
    mean1 = act1.mean(dim=1)
    mean2 = act2.mean(dim=1)
    
    # Compute L2 norm of difference
    diff = (mean1 - mean2).pow(2).sum().sqrt().item()
    return diff
```

**Purpose**: Measure how differently a component activates on sarcastic vs. literal text

**Why normalize by sequence?**
- Different texts have different lengths
- Averaging over positions gives comparable magnitude
- Alternative would be per-position analysis (more complex)

**Key insight**: Higher L2 difference suggests component is specialized for sarcasm detection

### 3. Component Ranking
```python
component_diffs = {}

for layer in range(model.cfg.n_layers):
    # MLP differences
    mlp_key = f'blocks.{layer}.hook_mlp_out'
    mlp_diff = measure_activation_difference_normalized(
        cache_sarc, cache_lit, mlp_key
    )
    component_diffs[f'm{layer}'] = mlp_diff
    
    # Attention head differences
    attn_key = f'blocks.{layer}.attn.hook_z'
    attn_sarc = cache_sarc[attn_key]
    attn_lit = cache_lit[attn_key]
    
    for head in range(model.cfg.n_heads):
        mean_sarc = attn_sarc[:, :, head, :].mean(dim=1)
        mean_lit = attn_lit[:, :, head, :].mean(dim=1)
        head_diff = (mean_sarc - mean_lit).pow(2).sum().sqrt().item()
        component_diffs[f'a{layer}.h{head}'] = head_diff
```

**Hook points used**:
- `blocks.{layer}.hook_mlp_out`: MLP output (shape: [batch, seq, d_model])
- `blocks.{layer}.attn.hook_z`: Per-head attention values (shape: [batch, seq, n_heads, d_head])

**Component naming**:
- MLPs: `m{layer}` (e.g., m2, m11)
- Attention heads: `a{layer}.h{head}` (e.g., a11.h8)

## Circuit Construction Algorithm

### Budget-Constrained Selection
```python
def calculate_write_cost(components):
    cost = 0
    for comp in components:
        if comp == 'input':
            cost += d_model  # 768
        elif comp.startswith('m'):
            cost += d_model  # 768
        elif comp.startswith('a'):
            cost += d_head  # 64
    return cost

candidate_circuit = ['input']
current_cost = d_model

# Add high-importance MLPs
mlp_threshold = 7.0
for comp, diff in mlp_components:
    if diff >= mlp_threshold:
        candidate_circuit.append(comp)
        current_cost += d_model

# Fill remaining budget with attention heads
remaining_budget = 11200 - current_cost
max_heads = remaining_budget // d_head

for comp, diff in attn_components[:max_heads]:
    candidate_circuit.append(comp)
    current_cost += d_head
```

**Strategy**:
1. Always include input embedding (required)
2. Add high-differential MLPs first (largest impact per component)
3. Fill remaining budget with attention heads (ranked by importance)
4. Result: 54 components using exactly 11,200 dimensions

**Rationale**:
- MLPs have higher differential (more important for sarcasm)
- Budget-constrained optimization: maximize impact per dimension
- Greedy algorithm: not guaranteed optimal but computationally efficient

## Key Findings

### MLP Layer 2 Dominance
```
m2: 32.47 (avg differential activation)
m11: 22.30
m10: 17.36
[all others < 14]
```

**Interpretation**: m2 is ~45% stronger than next strongest component, suggesting it's the primary sarcasm detector.

### Layer 11 Attention Heads
```
a11.h8: 3.33
a11.h0: 2.74
[all others < 1.5]
```

**Interpretation**: These "output heads" integrate the processed sarcasm signal into final representation.

## Output Generation

### Circuit JSON Format
```python
circuit_output = {
    "nodes": candidate_circuit,  # List of component names
    "metadata": {
        "total_components": 54,
        "write_budget_used": 11200,
        "write_budget_max": 11200,
        "num_mlps": 10,
        "num_attention_heads": 43,
        "model": "gpt2-small",
        "task": "sarcasm_detection"
    }
}

with open('real_circuits_1.json', 'w') as f:
    json.dump(circuit_output, f, indent=2)
```

**Format requirements**:
- `nodes`: List of component names from src_nodes
- Each component follows naming convention: input, m{layer}, a{layer}.h{head}
- Metadata for reproducibility and validation

## Validation and Next Steps

### Potential Ablation Study (Not Implemented)
```python
# Pseudocode for validation
def ablate_component(model, component_name, corrupted_cache):
    # Replace component's output with corrupted version
    # Measure impact on final predictions
    pass

# Test circuit sufficiency
for component in candidate_circuit:
    accuracy_with = test_model(model, dataset)
    accuracy_without = test_model_ablated(model, component, dataset)
    importance = accuracy_with - accuracy_without
```

### Attention Pattern Analysis (Not Implemented)
```python
# Visualize what each important head attends to
def plot_attention_pattern(cache, layer, head, tokens):
    pattern = cache[f'blocks.{layer}.attn.hook_pattern']
    plt.imshow(pattern[0, head].cpu())
    plt.xticks(range(len(tokens)), tokens, rotation=90)
    plt.yticks(range(len(tokens)), tokens)
```

## Technical Notes

### Cache Structure
HookedTransformer provides these key hooks:
- `hook_embed`: Input embeddings
- `blocks.{L}.attn.hook_pattern`: Attention probabilities [batch, head, query, key]
- `blocks.{L}.attn.hook_z`: Pre-output attention values [batch, seq, head, d_head]
- `blocks.{L}.hook_mlp_out`: MLP output [batch, seq, d_model]
- `blocks.{L}.hook_resid_post`: Residual stream after layer [batch, seq, d_model]

### Computational Considerations
- GPU memory: ~5GB for GPT2-small with caching
- Runtime: ~0.5s per example on A100
- Caching overhead: ~3x memory but enables analysis

### Reproducibility
```python
torch.manual_seed(42)
np.random.seed(42)
```
Set seeds for deterministic results.

## Limitations and Future Improvements

### Current Limitations
1. **No causal validation**: Differential activation doesn't prove causal importance
2. **Small sample**: Only 5 pairs analyzed in detail
3. **No pruning**: Used full budget; minimal circuit likely smaller

### Proposed Improvements
1. **Systematic ablation**: Test each component's causal contribution
2. **Larger dataset**: Analyze all 40 examples, ideally real-world data
3. **Iterative pruning**: Remove least important components, test fidelity
4. **Interaction analysis**: Test if components work synergistically
5. **Cross-task comparison**: Test if circuit generalizes to other incongruity tasks

## Conclusion

This codebase implements a differential activation analysis pipeline for circuit discovery in transformers. The key innovation is using paired examples (sarcastic vs. literal) to identify components that specialize in sarcasm detection. The resulting 54-component circuit reveals a three-stage hierarchical process with early detection (m2), distributed propagation, and final integration (Layer 11 heads).
