# IOI Circuit Analysis - Research Plan

## Objective

Identify a precise circuit in GPT2-small that implements the Indirect Object Identification (IOI) task while staying within a write budget of 11,200 dimensions.

## Hypothesis

The IOI circuit consists of three main components:

1. **Duplicate Token Heads**: Attend from S2 to S1, signaling token duplication
2. **S-Inhibition Heads**: Attend from END to S2, inhibiting attention to the subject
3. **Name-Mover Heads**: Attend from END to IO, copying the indirect object to the output

## Methodology

### Phase 1: Data Exploration
- Load GPT2-small model via TransformerLens
- Load mib-bench/ioi dataset
- Analyze dataset structure and identify key positions (S1, S2, IO, END)
- Establish baseline model performance on IOI task

### Phase 2: Attention Pattern Analysis
- Run model with activation caching
- For each layer and head, calculate attention patterns:
  - **Duplicate Token Heads**: Measure attention from S2 → S1
  - **S-Inhibition Heads**: Measure attention from END → S2
  - **Name-Mover Heads**: Measure attention from END → IO
- Rank heads by their alignment with hypothesized behavior

### Phase 3: Circuit Selection
- Select top-k heads from each category
- Include supporting MLPs from relevant layers
- Ensure total write budget ≤ 11,200 dimensions
  - Each head writes: d_model / n_heads = 768 / 12 = 64 dims
  - Each MLP writes: d_model = 768 dims

### Phase 4: Validation
- Verify all nodes are in allowed src_nodes
- Verify naming conventions (a{layer}.h{head}, m{layer})
- Verify budget constraints
- Document circuit composition and performance

## Expected Outcomes

- A JSON file (real_circuits_1.json) containing the selected circuit nodes
- Comprehensive documentation of findings
- Validation that the circuit stays within budget
- Analysis of whether findings support the IOI hypothesis

## Success Criteria

1. Circuit contains ≤ 11,200 dimensional writes
2. All nodes follow naming conventions
3. Circuit includes representatives from all three hypothesized head types
4. Documentation clearly explains methodology and results
