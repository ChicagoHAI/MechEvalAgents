# Phase 1: Initial Hypothesis - Sarcasm Circuit Analysis

## Date: 2025-11-10

## Goal
Identify the precise circuit in GPT2-small that enables sarcasm recognition by detecting contradictions between literal sentiment and contextual tone.

## Dataset
- **Source**: Synthetic sarcasm dataset
- **Sarcastic examples**: 20 sentences with contradictory tone vs. literal meaning
- **Non-sarcastic examples**: 20 literal sentences with similar structure
- **Example sarcastic**: "Oh great, another meeting at 7 AM."
- **Example literal**: "I'm excited about the meeting at 7 AM tomorrow."

## Model Configuration
- **Model**: GPT2-small (HookedTransformer)
- **Layers**: 12
- **Heads per layer**: 12  
- **d_model**: 768
- **d_head**: 64

## Write Budget Constraints
- Attention head: 64 dimensions
- MLP layer: 768 dimensions
- Input embedding: 768 dimensions
- **Total budget**: ≤ 11,200 dimensions

## Initial Hypothesis

### Expected Three-Stage Mechanism

#### Stage 1: Early Layers (L0-L3) - Sentiment Encoding
**Function**: Detect and encode literal sentiment words

- Attention heads should identify positive sentiment markers: "great", "wonderful", "fantastic", "perfect"
- These layers represent surface-level positive/negative polarity
- **Predicted key heads**: a1.h4, a1.h7, a2.h3, a2.h8

**Evidence to look for**:
- Strong attention from sentence positions to sentiment words
- Activation patterns distinguishing positive vs neutral words

#### Stage 2: Middle Layers (L4-L7) - Context & Incongruity Detection  
**Function**: Detect mismatches between sentiment and context

- Attention heads attend to contextual clues signaling incongruity
- MLPs compute mismatch/contradiction signals
- Key markers: discourse particles ("Oh", "Wow"), repetition ("another"), negative situations
- **Predicted key heads**: a5.h2, a5.h6, a6.h4, a6.h9
- **Predicted MLPs**: m5, m6

**Evidence to look for**:
- Attention from sentiment words back to discourse markers
- Different activation patterns for sarcastic vs. literal sentences
- MLP activations correlated with incongruity presence

#### Stage 3: Late Layers (L8-L11) - Meaning Reversal
**Function**: Perform sentiment inversion and integrate true meaning

- MLPs flip sentiment polarity when sarcasm indicators present
- Attention heads integrate reversed sentiment into output representation
- **Predicted key MLPs**: m7, m8, m9, m10
- **Predicted key heads**: a9.h3, a10.h7, a11.h2

**Evidence to look for**:
- MLP outputs that reverse sentiment direction
- Ablating these components should impair sarcasm detection
- Causal contribution to correct classification

## Testing Strategy

### Phase 1 Experiments
1. **Activation Analysis**
   - Run model on sarcastic vs. literal pairs
   - Visualize activation differences across layers
   - Identify components with strongest differential signal

2. **Attention Pattern Analysis**  
   - Plot attention patterns for key sentiment/context positions
   - Compare sarcastic vs. literal sentences
   - Identify heads with characteristic sarcasm-related patterns

3. **Preliminary Ablation**
   - Systematically ablate each attention head
   - Measure impact on downstream activations
   - Identify most causally important heads

### Success Criteria
- Circuit reproduces sarcasm detection behavior with >80% fidelity
- Total write budget ≤ 11,200 dimensions  
- Each component has interpretable role
- Minimal component count (sparse, precise circuit)

### Hypotheses to Test
1. Early layers encode literal sentiment → **TESTABLE**: attention to positive words
2. Middle layers detect incongruity → **TESTABLE**: differential activation on sarcastic sentences
3. Late MLPs perform reversal → **TESTABLE**: ablation impairs sarcasm detection
4. Circuit is sparse (<50 components) → **TESTABLE**: can prune to small set

## Next Steps
1. Implement baseline testing infrastructure
2. Run activation patching experiments
3. Identify candidate circuit components
4. Refine hypothesis based on empirical results
5. Iterate until convergence on minimal, interpretable circuit
