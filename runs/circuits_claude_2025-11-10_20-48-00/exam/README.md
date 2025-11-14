# Sarcasm Circuit Exam

This directory contains a comprehensive exam designed to evaluate understanding of the sarcasm detection circuit research documented in the parent directory.

## Files

### 1. `exam_documentation.ipynb`
- **Purpose**: Student-facing exam notebook
- **Contents**: 
  - Key knowledge points summary
  - 9 multiple choice questions
  - 7 free-generation questions  
  - 3 code question stubs (without solutions)
- **Total**: 19 questions

### 2. `exam_sarcasm_circuit.json`
- **Purpose**: Complete exam schema with answers and references
- **Format**: JSON array with full question objects including:
  - `question_type`, `question`, `answer`, `choice`
  - `requires_code`, `code_id`, `reference`
- **Use**: Grading, reference, validation

### 3. `exam_sarcasm_circuit_student_version.json`
- **Purpose**: Student-facing exam schema (no answers/references)
- **Format**: JSON array with questions only
- **Use**: Programmatic exam distribution

### 4. `exam_code_questions.txt`
- **Purpose**: Plain text index of code questions
- **Format**: One block per code question with:
  - `[code_id]`, `Title`, `Prompt`, `Expected_Outcome`, `Reference`
- **Use**: Quick reference for code question requirements

### 5. `exam_code_solutions.ipynb`
- **Purpose**: Code solutions with validation
- **Contents**:
  - Student stubs (identical to exam_documentation.ipynb)
  - Solution cells (marked with # SOLUTION)
  - Auto-check cells (assertions with tolerance)
- **Use**: Grading, verification, reference implementation

## Exam Structure

### Coverage Breakdown
- **Factual Understanding**: ~50% (9 MC + 3 free-gen questions)
- **Applied Reasoning**: ~50% (4 free-gen + 3 code questions)

### Question Types

#### Multiple Choice (9 questions)
- Primary computational mechanism
- Dominant component identification
- Budget utilization
- Excluded components
- Method identification
- Attention head distribution
- Normalization approach
- Key limitations
- Model specifications

#### Free Generation (7 questions)
- Three-stage hierarchical processing explanation
- IOI circuit comparison
- Linguistic features and detection mechanism
- Hypothesis evolution analysis
- Budget distribution reasoning
- m3/m4 exclusion hypothesis
- Ablation experiment design

#### Code Questions (3 questions)
1. **CQ1**: Write budget calculation verification
2. **CQ2**: Differential activation percentage verification
3. **CQ3**: Attention head distribution verification

## Key Knowledge Points Tested

1. **Circuit Discovery Method**
   - Differential activation analysis
   - L2 norm measurement
   - Budget-constrained selection

2. **Circuit Architecture**
   - 54 components (1 input, 10 MLPs, 43 heads)
   - 11,200 dimension budget (100% utilization)
   - Three-stage processing

3. **Key Components**
   - m2 primary detector (32.47 differential)
   - m11 final processing (22.30 differential)
   - Layer 11 attention heads (a11.h8, a11.h0)

4. **Mechanistic Insights**
   - Early detection (Layer 2, not middle layers)
   - MLP dominance over attention
   - Pattern matching vs semantic reversal

5. **Comparison to IOI**
   - Different mechanisms (MLP vs attention)
   - Different key layers (early vs late)
   - Different densities (dense vs sparse)

6. **Limitations**
   - No causal validation
   - Small dataset
   - Synthetic data
   - Budget maximization

## Expected Outcomes (Code Questions)

### CQ1: Write Budget Verification
```
Calculated total write cost: 11200
  - Input embedding: 768
  - MLPs: 7680
  - Attention heads: 2752
Documented budget: 11200
Budget matches documentation: True
```

### CQ2: Differential Activation Percentage
```
m2 differential: 32.47
m11 differential: 22.30
Percentage stronger: 45.61%
Claimed percentage: 45.0%
Approximately correct (±2%): True
```

### CQ3: Attention Head Distribution
```
Early layers (L0-L3): 9 heads (documented: 9)
Middle layers (L4-L7): 19 heads (documented: 19)
Late layers (L8-L11): 15 heads (documented: 15)
Total heads: 43
Distribution matches documentation: True
```

## Quality Assurance

All questions are:
- **Documentation-grounded**: Answerable from documentation alone
- **Non-trivial**: Require comprehension, not lookup
- **Clear**: Unambiguous phrasing and expectations
- **Balanced**: Mix of factual recall and applied reasoning
- **Verified**: Code questions include auto-checks with tolerance

## Usage Notes

1. **For Students**: 
   - Start with `exam_documentation.ipynb`
   - Use only the documentation in `/logs/documentation.md`
   - Do not access solution files

2. **For Graders**:
   - Use `exam_sarcasm_circuit.json` for answer key
   - Run `exam_code_solutions.ipynb` to verify code outputs
   - Check auto-checks pass with documented tolerances

3. **For Validation**:
   - Code questions are deterministic (no randomness)
   - Auto-checks include tolerance for floating-point comparison
   - Expected runtime: <5 seconds per code question

## Design Rationale

This exam follows evidence-based assessment principles:

1. **Bloom's Taxonomy Coverage**:
   - Remember/Understand: MC questions on facts
   - Apply/Analyze: Free-gen on comparisons, mechanisms
   - Evaluate/Create: Hypothesis generation, experiment design

2. **Causal Verification Emphasis**:
   - Code questions test generalization of documented claims
   - Students must compute, not just recall
   - Validates understanding of underlying principles

3. **No Plan Access**:
   - Students see only `documentation.md`
   - Tests ability to extract knowledge from research docs
   - Mirrors real-world paper comprehension scenarios

