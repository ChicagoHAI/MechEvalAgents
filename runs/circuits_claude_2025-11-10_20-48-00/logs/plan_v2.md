# Phase 2: Hypothesis Refinement - Sarcasm Circuit Analysis

## Date: 2025-11-10

## Revised Understanding Based on Empirical Evidence

### Summary of Phase 1 Findings

After analyzing 5 paired sarcastic/literal examples, we computed differential activation patterns across all 12 layers and 144 attention heads of GPT2-small.

**Key Discovery**: MLP layer 2 (m2) shows dramatically dominant differential activation (32.47), ~45% stronger than the next strongest component (m11: 22.30).

### Original vs. Observed Mechanism

#### Original Hypothesis
1. **Early layers (L0-L3)**: Sentiment encoding
2. **Middle layers (L4-L7)**: Incongruity detection
3. **Late layers (L8-L11)**: Meaning reversal

#### Empirical Findings
1. **Layer 2 MLP**: Primary sarcasm detector
2. **Late MLPs (L7-L11)**: Signal refinement and integration
3. **Layer 11 attention heads**: Critical output integration

### Revised Mechanistic Model

#### Stage 1: Early Detection (L0-L2)
**Primary Component**: m2 (write cost: 768 dims)

- **Function**: Detect incongruity between sentiment and context
- **Evidence**: 32.47 avg differential activation (4x stronger than typical MLP)
- **Mechanism**: 
  - Processes combination of sentiment words and contextual markers
  - Detects mismatch patterns: positive words + negative situations
  - Examples: "great" + "another meeting at 7 AM", "love" + "stuck in traffic"

**Supporting Components**: m0, m1 (write cost: 768 dims each)
- Provide initial sentiment and context encoding
- Feed into m2's incongruity computation

#### Stage 2: Signal Propagation and Refinement (L3-L7)
**Key MLPs**: m5, m6, m7 (write cost: 768 dims each)

- **Function**: Propagate and refine sarcasm signal from m2
- **Evidence**: Moderate differential activation (7-10 range)
- **Attention heads in L4-L6**: 
  - Dense cluster of moderately important heads
  - Distribute sarcasm information across sequence positions
  - Enable context-aware processing of the incongruity signal

#### Stage 3: Final Integration (L8-L11)
**Critical MLPs**: m8, m9, m10, m11 (write cost: 768 dims each)

- **Function**: Final processing of sarcasm signal
- **Evidence**: Increasing differential activation (11-22 range)
- m11 particularly strong (22.30), suggesting final pre-output processing

**Critical Attention Heads**: a11.h8, a11.h0 (write cost: 64 dims each)

- **Function**: "Output heads" that integrate processed signal into final representation
- **Evidence**: Strongest attention head differentiation (3.33, 2.74)
- Determine how sarcasm affects final token predictions

### Circuit Composition

**Total Components**: 54
- Input embedding: 1 (768 dims)
- MLPs: 10 (7,680 dims total)
- Attention heads: 43 (2,752 dims total)
- **Total write budget**: 11,200 / 11,200 (100% utilization)

**MLP Distribution**:
- All layers except m3, m4 (which showed minimal differential)
- Bimodal importance: early (m0-m2) + late (m7-m11)

**Attention Head Distribution**:
- Sparse in early layers (L0-L3): 9 heads
- Dense in middle layers (L4-L7): 19 heads  
- Moderate in late layers (L8-L11): 15 heads
- Concentration in L11: 5 heads including two most important

### Key Insights

1. **Sarcasm detection is early**: Network "decides" at L2 whether text is sarcastic
2. **Not sentiment reversal**: Later layers don't flip polarity but integrate early detection
3. **Distributed circuit**: 43 attention heads suggest information routing across positions
4. **Hierarchical processing**: Early detection → middle propagation → late integration

### Comparison to Original Predictions

✓ **Correct**: Early layers important for initial processing  
✗ **Incorrect**: Middle layers are primary detection site (actually L2)
✓ **Correct**: Late layers critical for final output
✗ **Incorrect**: Process is sentiment reversal (actually signal integration)
✓ **Correct**: MLPs more important than attention heads

### Validation Approach

To validate this circuit, we would need to:
1. **Ablation testing**: Remove components and measure impact on sarcasm detection
2. **Intervention experiments**: Patch activations to test causal relationships  
3. **Attention pattern analysis**: Verify information flow matches hypothesized stages
4. **Probing**: Train linear probes to detect sarcasm signal at each layer

### Limitations

1. **Small dataset**: Only 5 paired examples analyzed
2. **Synthetic data**: Real-world sarcasm may have different patterns
3. **Differential activation ≠ causation**: High differential doesn't guarantee causal importance
4. **No behavioral testing**: Haven't verified circuit actually reproduces sarcasm detection

### Next Steps for Phase 3

1. Expand analysis to all 20 sarcastic examples
2. Perform systematic ablation experiments
3. Analyze attention patterns in detail for key heads
4. Test circuit on held-out examples
5. Potentially prune circuit further based on ablation results

## Conclusion

The sarcasm circuit in GPT2-small appears to be a **three-stage hierarchical system** with early detection (m2), distributed propagation (mid-layer MLPs and attention), and final integration (late MLPs and L11 attention heads). This differs from our initial hypothesis in timing (earlier detection) and mechanism (integration rather than reversal).
