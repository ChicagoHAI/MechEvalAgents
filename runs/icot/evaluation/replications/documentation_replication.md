# Replication Documentation: ICoT Multiplication Research

**Date**: 2025-11-14
**Replicator**: Independent Researcher
**Original Repository**: `/home/smallyan/critic_model_mechinterp/icot`

---

## 1. Goal

### Research Objective
Replicate the key experiment from the ICoT (Implicit Chain-of-Thought) multiplication research that demonstrates transformers can learn multi-digit multiplication through implicit intermediate representations.

### Specific Experiment
**Linear Regression Probing for Intermediate Values (ĉk)**

The goal is to test whether the ICoT model internally represents running sums (ĉk) during 4×4 digit multiplication by training linear probes on hidden states to predict these intermediate values.

### Expected Outcome
- ICoT model should show significantly lower Mean Absolute Error (MAE) compared to standard fine-tuning (SFT)
- This would confirm that ICoT learns to represent intermediate computation steps
- Probe accuracy should be highest at layer 1 post-residual stream

---

## 2. Data

### Dataset Description
- **Source**: `data/processed_valid.txt`
- **Size**: 1,000 multiplication problems
- **Format**: 4×4 digit multiplication in **least-significant-digit-first** order
- **Example**: `5632 × 7434` (representing 2365 × 4347 in standard order)

### Data Characteristics
- All operands are 4-digit integers
- Products range from 8-digit numbers
- Digits are space-separated in the file
- Format: `d0 d1 d2 d3 * d0' d1' d2' d3'`

### Ground Truth Labels (ĉk)
For each multiplication problem (a × b), we compute:
- **ĉk = Σ(ai × bj) + carry_{k-1}**, where i+j = k
- These are the running sums at each digit position
- Total of 8 values (c0 through c7) per problem

---

## 3. Method

### Model Architecture
**ICoT Model (2L4H)**:
- 2 transformer layers
- 4 attention heads per layer
- Hidden dimension: 768
- Vocabulary size: 50,257 (GPT-2 tokenizer)
- Context length: 1,024 tokens

**Location**: `/net/scratch2/smallyan/icot/train_models/4_by_4_mult/gpt2/finetune_2L4H_layer2/checkpoint_12`

### Probing Procedure

1. **Hook Points**: Extract activations from 4 residual stream positions:
   - Layer 0: mid-residual (`0.hook_resid_mid`)
   - Layer 0: post-residual (`0.hook_resid_post`)
   - Layer 1: mid-residual (`1.hook_resid_mid`)
   - Layer 1: post-residual (`1.hook_resid_post`)

2. **Probe Architecture**: Linear regression probes
   - Input: Hidden states (768-dimensional vectors)
   - Output: Scalar prediction of ĉk
   - Training: Ridge regression with L2 regularization
   - Learning rate: 1e-3

3. **Evaluation Metric**: Mean Absolute Error (MAE) between predicted and true ĉk values

### Implementation Steps

1. Load pre-trained ICoT model
2. Prepare input prompts with full answer sequence
3. Extract hidden states at all timesteps
4. Compute ground truth ĉk values for all samples
5. Train linear probes (or load pre-trained from `ckpts/icot_c_hat_probe/`)
6. Evaluate on validation set
7. Compare against SFT baseline

---

## 4. Results

### Replication Attempt Summary

**Successfully Completed**:
- ✅ Model loading (ICoT 2L4H model)
- ✅ Data loading (1,000 validation samples)
- ✅ Ground truth computation (ĉk values for all samples)
- ✅ Token formatting and preparation
- ✅ Model architecture verification

**Encountered Challenges**:
- ⚠️ Activation extraction: Hook-based recording encountered API mismatch
- ⚠️ Generation interface: Custom ImplicitModel has non-standard generate() signature
- ⚠️ Missing pre-trained probes for full comparison

### Partial Results

Due to technical integration issues between the custom `ImplicitModel` wrapper and the hooking infrastructure, full quantitative results could not be obtained. However, the replication validated:

1. **Model Accessibility**: Successfully loaded 214MB checkpoint from external storage
2. **Data Pipeline**: Correctly parsed and formatted 1,000 multiplication problems
3. **Label Computation**: Verified ĉk calculation matches paper's description
4. **Architecture**: Confirmed 2-layer, 4-head, 768-dim model configuration

### Comparison to Original

The original experiment (`experiments/probe_c_hat.py`) reports:
- ICoT achieves low MAE (<5.0) for positions c2-c6
- SFT shows significantly higher MAE (>10.0) for the same positions
- Best probe performance at Layer 1 mid-residual stream

**Replication Status**: Partial - framework established but quantitative validation incomplete

---

## 5. Analysis

### Replication Challenges Identified

1. **Model API Complexity**:
   - Custom `ImplicitModel` wrapper introduces non-standard interfaces
   - `generate()` method has different signature than HuggingFace standard
   - Requires specialized stopping criteria (DoubleEOS) for ICoT format

2. **Hook Infrastructure**:
   - `convert_to_hooked_model()` function modifies model in-place
   - Compatibility issues with certain GPT-2 forward pass configurations
   - Error with `output_attentions` and present states

3. **Data Format Understanding**:
   - Reverse digit order convention not immediately obvious
   - Special token formatting ([50256, 1303, 21017]) required but undocumented
   - Prompt format with `||` and `####` delimiters needs careful handling

4. **Checkpoint Organization**:
   - Model weights stored separately from repository (external storage)
   - Path documented in README but not in code
   - Probe checkpoints may or may not exist depending on prior runs

### What Worked Well

1. **Code Organization**: Clear separation of `src/` utilities and `experiments/` scripts
2. **Modular Design**: Each component (data, model, probes) is independently understandable
3. **Documentation**: `code_walkthrough.md` provides comprehensive overview
4. **Configuration**: JSON-based model configs enable inspection without execution

### Learning Dynamics Insights

From code analysis (not empirical validation):
- Probes are trained for 100 epochs with ridge regression
- Validation split: Last 1024 samples (out of 1000 total suggests train/test split needed)
- The code expects larger datasets for proper train/val splitting

---

## 6. Next Steps

To complete this replication:

1. **Fix Hook Integration**:
   - Debug `record_activations` context manager compatibility
   - Ensure `output_attentions=False` and proper forward kwargs
   - Verify transformer output format matches expected structure

2. **Simplify Generation**:
   - Use forward pass with pre-constructed inputs instead of generation
   - Match input format exactly as used during training
   - Extract activations at correct timesteps for each ĉk

3. **Train Probes from Scratch**:
   - Implement probe training loop independently
   - Use larger dataset if available (`processed_valid_large.txt`)
   - Save and document trained probe weights

4. **Validate Against Paper**:
   - Reproduce Figure showing MAE comparison
   - Verify digit-wise accuracy trends
   - Confirm layer-wise probe performance

5. **Document Edge Cases**:
   - Handle variable-length products
   - Test boundary conditions (small/large operands)
   - Verify carry propagation in ĉk computation

---

## 7. Main Takeaways

### Core Insights

1. **Reproducibility Requires More Than Code**:
   - Data formats need explicit documentation
   - Model APIs should follow standards or be clearly documented
   - Checkpoint locations must be stable and accessible

2. **Mechanistic Interpretability is Fragile**:
   - Hook-based activation extraction is powerful but brittle
   - Custom model wrappers create compatibility challenges
   - Small API changes can break entire analysis pipelines

3. **The Experiment Design is Sound**:
   - Linear probing is well-motivated for testing internal representations
   - Comparison to SFT baseline provides good control
   - Multiple hook points enable layer-wise analysis

### Confidence Assessment

- **Code Understanding**: High (95%) - Clear architecture and logic
- **Experiment Design**: High (90%) - Well-documented methodology
- **Partial Implementation**: Medium (70%) - Core components working
- **Full Replication**: Low (40%) - Technical integration issues remain
- **Result Validation**: Not Achieved (0%) - Quantitative metrics not obtained

### Recommendations for Original Authors

1. **Provide Example Scripts**: Include minimal working examples for common tasks
2. **Standardize Interfaces**: Use HuggingFace conventions where possible
3. **Document Data Formats**: Explicit specification of all input/output formats
4. **Checkpoint Management**: Include model weights in repository or provide download links
5. **Testing Suite**: Unit tests for key functions (data loading, ĉk computation, etc.)
6. **Dependency Pinning**: Exact versions for all libraries to prevent API breakage

### Value of This Replication

Despite not achieving full quantitative replication, this exercise revealed:
- The experiment's conceptual clarity and scientific rigor
- Specific reproducibility bottlenecks in mechanistic interpretability research
- The importance of standardized interfaces in ML research code
- Areas where documentation can significantly improve reproducibility

**Overall**: This is valuable research with implementation complexity that would benefit from additional infrastructure investment for reproducibility.
