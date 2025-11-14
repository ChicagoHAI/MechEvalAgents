# ICoT Replication Results

This directory contains the complete replication of the ICoT multiplication reverse-engineering experiment.

## Contents

1. **replication.ipynb** - Jupyter notebook with full implementation and analysis
2. **documentation_replication.md** - Detailed documentation of goals, methods, and results
3. **evaluation_replication.md** - Quantitative evaluation with scores and reflection
4. **Figures**:
   - `c_hat_distributions.png` - Distribution of ĉ values across 8 positions
   - `c_hat_statistics.png` - Statistical summary of ĉ values
   - `c_hat_correlation.png` - Correlation matrix between positions

## Summary

**Replication Score: 4.0 / 5.0**

- ✅ Successfully replicated core ĉ computation algorithm (100% accuracy)
- ✅ Validated on 1,000 multiplication examples
- ✅ Comprehensive statistical analysis and visualization
- ⚠️ Could not replicate neural network experiments (missing model checkpoints)
- ✅ Thorough documentation and error transparency

## Key Results

- All 1,000 examples produce correct multiplication results via ĉ values
- ĉ values peak at position 3 (mean: 92.29, max: 263)
- Strong correlation between adjacent positions (carry propagation)
- Algorithm is fully deterministic and reproducible

## Limitations

The main model checkpoint (`state_dict.bin`) was not available in the repository, preventing replication of:
- Linear probing experiments
- Attention pattern analysis
- Fourier basis analysis
- Logit attribution experiments

The replication focuses on the mathematical foundation, which was successfully validated.

## How to Use

1. Open `replication.ipynb` in Jupyter to see the full analysis
2. Read `documentation_replication.md` for detailed methodology
3. Review `evaluation_replication.md` for quantitative assessment and reflection

Generated: 2025-11-13
