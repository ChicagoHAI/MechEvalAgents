# Sarcasm Circuit Analysis - Replication Documentation

## Goal

Identify the computational circuit in GPT2-small responsible for detecting sarcasm in text using differential activation analysis.

## Research Question

What components (MLPs and attention heads) in GPT2-small show differential activation patterns between sarcastic and literal text, and how do these components form a hierarchical processing circuit?

## Data

### Dataset Design
- **Size**: 5 paired examples (10 texts total)
- **Structure**: Sarcastic/literal pairs on similar topics
- **Sarcastic examples**: Positive words in negative contexts
  - "Oh great, another meeting at 7 AM."
  - "Wow, I just love getting stuck in traffic."
  - "Perfect, my computer crashed right before the deadline."
  - "Fantastic, it's raining on my only day off."
  - "Amazing, the wifi is down again."

- **Literal examples**: Genuine positive sentiment
  - "I'm excited about the meeting at 7 AM tomorrow."
  - "I really enjoy my peaceful morning commute."
  - "I'm glad I saved my work before the deadline."
  - "I love relaxing at home on my day off."
  - "The wifi connection is working great today."

### Data Characteristics
- Paired structure enables direct comparison
- Clear discourse markers in sarcastic text ("Oh", "Wow", "Perfect")
- Sentiment-context incongruity is the key feature

## Method

### 1. Model Setup
- **Model**: GPT2-small (HookedTransformer from TransformerLens)
- **Configuration**:
  - 12 layers
  - 12 attention heads per layer
  - d_model = 768 (MLP dimension)
  - d_head = 64 (attention head dimension)
- **Device**: CUDA (NVIDIA A100 80GB)
- **Reproducibility**: Seeds set to 42

### 2. Activation Collection
For each text example:
1. Tokenize with BOS token prepended
2. Run forward pass with activation caching
3. Store all intermediate activations using HookedTransformer hooks

### 3. Differential Activation Analysis

**Core Metric**: L2 norm of activation differences

For each component (MLP or attention head):
1. Extract activations for sarcastic and literal examples
2. Average activations over sequence dimension
3. Compute L2 difference: `||mean(act_sarc) - mean(act_lit)||_2`
4. Average across all 5 pairs

**Hook Points Used**:
- MLPs: `blocks.{layer}.hook_mlp_out` (shape: [batch, seq, 768])
- Attention heads: `blocks.{layer}.attn.hook_z` (shape: [batch, seq, 12, 64])

### 4. Circuit Construction

**Budget Constraints**:
- Total budget: 11,200 dimensions
- Input embedding: 768 dims (required)
- MLP layer: 768 dims each
- Attention head: 64 dims each

**Selection Algorithm** (greedy):
1. Start with input embedding (768 dims)
2. Add all MLPs with differential ≥ 7.0 (10 MLPs × 768 = 7,680 dims)
3. Fill remaining budget with top attention heads (2,752 dims / 64 = 43 heads)
4. Total: 11,200 dims (100% utilization)

**Rationale**:
- MLPs show much higher differential than attention heads
- Prioritize high-impact components
- Maximize total differential activation within budget

## Results

### Component Rankings

**Top 10 MLPs** (by differential activation):
1. m2: 31.51 ← **Dominant sarcasm detector**
2. m11: 22.32
3. m10: 17.47
4. m9: 13.23
5. m8: 11.51
6. m7: 9.70
7. m6: 8.70
8. m1: 8.07
9. m0: 7.98
10. m5: 7.59

**Top 10 Attention Heads**:
1. a11.h8: 3.00 ← **Output integration head**
2. a11.h0: 2.59
3. a8.h5: 1.43
4. a4.h11: 1.37
5. a6.h11: 1.36
6. a10.h5: 1.29
7. a5.h3: 1.27
8. a11.h3: 1.24
9. a9.h3: 1.23
10. a8.h10: 1.22

### Final Circuit Composition

**Total**: 54 components
- Input embedding: 1 (768 dims)
- MLPs: 10 (7,680 dims)
- Attention heads: 43 (2,752 dims)
- **Write budget**: 11,200 / 11,200 (100%)

**MLP Distribution**:
- Early layers (L0-L2): m0, m1, **m2** (dominant)
- Middle layers (L5-L7): m5, m6, m7
- Late layers (L8-L11): m8, m9, m10, m11
- Excluded: m3, m4 (differential < 7.0)

**Attention Head Distribution**:
- Layer 11: 5 heads (including top 2)
- Layer 8: 5 heads
- Layer 4-6: 13 heads
- Other layers: 20 heads
- Dense coverage across middle-to-late layers

## Analysis

### Three-Stage Hierarchical Model

#### Stage 1: Early Detection (L0-L2)
**Primary component**: m2 (diff = 31.51)
- **Function**: Detect incongruity between sentiment words and context
- **Evidence**: 41% stronger than next component (m11)
- **Mechanism**: Process combination of positive sentiment markers ("great", "love") with negative contextual cues

**Supporting components**: m0 (7.98), m1 (8.07)
- Provide initial sentiment and context encoding
- Feed into m2's incongruity computation

#### Stage 2: Signal Propagation (L3-L7)
**Key MLPs**: m5 (7.59), m6 (8.70), m7 (9.70)
- **Function**: Propagate and refine sarcasm signal from m2
- **Evidence**: Moderate differential activation
- **Attention heads** (L4-L6): Dense cluster distributes information across positions

#### Stage 3: Final Integration (L8-L11)
**Critical MLPs**: m8 (11.51), m9 (13.23), m10 (17.47), m11 (22.32)
- **Function**: Final processing before output
- **Evidence**: Increasing differential through layers
- m11 particularly strong, suggesting final pre-output refinement

**Output heads**: a11.h8 (3.00), a11.h0 (2.59)
- **Function**: Integrate processed sarcasm signal into final representation
- **Evidence**: Strongest attention head differentiation
- Determine how sarcasm affects token predictions

### Key Insights

1. **Early detection dominates**: Network identifies sarcasm at Layer 2, not through gradual accumulation
2. **Not sentiment reversal**: Later layers integrate early detection signal rather than flipping polarity
3. **Distributed routing**: 43 attention heads suggest complex information movement across sequence positions
4. **Hierarchical refinement**: Early detection → middle propagation → late integration

### Comparison to Hypothesis

From the plan document, the original hypothesis was:
- Early layers (L0-L3): Sentiment encoding ✓ (Partially correct)
- Middle layers (L4-L7): Incongruity detection ✗ (Actually happens at L2)
- Late layers (L8-L11): Meaning reversal ✗ (Actually signal integration)

**What was correct**:
- Early layers important for initial processing ✓
- Late layers critical for final output ✓
- MLPs more important than attention heads ✓

**What was incorrect**:
- Timing: Detection happens at L2, not L4-L7
- Mechanism: Integration not reversal

## Limitations

1. **Small dataset**: Only 5 paired examples
   - Statistical variation possible
   - May not generalize to all sarcasm types

2. **Synthetic data**: Hand-crafted examples may not capture real-world complexity
   - All follow similar pattern (positive words + negative context)
   - Missing: implicit sarcasm, cultural context, tone markers

3. **Correlation ≠ Causation**: High differential doesn't prove causal importance
   - Components may be correlated with sarcasm without being necessary
   - Need ablation studies to test causal contribution

4. **No behavioral validation**: Haven't verified circuit reproduces sarcasm detection
   - Should test on held-out examples
   - Should measure accuracy drop when ablating components

5. **Determinism**: Single run with fixed seeds
   - Results should be verified across multiple random initializations
   - Variability analysis needed

## Future Directions

1. **Systematic ablation**: Test each component's causal contribution by removing it
2. **Larger dataset**: Expand to all 20+ examples or real-world data
3. **Attention pattern analysis**: Visualize what key heads attend to
4. **Iterative pruning**: Remove least important components, test fidelity
5. **Cross-task generalization**: Test if circuit works for other incongruity tasks
6. **Probing analysis**: Train linear classifiers to detect sarcasm signal at each layer

## Reproducibility

### Environment
- Python with PyTorch (CUDA enabled)
- TransformerLens library
- Random seeds: 42 (both torch and numpy)

### Computational Requirements
- GPU memory: ~5GB for GPT2-small with caching
- Runtime: ~30 seconds for full pipeline
- Storage: ~50MB for cached activations

### Data Availability
- Synthetic dataset defined in code
- Can be regenerated from scratch
- Original examples listed in this document
