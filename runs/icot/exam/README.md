# ICoT Multiplication Exam - README

## Overview

This directory contains a comprehensive exam designed to assess understanding of the research on "Why Can't Transformers Learn Multiplication? Reverse-Engineering Reveals Long-Range Dependency Pitfalls."

**Important Note**: This repository does not contain a separate PLAN file. The exam is designed based entirely on the documentation available in `/icot/icot_restructured/documentation.md`, which describes the completed research, findings, and methodologies.

---

## Exam Files

### 1. `exam_documentation.ipynb`
- **Purpose**: Student-facing exam notebook
- **Contents**:
  - Comprehensive key knowledge points (10 major sections)
  - Code question stubs with clear TODOs
  - Instructions and context for each code question
- **Usage**: Distribute to students for taking the exam

### 2. `exam_icot.json`
- **Purpose**: Complete exam with all questions and answers
- **Contents**: 31 questions total
  - Multiple-choice questions (testing factual understanding)
  - Free-generation questions (testing reasoning and application)
  - Code questions (computational verification)
- **Format**: JSON array with fields:
  - `question_type`: "multiple_choice" or "free_generation" or "code"
  - `question`: The question text
  - `answer`: Model answer
  - `choice`: Options for multiple-choice (if applicable)
  - `requires_code`: Boolean
  - `code_id`: Identifier for code questions (e.g., "CQ1")
  - `reference`: Documentation section reference

### 3. `exam_icot_student_version.json`
- **Purpose**: Student version without answers
- **Contents**: Same questions without `answer` and `reference` fields
- **Usage**: For automated grading systems or student self-study

### 4. `exam_code_questions.txt`
- **Purpose**: Index of code questions
- **Format**: Plain text with one block per code question:
  ```
  [code_id]: CQ1
  Title: <title>
  Prompt: <student-facing prompt>
  Expected_Outcome: <what solution computes/prints>
  Reference: <documentation section>
  ---
  ```
- **Contains**: 3 code questions (CQ1, CQ2, CQ3)

### 5. `exam_code_solutions.ipynb`
- **Purpose**: Complete solutions with auto-grading
- **Contents**:
  - Student stubs (identical to exam_documentation.ipynb)
  - Complete solution implementations
  - Auto-check cells with tolerance-based validation
- **Usage**: Instructor reference and automated grading
- **⚠️ INSTRUCTOR ONLY**: Do not distribute to students

---

## Exam Structure

### Question Breakdown

**Total Questions**: 31

**By Type**:
- Multiple-choice: 10 questions (factual understanding)
- Free-generation: 18 questions (reasoning, application, transfer)
- Code: 3 questions (computational verification)

**By Content**:
- Research motivation and goals: 3 questions
- Data format and training: 4 questions
- Model architecture: 3 questions
- Performance results: 2 questions
- Discovered mechanisms: 6 questions
- Learning dynamics: 4 questions
- Geometric representations: 3 questions
- Implications and applications: 3 questions
- Code verification: 3 questions

**Balance**:
- Factual understanding: ~45% (questions 1-10 mostly)
- Reasoning/application: ~55% (questions 11-31)

---

## Code Questions Details

### CQ1: Fourier Basis R² Verification
**Concept Tested**: Geometric representations using Fourier bases

**Task**:
- Construct Fourier basis Φ(n) = [1, cos(2πn/10), sin(2πn/10), cos(2πn/5), sin(2πn/5), (-1)^n]
- Compute R² fit for structured vs. random embeddings
- Demonstrate structured embeddings achieve R² ≈ 1.0, random < 0.5

**Expected Runtime**: <10 seconds
**Dependencies**: numpy
**Auto-checks**: 3 validations (structured R² > 0.98, random R² < 0.6, difference > 0.5)

### CQ2: Attention Tree Caching/Retrieval
**Concept Tested**: Binary attention tree mechanism

**Task**:
- Simulate Layer 1 caching of pairwise products a_i × b_j
- Simulate Layer 2 retrieval to compute output digit c_3
- Verify correct computation for 8331 × 5015 example
- Show which cached products are retrieved

**Expected Runtime**: <5 seconds
**Dependencies**: numpy
**Auto-checks**: 4 validations (c_3 = 7, 4 products retrieved, correct sum, full product correct)

### CQ3: Logit Attribution Dependency Pattern
**Concept Tested**: Long-range dependency structure

**Task**:
- Compute 8×8 dependency matrix for multiplication
- Encode dependencies: 2 (strong, i+j=k), 1 (weak, i+j<k), 0 (none)
- Visualize as heatmap
- Validate mathematical properties

**Expected Runtime**: <10 seconds
**Dependencies**: numpy, matplotlib
**Auto-checks**: 6 validations (c_0 dependencies, c_7 dependencies, middle digits, i+j=k pattern, shape, value range)

---

## Grading Rubric

### Multiple-Choice Questions (10 questions)
- **Points per question**: 3 points
- **Total**: 30 points
- **Grading**: Exact match only

### Free-Generation Questions (18 questions)
- **Points per question**: 5 points
- **Total**: 90 points
- **Grading criteria**:
  - Factual accuracy (2 points)
  - Conceptual understanding (2 points)
  - Completeness and clarity (1 point)

### Code Questions (3 questions)
- **Points per question**: 10 points
- **Total**: 30 points
- **Grading**: Based on auto-check pass rate
  - All checks passed: 10 points
  - 75%+ checks passed: 7 points
  - 50%+ checks passed: 5 points
  - <50% checks passed: 0-3 points (partial credit for effort)

**Total Possible Points**: 150

**Grade Scale**:
- A: 135-150 (90%+)
- B: 120-134 (80-89%)
- C: 105-119 (70-79%)
- D: 90-104 (60-69%)
- F: <90 (<60%)

---

## Key Knowledge Points Covered

1. **Research Motivation**: Why Transformers fail, hypothesis, objectives
2. **Data Format**: Least-significant-first ordering, ICoT curriculum, token removal
3. **Training Procedures**: ICoT, SFT, auxiliary loss approaches
4. **Architecture**: Minimal 2L4H architecture, scaling results
5. **Discovered Mechanisms**:
   - Binary attention trees (caching/retrieval)
   - Minkowski sums (nested geometric structures)
   - Fourier basis representations (pentagonal prism)
6. **Long-Range Dependencies**: Logit attribution, linear probes, ĉ_k encoding
7. **Learning Dynamics**: SFT failure pattern, gradient flow, local optima
8. **Geometric Representations**: R² fits, self-similarity, parity separation
9. **Core Insights**: Optimization vs. capacity, inductive biases, process supervision
10. **Implications**: Multi-step reasoning, architectural design, training methodology

---

## Usage Instructions

### For Instructors

1. **Distribute**: Give students `exam_documentation.ipynb` and `exam_icot_student_version.json`
2. **Reference Materials**: Allow access to `documentation.md` during exam
3. **Time Limit**: Recommended 3-4 hours for complete exam
4. **Code Environment**: Provide Python environment with numpy, matplotlib
5. **Grading**: Use `exam_code_solutions.ipynb` auto-checks for code questions
6. **Answer Key**: Refer to `exam_icot.json` for all model answers

### For Students

1. **Read**: Review `documentation.md` thoroughly before exam
2. **Answer**: Complete questions in `exam_documentation.ipynb`
3. **Code**: Implement all TODOs in code question cells
4. **Verify**: Run cells to check your code works
5. **Submit**: Export completed notebook and JSON responses

### Running Code Solutions

```bash
# Install dependencies
pip install numpy matplotlib

# Run Jupyter notebook
jupyter notebook exam_code_solutions.ipynb

# Or convert to script
jupyter nbconvert --to script exam_code_solutions.ipynb
python exam_code_solutions.py
```

---

## Design Principles

### Comprehensive Coverage
- All 7 major documentation sections represented
- Key findings and mechanisms tested
- Both factual and applied understanding assessed

### Non-Trivial Questions
- No simple fact lookups
- Require understanding of mechanisms and relationships
- Transfer questions test generalization

### Code Verification
- Each code question verifies a key research claim
- Deterministic (seeded) for reproducibility
- Fast execution (<60 seconds total)
- Self-contained (no external dependencies beyond numpy/matplotlib)

### Grounded in Documentation
- Every question answerable from documentation alone
- References provided for each question
- No reliance on hypothetical plan files

---

## Special Notes

### No Plan File
This repository does not contain a separate PLAN file. All questions are designed based on:
- The completed research documentation (`documentation.md`)
- The code walkthrough (`code_walkthrough.md`)
- Observable implementation details in the codebase

Questions related to "plan" or "experiment design" are avoided, as requested in the original task instructions.

### Documentation-Only Assessment
Students should be able to answer all questions (including code questions) using only:
1. `documentation.md` - Primary reference
2. `code_walkthrough.md` - For implementation details (if needed)
3. Basic knowledge of machine learning and transformers

No access to actual model checkpoints or training scripts is required.

### Code Question Philosophy
Code questions ask students to **verify** research claims, not to **discover** them:
- CQ1: Verify Fourier basis R² fits match reported values
- CQ2: Verify attention tree mechanism computes multiplication correctly
- CQ3: Verify dependency pattern matches mathematical structure

This tests computational understanding while keeping runtime fast and dependencies minimal.

---

## Contact and Feedback

For questions about exam design or grading:
- Review `exam_icot.json` for complete answer key
- Check `exam_code_solutions.ipynb` for solution implementations
- Refer to `documentation.md` sections cited in references

---

**Exam Version**: 1.0
**Created**: 2025-11-14
**Repository**: /home/smallyan/critic_model_mechinterp/icot
**Documentation Source**: icot_restructured/documentation.md
