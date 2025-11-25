# Code Walkthrough: ICoT Multiplication Reverse-Engineering

## Overview

This repository contains code for reverse-engineering Implicit Chain-of-Thought (ICoT) models that successfully learn multi-digit multiplication. The codebase enables training, analysis, and mechanistic interpretability of transformer models on 4×4 digit multiplication tasks.

**Repository Structure:**
- `src/` — Backend source code for experiments and model infrastructure
- `experiments/` — Scripts to reproduce all paper results and figures
- `data/` — Datasets used in experiments (validation sets)
- `paper_figures/` — Generated figures from experiment scripts
- `ckpts/` — Model checkpoints and trained probe weights

## Setup and Installation

### Prerequisites
```bash
# Core dependencies (inferred from code)
pip install torch transformers
pip install fancy_einsum einops
pip install numpy pandas matplotlib plotly
pip install scikit-learn tqdm
```

### Repository Structure
```
icot/
├── src/                       # Core library code
│   ├── ActivationCache.py    # Activation recording utilities
│   ├── HookedModel.py        # Hooked transformer for interpretability
│   ├── ImplicitModel.py      # ICoT model wrapper
│   ├── Intervention.py       # Activation patching/intervention tools
│   ├── data_utils.py         # Data formatting and processing
│   ├── model_utils.py        # Model loading utilities
│   ├── probes.py             # Linear regression probes
│   └── transformer.py        # Custom transformer implementation
│
├── experiments/               # Reproducibility scripts
│   ├── fourier_figure.py     # Generate Fourier basis visualizations
│   ├── fourier_r2_fits.py    # Compute R² fits for Fourier bases
│   ├── fractals_and_minkowski.py  # Minkowski sum visualizations
│   ├── grad_norms_and_losses.py   # Training dynamics analysis
│   ├── long_range_logit_attrib.py # Logit attribution experiments
│   └── probe_c_hat.py        # Linear probing for running sums
│
├── data/                      # Datasets
│   ├── processed_valid.txt   # Validation set (1,000 samples)
│   └── processed_valid_large.txt  # Extended validation set
│
├── ckpts/                     # Model checkpoints
│   ├── 2L4H/                  # ICoT 2-layer 4-head model
│   ├── aux_head/              # Auxiliary loss model checkpoints
│   ├── vanilla_ft/            # Standard fine-tuning model
│   ├── icot_c_hat_probe/      # Trained ĉ probes for ICoT
│   └── sft_c_hat_probe/       # Trained ĉ probes for SFT
│
├── paper_figures/             # Generated visualizations
├── constants.py               # Path constants (BASE_DIR)
└── README                     # Basic repository overview
```

## Data Pipeline

### Data Format

The multiplication data uses a specific format with operands in **least-significant-digit-first** order:

**Input Format:**
```
a0a1a2a3 * b0b1b2b3
```
For example, to compute 8331 × 5015, the input is: `1338 * 5105`

**ICoT Format with Chain-of-Thought:**
```
1338 * 5105||5614 + 013380(569421) + 0000000(5694210) + 0005561%%####56997714
```

**Components:**
- `||` — Separator after operands
- `5614` — First partial product (1338 × 5)
- `013380(569421)` — Second partial product and running sum
- `%%####` — Delimiters before final answer
- `56997714` — Final product (in reverse digit order)

### Key Data Functions (data_utils.py:326 lines)

1. **`format_tokens(tokens)`**  
   Adds special delimiter values [50256, 1303, 21017] to tokenized inputs

2. **`read_operands(file_path)`**  
   Reads multiplication problems from text files

3. **`prompt_ci_raw_format_batch(operands, tokenizer)`**  
   Formats batches of operands into model input format

4. **`get_ci(a, b, i)`**  
   Computes the i-th digit of the product of two numbers

5. **`extract_answer(output_text)`**  
   Extracts predicted digits from model output

## Model Architecture

### Core Components

#### 1. Custom Transformer (transformer.py:354 lines)

**TransformerConfig:**
```python
@dataclass
class TransformerConfig:
    D: int = 768           # Hidden dimension
    n_layers: int = 2      # Number of layers
    n_heads: int = 4       # Number of attention heads
    n_vocab: int = 50257   # Vocabulary size
    ctx_len: int = 512     # Context length
    device: str = "cuda"
```

**Key Classes:**
- `Attention` — Multi-head self-attention with causal masking
- `MLP` — Feed-forward network with activation functions
- `TransformerBlock` — Layer = Attention + MLP with residual connections  
- `Transformer` — Full model = Embedding + N×TransformerBlock + Unembedding

**Key Feature:** Implements hook points for interpretability

#### 2. Hooked Model (HookedModel.py:286 lines)

Extends GPT2 models with interpretability hooks for:
- Recording activations at any layer/component
- Intervening on activations during forward pass
- Extracting attention patterns

**`convert_to_hooked_model(model)`**  
Converts a standard GPT2 model to support hooks by replacing attention forward method

#### 3. ICoT Model Wrapper (ImplicitModel.py:264 lines)

**ImplicitModel class:**
- Wraps GPT2LMHeadModel for ICoT training
- Handles separator token positioning
- Implements custom generation logic

**Key Functions:**
- `get_sep_position(input_ids, sep_id)` — Finds delimiter positions
- `forward()` — Custom forward pass with loss computation

### Model Loading (model_utils.py:162 lines)

**`load_hf_model(config_path, state_dict_path)`**
- Loads model from config JSON and state dict
- Returns hooked model + tokenizer
- Handles state dict key processing

**`load_c_hat_model(path, type="icot")`**  
- Loads models trained with auxiliary ĉ loss
- Returns model and probe weights

## Experiment Pipeline

### 1. Logit Attribution (long_range_logit_attrib.py:178 lines)

**Purpose:** Measure how input digit perturbations affect output logits

**Procedure:**
1. Generate original input: `a0a1a2a3 * b0b1b2b3`
2. Record baseline logits for each output digit ck
3. For each input position t, create counterfactual by swapping digit
4. Compute Δt,k = logit_ck(original) - logit_ck(counterfactual)
5. Aggregate over 1,000 samples per (t,k) pair

**Output:** Heatmaps showing which input digits affect which output digits

### 2. Linear Regression Probing (probe_c_hat.py:222 lines)

**Purpose:** Test if intermediate value ĉk can be decoded from hidden states

**Procedure:**
1. Define probe hook points: layer 0/1 residual stream (mid/post)
2. Extract hidden states h²ᵐⁱᵈ at timestep tck
3. Train linear probe: wk · h²ᵐⁱᵈ = ĉk (MSE loss)
4. Evaluate MAE on held-out validation set

**Probe Training:**
```python
probe = RegressionProbe(shape=(d,), lr=1e-3, use_ridge=True)
probe.train_step(hidden_states, target_c_hat)
```

### 3. Fourier Basis Analysis (fourier_r2_fits.py:169 lines)

**Purpose:** Quantify how well Fourier bases explain model representations

**Fourier Basis Matrix F:**
```python
Φ(n) = [1, cos(2πn/10), sin(2πn/10), cos(2πn/5), sin(2πn/5), (-1)^n]
```

**R² Computation:**
1. Extract vectors x ∈ ℝ¹⁰ (over digits 0-9) from embeddings/weights/activations
2. Fit: C = argmin_C ||x - FC||²
3. Compute: R² = 1 - ||x - FC||² / ||x - mean(x)||²
4. Report median R² over all vectors

**Analyzed Components:**
- Token embeddings E
- MLP output weights W_out
- Final hidden states h^L

### 4. Attention Pattern Visualization (fractals_and_minkowski.py:440 lines)

**Purpose:** Visualize attention trees and Minkowski sum structures

**Attention Tree Reconstruction:**
1. Record attention patterns for all heads/layers
2. For each output digit ck, identify which timesteps are attended to
3. Trace back through layers to find cached partial products
4. Visualize as directed graph showing information flow

**Minkowski Sum Analysis:**
1. Extract attention head outputs ATT^ℓ_h
2. Apply 3D PCA
3. Color points by ai (global) and bj (local) to reveal nested structure

### 5. Training Dynamics Analysis (grad_norms_and_losses.py:334 lines)

**Purpose:** Understand why SFT fails by tracking learning progression

**Tracked Metrics:**
- Gradient norms per output token (c0-c7)
- Loss per output token over training steps
- Overall model loss and accuracy

**Visualization:**
- Heatmap of gradient norms over time
- Line plots of per-token loss curves
- Identifies which digits are learned when

## Running Experiments

### Reproduce Paper Figures

Each experiment script is self-contained and outputs visualizations to `paper_figures/`.

**1. Logit Attribution Heatmap:**
```bash
python experiments/long_range_logit_attrib.py
```
Generates comparison between ICoT and SFT models showing long-range dependencies.

**2. Linear Probe Accuracy:**
```bash
python experiments/probe_c_hat.py
```
Trains and evaluates probes for ĉ2 through ĉ6, outputs MAE plots.

**3. Fourier Basis Fits:**
```bash
python experiments/fourier_r2_fits.py
```
Computes R² statistics for embeddings, weights, and activations.

**4. 3D PCA Visualizations:**
```bash
python experiments/fourier_figure.py
```
Generates pentagonal prism and Fourier basis structure plots.

**5. Minkowski Sum Fractals:**
```bash
python experiments/fractals_and_minkowski.py
```
Creates nested representation visualizations for attention heads.

**6. Training Dynamics:**
```bash
python experiments/grad_norms_and_losses.py --model_type sft
python experiments/grad_norms_and_losses.py --model_type aux
```
Analyzes gradient norms and losses during training (requires logged training data in ckpts/).

### Model Checkpoints

**ICoT Model (2L4H):**
```python
from src.model_utils import load_hf_model
config_path = "ckpts/2L4H/config.json"
state_dict_path = "ckpts/2L4H/state_dict.bin"
model, tokenizer = load_hf_model(config_path, state_dict_path)
```

**Auxiliary Loss Model:**
```python
from src.model_utils import load_c_hat_model  
model, probes = load_c_hat_model("ckpts/aux_head/", type="aux")
```

## Key Functions and Classes

### Activation Recording (ActivationCache.py:156 lines)

**`ActivationCache` class:**
- Dictionary-like container for recorded activations
- Maps component names (e.g., "0.hook_resid_mid") to tensors

**`record_activations(model, input, modules)` context manager:**
```python
with record_activations(model, input_ids, ["1.hook_resid_mid"]) as cache:
    output = model(input_ids)
    activations = cache["1.hook_resid_mid"]  # Shape: [batch, seq, hidden]
```

### Intervention Tools (Intervention.py:256 lines)

**Activation Patching:**
```python
from src.Intervention import patch_activations

# Replace activations from source in target at specific component
with patch_activations(target_model, source_cache, components):
    output = target_model(input_ids)
```

**Supported Operations:**
- Patching: Replace activations from another forward pass
- Ablation: Zero out specific components
- Custom interventions: Apply arbitrary transformations

### Probe Training (probes.py:171 lines)

**RegressionProbe class:**
```python
probe = RegressionProbe(
    shape=(hidden_dim,),      # Probe weight shape
    lr=1e-3,                  # Learning rate
    ridge_alpha=0.01,         # L2 regularization
    use_ridge=True
)

# Training loop
for batch in dataloader:
    loss = probe.train_step(hidden_states, targets)
    
# Inference
predictions = probe.predict(hidden_states)
```

## Reproducibility

### Seeds and Determinism
The codebase uses random seeds for reproducibility:
```python
import random
random.seed(99)  # Used in several experiment scripts
```

### Configuration Files
Model configurations are stored as JSON:
```json
{
  "vocab_size": 50257,
  "n_positions": 512,
  "n_embd": 768,
  "n_layer": 2,
  "n_head": 4,
  ...
}
```

### Data Processing
All experiments use the same validation sets:
- `data/processed_valid.txt` — 1,000 samples
- `data/processed_valid_large.txt` — 5,000 samples

### Hardware Requirements
- **GPU:** CUDA-capable GPU recommended (experiments use cuda)
- **Memory:** ~8GB GPU memory for 2L4H model
- **Storage:** ~3GB for checkpoints and figures

## Usage Examples

### Example 1: Load Model and Generate

```python
from src.model_utils import load_hf_model
from src.data_utils import prompt_ci_raw_format_batch

# Load model
config_path = "ckpts/2L4H/config.json"
state_dict_path = "ckpts/2L4H/state_dict.bin"  
model, tokenizer = load_hf_model(config_path, state_dict_path)
model.to("cuda")

# Prepare input
operands = [("1338", "5105")]  # 8331 × 5015 in reverse
inputs = prompt_ci_raw_format_batch(operands, tokenizer)

# Generate
outputs = model.generate(inputs["input_ids"].to("cuda"), max_length=50)
print(tokenizer.decode(outputs[0]))
```

### Example 2: Record and Visualize Attention

```python
from src.HookedModel import convert_to_hooked_model
from src.ActivationCache import record_activations
import matplotlib.pyplot as plt

# Convert to hooked model
convert_to_hooked_model(model)

# Record attention patterns
with record_activations(model, inputs["input_ids"], ["1.attn.hook_pattern"]) as cache:
    _ = model(inputs["input_ids"].to("cuda"))
    attn_pattern = cache["1.attn.hook_pattern"]  # [batch, heads, seq, seq]

# Visualize
plt.imshow(attn_pattern[0, 0].cpu(), cmap="Blues")
plt.title("Layer 1 Head 0 Attention")
plt.show()
```

### Example 3: Train a Probe

```python
from src.probes import RegressionProbe
from src.data_utils import read_operands, get_ci

# Load training data
operands = read_operands("data/processed_valid.txt")

# Extract hidden states (pseudo-code)
hidden_states = []  # Shape: [N, hidden_dim]
targets = []        # Target ĉ values

for a, b in operands:
    # Compute target ĉ_k
    c_hat = sum([int(a[i])*int(b[j]) for i+j <= k]) + carry
    targets.append(c_hat)
    
    # Record hidden state at timestep t_ck
    with record_activations(model, ...) as cache:
        h = cache["1.hook_resid_mid"][..., timestep_ck, :]
        hidden_states.append(h)

# Train probe
probe = RegressionProbe(shape=(768,), lr=1e-3)
for epoch in range(100):
    loss = probe.train_step(
        torch.stack(hidden_states),
        torch.tensor(targets)
    )
    print(f"Epoch {epoch}: Loss = {loss:.4f}")
```

## Code Organization Best Practices

The codebase follows these organizational principles:

1. **Separation of Concerns:**
   - `src/` contains reusable library code
   - `experiments/` contains one-off analysis scripts

2. **Modular Design:**
   - Each source file has a single clear purpose
   - Functions are composable and reusable

3. **Interpretability First:**
   - Hook points everywhere for activation access
   - Caching and intervention utilities built-in

4. **Reproducibility:**
   - Fixed random seeds
   - Saved checkpoints for all models
   - Self-contained experiment scripts

## Extending the Codebase

### Adding New Experiments

1. Create new script in `experiments/`
2. Import from `src/` libraries
3. Load models using `src.model_utils`
4. Use `ActivationCache` for recording
5. Save figures to `paper_figures/`

### Training New Models

1. Define model config in `ckpts/new_model/config.json`
2. Implement training loop using `ImplicitModel`
3. Save state dict to `ckpts/new_model/state_dict.bin`
4. Update `model_utils.py` with loading function if needed

### Adding New Probes

1. Extend `RegressionProbe` class in `probes.py`
2. Implement custom `forward()` and `loss()` methods
3. Add training script to `experiments/`

## Common Issues and Solutions

**Issue: CUDA out of memory**
- Reduce batch size in experiment scripts
- Use smaller validation set

**Issue: Missing checkpoints**
- Download from repository or train models
- Verify paths in `constants.py`

**Issue: Import errors**
- Ensure PYTHONPATH includes repository root
- Install all dependencies

**Issue: Different results**
- Check random seed settings
- Verify model checkpoint matches expected version

## Summary

This codebase provides a complete pipeline for:
1. **Training** ICoT and SFT models on multi-digit multiplication
2. **Analyzing** learned mechanisms through interpretability tools  
3. **Reproducing** all experiments and figures from the paper
4. **Extending** with new experiments and analyses

The modular design separates core functionality (`src/`) from experiments, making it easy to adapt for new research questions while maintaining reproducibility.
