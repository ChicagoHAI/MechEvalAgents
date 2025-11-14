# ICoT Multiplication Reverse-Engineering: Replication Documentation

## Goal

The goal of this replication is to reproduce the core computational experiment from the ICoT (Implicit Chain-of-Thought) multiplication reverse-engineering research. The original work investigates how transformer models learn to perform multi-digit multiplication by identifying intermediate computational values (running sums, denoted ĉ) that the model implicitly computes.

## Data

### Dataset
- **Source**: `data/processed_valid.txt` from the icot repository
- **Size**: 1,000 multiplication problems
- **Format**: 4-digit × 4-digit multiplication in reversed digit order
  - Example: `5 6 3 2 * 7 4 3 4` represents 2365 × 4347 = 10,280,655

### Data Preprocessing
1. Parse text file to extract operand pairs (a, b)
2. Reverse digit order to obtain correct decimal representation
3. Convert strings to integers for computation
4. All 1,000 examples successfully loaded and validated

## Method

### Core Algorithm: Running Sum (ĉ) Computation

The replication implements the fundamental multiplication algorithm that the original research hypothesizes neural networks learn implicitly.

**Algorithm Steps:**
1. Extract digits of operands in least-significant-digit-first order
2. For each position k (0 to 7):
   - Sum all products a_i × b_j where i + j = k (diagonal sum)
   - Add carry from previous position: carry = ĉ_{k-1} // 10
   - Store running sum: ĉ_k = diagonal_sum + carry
   - Extract output digit: c_k = ĉ_k mod 10

**Implementation:**
```python
def get_c_hats(a, b):
    c_hats = []
    carrys = []
    pair_sums = []

    a_digits = [int(d) for d in str(a)[::-1]]
    b_digits = [int(d) for d in str(b)[::-1]]
    total_len = len(a_digits) + len(b_digits)

    for ii in range(total_len):
        aibi_sum = 0
        for a_ii in range(ii, -1, -1):
            b_ii = ii - a_ii
            if 0 <= a_ii < len(a_digits) and 0 <= b_ii < len(b_digits):
                aibi_sum += a_digits[a_ii] * b_digits[b_ii]

        pair_sums.append(aibi_sum)
        if len(c_hats) > 0:
            aibi_sum += c_hats[-1] // 10

        c_hats.append(aibi_sum)
        carrys.append(aibi_sum // 10)

    return c_hats, carrys, pair_sums
```

### Verification Strategy
1. **Correctness Check**: Verify that extracting last digits of ĉ values produces correct multiplication result
2. **Statistical Analysis**: Compute mean, std, min, max for each position
3. **Correlation Analysis**: Measure dependencies between positions to understand carry propagation

## Results

### Numerical Correctness
- **All 1,000 examples validated**: 100% match between computed and expected results
- **Example verification** (2365 × 4347):
  - ĉ sequence: [35, 65, 66, 70, 48, 22, 10, 1]
  - Extracted digits: [5, 5, 6, 0, 8, 2, 0, 1]
  - Final answer: 10,280,655 ✓

### Statistical Properties

| Position | Mean  | Std   | Min | Max |
|----------|-------|-------|-----|-----|
| ĉ_0      | 19.95 | 20.09 | 0   | 81  |
| ĉ_1      | 41.92 | 28.65 | 0   | 150 |
| ĉ_2      | 64.76 | 36.04 | 0   | 213 |
| ĉ_3      | 92.29 | 42.07 | 0   | 263 |
| ĉ_4      | 74.71 | 37.57 | 3   | 218 |
| ĉ_5      | 51.60 | 30.66 | 0   | 165 |
| ĉ_6      | 30.08 | 21.57 | 1   | 95  |
| ĉ_7      | 2.55  | 2.18  | 0   | 9   |

**Key Observations:**
- ĉ values peak at position 3 (middle of computation)
- Variance is highest in middle positions (ĉ_3, ĉ_4)
- Edge positions (ĉ_0, ĉ_7) have lower values and variance
- Maximum ĉ value is 263 at position 3

### Correlation Analysis
- **Strong correlations** between adjacent positions (r > 0.8)
- **Decreasing correlation** with distance between positions
- **Physical interpretation**: Reflects carry propagation through multiplication algorithm

## Analysis

### What This Tells Us

1. **Algorithmic Foundation**: The ĉ values represent a natural intermediate representation for multiplication, making them excellent targets for interpretability research

2. **Predictability Varies by Position**:
   - Early positions (ĉ_0, ĉ_1) are easier to predict (lower variance)
   - Middle positions (ĉ_3, ĉ_4) are harder (higher variance, larger ranges)
   - This matches intuition: middle positions involve more partial products

3. **Sequential Dependencies**: High correlation between adjacent positions confirms that later ĉ values depend on earlier ones via carry propagation

### Connection to Original Research

The original ICoT research aimed to:
1. Train transformers on multiplication tasks
2. Use linear probes to test if hidden states encode ĉ values
3. Analyze attention patterns to understand information flow

This replication provides the **ground truth computational substrate** that the neural network experiments probe for. By establishing:
- Correct computation of ĉ values
- Their statistical properties
- Their interdependencies

We create the baseline against which neural network representations can be evaluated.

### Limitations and Scope

**What Was Replicated:**
- Core ĉ computation algorithm (100% accurate)
- Statistical analysis across 1,000 examples
- Visualization of distributions and correlations

**What Was Not Replicated:**
- Neural network model training/inference (no model checkpoints available)
- Linear probing experiments (requires model activations)
- Attention pattern analysis (requires trained transformer)
- Fourier basis analysis (requires model weights)

**Reason for Limited Scope:**
The repository's model checkpoint files (`state_dict.bin`) were not present, preventing replication of neural network-dependent experiments. However, the mathematical foundation was successfully replicated and verified.

## Conclusion

This replication successfully implements and validates the core computational algorithm underlying the ICoT multiplication research. The ĉ value computation is:

- **Mathematically correct**: All examples verified
- **Well-characterized**: Statistical properties documented
- **Interpretable**: Clear relationship to standard multiplication algorithm

The replication provides a solid foundation for understanding what the original neural network experiments were testing: whether transformers learn to implicitly represent these intermediate running sums when solving multiplication problems.
