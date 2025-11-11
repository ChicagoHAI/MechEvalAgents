# IOI Circuit Analysis - Code Walkthrough

## Overview

This document provides a detailed walkthrough of the implementation used to identify the IOI circuit in GPT2-small.

## Setup and Initialization

### 1. Environment Configuration

```python
import os
os.chdir('/home/smallyan/critic_model_mechinterp')

# Check for GPU availability
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
```

**Purpose**: Set working directory and configure compute device. Using CUDA significantly speeds up model inference and activation caching.

### 2. Load Model

```python
from transformer_lens import HookedTransformer

model = HookedTransformer.from_pretrained('gpt2-small', device=device)
```

**Key Configuration**:
- `n_layers`: 12
- `n_heads`: 12  
- `d_model`: 768
- `d_head`: 64

**Why TransformerLens**: Provides easy access to activation caching and intervention capabilities needed for mechanistic interpretability.

### 3. Load Dataset

```python
from datasets import load_dataset

dataset = load_dataset("mib-bench/ioi")
ioi_data = dataset['train']
```

**Dataset Structure**:
- Each example has a `prompt`, `choices`, `answerKey`, and `metadata`
- Metadata includes `subject`, `indirect_object`, `object`, and `place`
- Multiple counterfactual variants provided for each example

## Data Processing

### 4. Position Identification

```python
def find_positions(prompt_idx):
    tokens_str = model.to_str_tokens(prompts[prompt_idx])
    s_name = s_names[prompt_idx]
    
    s1_pos = None
    s2_pos = None
    end_pos = len(tokens_str) - 1
    
    for i, token in enumerate(tokens_str):
        if s_name in token:
            if s1_pos is None:
                s1_pos = i
            else:
                s2_pos = i
                break
    
    return s1_pos, s2_pos, end_pos, tokens_str
```

**Purpose**: Locate critical positions in each sentence:
- **S1**: First subject mention (typically position 2)
- **S2**: Second subject mention (varies by sentence structure)
- **END**: Last token position (where model predicts next token)

**Challenge**: Names are tokenized differently, so we search for name substrings in tokens rather than exact matches.

### 5. Baseline Evaluation

```python
logits, cache = model.run_with_cache(tokens)

for i in range(len(prompts)):
    _, _, end_pos, _ = find_positions(i)
    end_logits = logits[i, end_pos, :]
    
    io_token = model.to_single_token(' ' + io_names[i])
    s_token = model.to_single_token(' ' + s_names[i])
    
    predicted_io = end_logits[io_token] > end_logits[s_token]
```

**Purpose**: Measure model's baseline performance by comparing logits for IO vs. Subject tokens.

**Result**: 94% accuracy demonstrates model has learned IOI behavior.

## Attention Pattern Analysis

### 6. Duplicate Token Head Detection

```python
duplicate_token_scores = np.zeros((n_layers, n_heads))

for i in range(len(prompts)):
    s1_pos, s2_pos, _, _ = find_positions(i)
    
    for layer in range(n_layers):
        attn_pattern = cache[f'blocks.{layer}.attn.hook_pattern'][i]
        
        for head in range(n_heads):
            attn_s2_to_s1 = attn_pattern[head, s2_pos, s1_pos].item()
            duplicate_token_scores[layer, head] += attn_s2_to_s1

duplicate_token_scores /= len(prompts)
```

**Mechanism**:
1. Access cached attention patterns from each head
2. Extract attention weight from S2 position to S1 position
3. Average across all examples
4. Higher scores indicate heads that specialize in duplicate token detection

**Top Result**: a3.h0 with 0.72 average attention from S2→S1

### 7. S-Inhibition Head Detection

```python
s_inhibition_scores = np.zeros((n_layers, n_heads))

for i in range(len(prompts)):
    s1_pos, s2_pos, end_pos, _ = find_positions(i)
    
    for layer in range(n_layers):
        attn_pattern = cache[f'blocks.{layer}.attn.hook_pattern'][i]
        
        for head in range(n_heads):
            attn_end_to_s2 = attn_pattern[head, end_pos, s2_pos].item()
            s_inhibition_scores[layer, head] += attn_end_to_s2

s_inhibition_scores /= len(prompts)
```

**Mechanism**:
1. Extract attention weight from END position to S2 position
2. These heads attend to the subject to inhibit it from being predicted
3. Works in conjunction with Name-Mover heads

**Top Result**: a8.h6 with 0.74 average attention from END→S2

### 8. Name-Mover Head Detection

```python
name_mover_scores = np.zeros((n_layers, n_heads))

for i in range(len(prompts)):
    tokens_str = model.to_str_tokens(prompts[i])
    s1_pos, s2_pos, end_pos, _ = find_positions(i)
    
    # Find IO position
    io_name = io_names[i]
    io_pos = None
    for j, token in enumerate(tokens_str):
        if io_name in token and j != s1_pos and j != s2_pos:
            io_pos = j
            break
    
    for layer in range(n_layers):
        attn_pattern = cache[f'blocks.{layer}.attn.hook_pattern'][i]
        
        for head in range(n_heads):
            attn_end_to_io = attn_pattern[head, end_pos, io_pos].item()
            name_mover_scores[layer, head] += attn_end_to_io

name_mover_scores /= len(prompts)
```

**Mechanism**:
1. First locate IO position (different from S1/S2)
2. Extract attention weight from END to IO
3. These heads copy the IO token to the output

**Top Result**: a9.h9 with 0.80 average attention from END→IO

## Circuit Selection

### 9. Head Selection Strategy

```python
# Select top heads from each category
duplicate_heads_to_include = [
    (layer, head) for _, layer, head in top_duplicate_heads[:3]
]

s_inhibition_heads_to_include = [
    (layer, head) for _, layer, head in top_s_inhibition_heads[:3]
]

name_mover_heads_to_include = [
    (layer, head) for _, layer, head in top_name_mover_heads[:4]
]

selected_heads = list(set(
    duplicate_heads_to_include +
    s_inhibition_heads_to_include +
    name_mover_heads_to_include
))
```

**Strategy**:
1. Start with top performers from each category
2. Remove duplicates (some heads rank high in multiple categories)
3. Calculate budget used so far

### 10. MLP Selection

```python
head_layers = sorted(set([layer for layer, _ in selected_heads]))

# Include MLPs from layers with selected heads plus supporting layers
selected_mlps = [0, 1]  # Early layers for feature extraction
selected_mlps.extend(head_layers)  # Layers with attention heads
selected_mlps.extend([2, 4, 5, 6])  # Middle layers for transformation

selected_mlps = sorted(set(selected_mlps))
```

**Rationale**:
- MLPs provide nonlinear transformations essential for circuit computation
- Include early layers for basic feature extraction
- Include layers with selected heads for local computation
- Include middle layers for feature transformation

### 11. Budget Maximization

```python
remaining_budget = 11200 - (len(selected_heads) * 64 + len(selected_mlps) * 768)
max_additional_heads = remaining_budget // 64

# Combine and sort all candidates
all_important_heads = []
for score, layer, head in top_duplicate_heads[:15]:
    if (layer, head) not in selected_heads:
        all_important_heads.append((score, layer, head, 'duplicate'))
# ... repeat for other categories

all_important_heads.sort(reverse=True)

# Add top additional heads
for i in range(max_additional_heads):
    score, layer, head, category = all_important_heads[i]
    selected_heads.append((layer, head))
```

**Purpose**: Maximize circuit expressiveness by using all available budget.

**Result**: Added 21 additional heads, achieving exact 11,200-dimension budget usage.

## Validation and Output

### 12. Constraint Validation

```python
# Validate all nodes are in src_nodes
for node in circuit_nodes:
    if node not in src_nodes:
        invalid_nodes.append(node)

# Validate naming convention
if node.startswith('a'):
    # Check format: a{layer}.h{head}
    parts = node.split('.')
    # Validation logic...

# Validate budget
total_budget = len(selected_heads) * 64 + len(selected_mlps) * 768
assert total_budget <= 11200
```

**Checks**:
1. All nodes exist in allowed source nodes
2. Naming follows convention (a{layer}.h{head}, m{layer})
3. Total write budget ≤ 11,200 dimensions

### 13. Save Circuit

```python
circuit_data = {
    "nodes": circuit_nodes
}

with open('real_circuits_1.json', 'w') as f:
    json.dump(circuit_data, f, indent=2)
```

**Output Format**: JSON with single "nodes" key containing ordered list of node names.

## Key Implementation Details

### Attention Pattern Caching

TransformerLens's `run_with_cache` stores all intermediate activations:
- `cache['blocks.{layer}.attn.hook_pattern']`: Attention probabilities after softmax
- Shape: `[batch, n_heads, seq_len_q, seq_len_k]`
- Values range [0, 1] and sum to 1 over key dimension

### Averaging Across Examples

We average attention scores across examples to find heads with consistent behavior:
- Consistent high attention → specialized functionality
- Inconsistent attention → general-purpose or context-dependent

### Budget Calculation

```
Head budget = n_heads × (d_model / n_heads_per_layer)
            = 31 × 64 = 1,984

MLP budget = n_mlps × d_model  
           = 12 × 768 = 9,216

Total = 1,984 + 9,216 = 11,200 ✓
```

## Performance Considerations

### GPU Acceleration
- Model and data moved to CUDA
- Batch processing of 100 examples
- Activation caching done in single forward pass

### Memory Management
- Used subset of 100 examples (vs. full 10,000)
- Cached activations for all layers at once
- Total memory usage: ~2-3 GB GPU RAM

### Computational Complexity
- Forward pass: O(batch_size × seq_len²)
- Attention analysis: O(n_layers × n_heads × n_examples)
- Total runtime: ~2-3 minutes on A100

## Reproducibility

### Random Seeds
No random operations used - results are fully deterministic given:
1. Model weights (GPT2-small from Hugging Face)
2. Dataset (mib-bench/ioi)
3. Sample indices (first 100 examples)

### Dependencies
- `transformer_lens`: For model loading and activation caching
- `datasets`: For loading IOI dataset
- `torch`: For GPU computation
- `numpy`: For numerical operations

---

**Code Organization**:
- All analysis done in single Jupyter notebook
- Modular functions for position finding and scoring
- Clear separation of analysis phases (exploration → analysis → selection → validation)
