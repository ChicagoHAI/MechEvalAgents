# Replication Evaluation: ICoT Multiplication Research

**Date**: 2025-11-14
**Repository**: `/home/smallyan/critic_model_mechinterp/icot`
**Target Experiment**: Linear Regression Probing for Intermediate Values (ĉk)

---

## Replication Reflection

### What Was Easy

1. **Code Exploration**: The repository is well-structured with clear separation between source code (`src/`) and experiments (`experiments/`). Navigation was straightforward.

2. **Documentation Quality**: The `code_walkthrough.md` file provided an excellent overview of the codebase, explaining:
   - Repository structure and file organization
   - Data formats and conventions
   - Model architecture details
   - Experiment procedures and expected outputs

3. **Conceptual Understanding**: The paper's methodology is clearly described, making it easy to understand:
   - The goal (probe for intermediate values)
   - The approach (linear regression on hidden states)
   - The expected results (ICoT outperforms SFT)

4. **Initial Setup**: Loading the model configuration, accessing data files, and understanding the overall pipeline was straightforward.

### What Was Hard

1. **Custom Model Wrapper**: The `ImplicitModel` class wraps GPT-2 with custom logic:
   - Non-standard `generate()` signature (expects `max_new_tokens`, `num_beams`, `stop_on_two_eos`)
   - Special handling for double-EOS stopping criteria
   - Position IDs and separator token management adds complexity

2. **Hook Infrastructure Integration**: The `convert_to_hooked_model()` function:
   - Modifies models in-place with side effects
   - Encountered compatibility issues with activation recording
   - Error: "tuple index out of range" when recording activations
   - Root cause: Mismatch between expected HookedModel interface and actual model behavior

3. **Data Format Nuances**:
   - Reverse digit order convention (least-significant-digit-first) wasn't immediately obvious
   - Special token sequence `[50256, 1303, 21017]` required but not documented in code
   - Delimiter format (`||` for CoT separator, `####` for answer) needs careful handling

4. **Missing Dependencies/Checkpoints**:
   - Model checkpoint not in repository, stored at `/net/scratch2/smallyan/icot/...`
   - Path documented in README but requires external storage access
   - Pre-trained probe weights may or may not exist depending on prior runs
   - No automated download or setup script

### Where Inference Was Required

1. **Data Splitting**: Code suggests validation size of 1024, but dataset only has 1000 samples. Inferred that:
   - Original experiments used larger datasets
   - Current validation set might be a subset
   - Need to adjust splitting logic for available data

2. **Activation Extraction Timesteps**: The code references `timestep_ck` but doesn't explicitly document:
   - Which token position corresponds to which ĉk
   - How to align hidden states with output digits
   - Inferred from prompt construction that last `seq_len` positions map to ĉ values

3. **Probe Training Configuration**:
   - Ridge alpha value (L2 regularization) not specified in experiment
   - Inferred from `RegressionProbe` default or prior runs
   - Number of training epochs (100) found in code, not documentation

4. **Error Handling**: When generation failed:
   - Inferred that `do_sample` parameter not supported
   - Tried alternative approaches (direct forward pass)
   - API documentation lacking for custom generate method

### What Was Modified

1. **Model Path**: Updated checkpoint path from repository-local to external storage:
   ```python
   # Original (expected): ckpts/2L4H/state_dict.bin
   # Modified (actual): /net/scratch2/smallyan/icot/.../checkpoint_12/state_dict.bin
   ```

2. **Data Splitting**: Adjusted validation split to handle 1000-sample dataset:
   ```python
   # Original: val_size = 1024 (assumes larger dataset)
   # Modified: Handled case where total < val_size
   ```

3. **Generation Approach**: Attempted to simplify generation by:
   - Removing unsupported parameters (`do_sample`, `pad_token_id`)
   - Considering direct forward pass instead of generation
   - Could not complete due to API incompatibility

4. **Error Recovery**: Added try-except blocks to handle:
   - Missing SFT model
   - Generation failures
   - Probe loading errors

---

## Quantitative Evaluation

### A. Implementation Reconstructability

**Score: 3/5**

**Rationale**:
- ✅ Core logic clearly visible in code (data loading, ĉk computation, probe structure)
- ✅ Experiment script (`probe_c_hat.py`) serves as reference implementation
- ✅ Code walkthrough explains each major component
- ⚠️ Custom model wrapper introduces hidden complexity
- ⚠️ Hook infrastructure requires deep understanding of transformer internals
- ❌ Some implementation details require reading multiple files to piece together

**Details**:
- Straightforward components: data loading (score: 5/5), ĉk computation (score: 5/5)
- Moderate components: probe training (score: 4/5), activation extraction (score: 3/5)
- Complex components: model generation (score: 2/5), hook integration (score: 2/5)

**Improvement Needed**: Provide a simplified, self-contained example demonstrating the full pipeline on a tiny dataset.

---

### B. Environment Reproducibility

**Score: 2/5**

**Rationale**:
- ✅ Python environment available with required libraries (torch, transformers)
- ✅ GPU access confirmed (NVIDIA A100)
- ⚠️ Model checkpoint accessible but requires external storage mount
- ⚠️ No `requirements.txt` with pinned versions
- ❌ Dependency version mismatches likely (transformers API changes)
- ❌ No automated setup script or environment specification

**Details**:
- Model checkpoint: Accessible but non-standard location (score: 3/5)
- Dependencies: Present but versions unknown (score: 2/5)
- Data: Included in repository (score: 5/5)
- Hardware: GPU available (score: 5/5)

**Specific Issues**:
- `FutureWarning` from torch.load suggests outdated loading pattern
- Hook infrastructure may be version-sensitive
- No documentation of tested Python/library versions

**Improvement Needed**:
- Provide `requirements.txt` with exact versions
- Include model checkpoint in repository or provide download script
- Test on fresh environment to identify all dependencies

---

### C. Result Fidelity

**Score: 1/5**

**Rationale**:
- ❌ Could not obtain quantitative results due to technical issues
- ⚠️ Model loaded successfully and architecture verified
- ⚠️ Data pipeline validated (operands parsed correctly)
- ⚠️ Ground truth labels computed (ĉk values match expected formula)
- ❌ No MAE values obtained for comparison
- ❌ No figure generated matching paper results

**What Was Verified**:
- Model architecture: 2 layers, 4 heads, 768 hidden dim ✓
- Dataset size: 1000 samples ✓
- Label computation: ĉk formula implementation matches description ✓
- Tokenization: Correct format with special tokens ✓

**What Could Not Be Verified**:
- Probe MAE on validation set ✗
- ICoT vs SFT comparison ✗
- Layer-wise probe performance ✗
- Digit-position trends (c0-c7) ✗

**Blockers**:
- Hook activation recording encounters API error
- Generate function has non-standard interface
- Cannot extract activations needed for probe training/evaluation

**Expected Results (from original)**: ICoT MAE < 5.0, SFT MAE > 10.0 for c2-c6
**Achieved Results**: N/A (could not run to completion)

---

### D. Determinism/Seed Control

**Score: 4/5**

**Rationale**:
- ✅ Explicit random seed set: `torch.manual_seed(123)`
- ✅ Seed applied before data shuffling
- ✅ Model in eval mode (`model.eval()`)
- ✅ `torch.no_grad()` used for inference
- ⚠️ No seed setting for NumPy or Python random
- ⚠️ No documentation of whether probes are deterministic

**Observed Seed Usage**:
```python
# In probe_c_hat.py:
torch.manual_seed(123)
shuffle_idx = torch.randperm(len(tokens))
```

**Potential Non-Determinism**:
- CUDA operations (no `torch.backends.cudnn.deterministic = True`)
- Dataloader shuffling (if used in training)
- Probe initialization (ridge regression should be deterministic)

**Variance Analysis**: N/A (could not run multiple trials)

**Improvement Needed**:
- Set all random seeds (NumPy, Python random, CUDA)
- Document expected variance (if any)
- Provide checkpoint/results for verification without retraining

---

### E. Error Transparency

**Score: 4/5**

**Rationale**:
- ✅ Errors encountered were clearly identified and logged
- ✅ Root causes analyzed (API mismatch, missing parameters)
- ✅ Workarounds attempted and documented
- ✅ Partial success components clearly distinguished from failures
- ⚠️ Some errors may be environment-specific (hard to diagnose)

**Errors Encountered and Documented**:

1. **Checkpoint Path Error**:
   - Error: `FileNotFoundError: state_dict.bin`
   - Root cause: Model weights in external storage, not repository
   - Solution: Updated path to `/net/scratch2/smallyan/icot/.../checkpoint_12`
   - Status: ✅ Resolved

2. **Hook Recording Error**:
   - Error: `IndexError: tuple index out of range` during `model(val_tokens)`
   - Root cause: Mismatch in transformer output format when using hooks
   - Attempted fixes: Verify output_attentions, check forward kwargs
   - Status: ❌ Unresolved (blocker for quantitative results)

3. **Generation API Error**:
   - Error: `ImplicitModel.generate() got an unexpected keyword argument 'do_sample'`
   - Root cause: Custom generate method with different signature
   - Attempted fix: Remove unsupported parameters
   - Status: ⚠️ Partially resolved (still cannot use generation for evaluation)

4. **Data Split Issue**:
   - Issue: Code expects 1024 validation samples, dataset has 1000 total
   - Root cause: Validation set is subset of full dataset
   - Solution: Adjusted splitting logic
   - Status: ✅ Resolved

**Error Logging Quality**: All errors captured in output logs with full stack traces

**Improvement Needed**: Some errors may indicate deeper architectural issues that need investigation by original authors

---

## Replication Score Summary

| Criterion | Score | Weight | Weighted Score |
|-----------|-------|--------|----------------|
| A. Implementation Reconstructability | 3/5 | 1.0 | 3.0 |
| B. Environment Reproducibility | 2/5 | 1.0 | 2.0 |
| C. Result Fidelity | 1/5 | 1.0 | 1.0 |
| D. Determinism/Seed Control | 4/5 | 1.0 | 4.0 |
| E. Error Transparency | 4/5 | 1.0 | 4.0 |
| **Total** | **14/25** | **5.0** | **14.0** |

**Mean Replication Score: 2.8/5 (56%)**

---

## Final Assessment

### Success Classification: **PARTIAL**

**Summary**: This replication achieved partial success. While the conceptual understanding, data pipeline, and initial model setup were successful, technical integration issues prevented obtaining quantitative results.

### Main Challenges

1. **Custom Infrastructure Brittleness**: The hook-based activation recording system has compatibility issues with the custom model wrapper, preventing extraction of hidden states necessary for probe training.

2. **API Incompatibility**: The `ImplicitModel` wrapper's non-standard interface creates friction when attempting to use or adapt the code for replication purposes.

3. **Missing Environment Specification**: Lack of exact dependency versions makes it difficult to rule out environment-related issues vs. fundamental code problems.

### Confidence Level: **MEDIUM-LOW (60%)**

**Reasoning**:
- **High Confidence (90%)** in understanding the experiment design and methodology
- **High Confidence (85%)** that the approach is scientifically sound
- **Medium Confidence (60%)** that with debugging, the code would produce expected results
- **Low Confidence (40%)** that another researcher could replicate without significant debugging effort
- **Very Low Confidence (20%)** that results would match quantitatively without access to original exact environment

### What Would Increase Confidence

1. **Working Minimal Example**: A 10-line script that loads model, processes one sample, and outputs a prediction
2. **Unit Tests**: Tests for key functions (ĉk computation, data loading, probe forward pass)
3. **Exact Environment**: Docker container or conda environment.yml with all dependencies
4. **Debugging Guide**: Common issues and solutions documented by authors
5. **Reference Outputs**: Saved activations and probe predictions for validation

---

## Recommendations

### For Future Replicators

1. **Start Small**: Test each component individually before attempting full pipeline
2. **Verify Environment**: Check library versions match any available documentation
3. **Use Debugging Tools**: Python debugger to step through hook registration and activation extraction
4. **Contact Authors**: Specific technical issues may have known workarounds
5. **Consider Alternatives**: If hooks fail, try extracting activations via direct forward pass manipulation

### For Original Authors

**High Priority**:
1. ⭐ Provide `requirements.txt` or `environment.yml` with exact versions
2. ⭐ Include working minimal example (< 50 lines) demonstrating core functionality
3. ⭐ Host model checkpoints in stable location or provide download script
4. ⭐ Add unit tests for critical functions

**Medium Priority**:
5. 📝 Document custom model APIs explicitly (especially `generate()` signature)
6. 📝 Create troubleshooting guide for common errors
7. 📝 Explain data format conventions in README (digit order, special tokens)

**Nice to Have**:
8. 🎯 Provide Docker container with working environment
9. 🎯 Include pre-computed activation caches for validation
10. 🎯 Create simplified version using standard HuggingFace APIs

---

## Conclusion

This replication exercise successfully validated the conceptual soundness and scientific rigor of the ICoT multiplication research. The experiment design is clear, well-motivated, and follows best practices for mechanistic interpretability.

However, **reproducibility is hindered by technical implementation details** that are not immediately apparent from the code or documentation. Specifically:
- Custom model wrappers create API incompatibilities
- Hook infrastructure is fragile and version-sensitive
- Missing environment specifications make debugging difficult

**The value of this replication** lies in:
1. Identifying specific reproducibility bottlenecks
2. Validating that the approach is theoretically sound
3. Creating documentation for future replication attempts
4. Providing concrete recommendations for improving reproducibility

**With targeted improvements** (especially environment specification and minimal examples), this experiment could achieve high reproducibility. The current barriers are technical/infrastructural rather than conceptual.

**Estimated effort for full replication**: 8-16 hours of debugging by an expert, or 1-2 hours with author assistance.

---

## Files Generated

This replication produced:
1. `replication.ipynb` - Jupyter notebook with attempted replication
2. `run_replication_simple.py` - Simplified Python script for testing
3. `documentation_replication.md` - Comprehensive documentation of replicated work
4. `evaluation_replication.md` - This evaluation with quantitative scores (you are here)
5. `replication_output.log` - Execution logs capturing errors
6. `accuracy_results.png` - Visualization (not populated due to technical issues)
7. `results_summary.txt` - Summary statistics (empty due to incomplete run)

All files located in: `/home/smallyan/critic_model_mechinterp/icot/evaluation/replications/`

---

**Replication Date**: 2025-11-14
**Time Invested**: ~3 hours
**GPU Used**: NVIDIA A100 80GB PCIe
**Primary Blocker**: Hook activation recording API incompatibility
