# Evaluation Pipeline for Automated MechInterp Research

## Typical Evaluation Pipeline

* **Exam** 
    * **Exam Designer** creates assessment questions from documentation
    * **Student** (or model) answers the exam
    * **Exam Grader** evaluates answers and detects external references
* **Instruction Following Evaluator** checks goal alignment and hypothesis testing
* **Consistency Evaluator** verifies code correctness and result-conclusion matching
* **Replication**
    * **Replicator** independently replicates the experiment
    * **Replicator-Documentation Evaluator** verifies replication fidelity

## Implementation
Run `evaluation_prompt_construct.py` and pass in the directory you want to evaluate. The directory must contain all required input files. Our replicator evaluator also needs the directory where the replication results are stored, so you’ll need to rerun this after generating those results. The parameters you need to pass in include `skip_replication`, `task_name`, `repo_path`, `system_prompt_path`, `replication_path`

Run `run_critic.sh` to get instruction-following and consistency evaluations; this will also produce the exam and replication outputs. You will need to change the prompts you pass in. 

Run `student/student_simulator.py` to complete the exam. You can choose your model and pass in the exam file and documentation there.

Finally, run `run_replicatoreval_grader.sh` to evaluate the replication results and the student’s answers.

## Evaluation Processes and Output Files

### Required Input Files

Each research project requires four types of files:
- **Plan** - Experiment goals and design
- **Implementation code** - Source code implementing the experiment
- **Code walkthrough** - Detailed explanation of the code (code_walk.md or equivalent)
- **Documentation** - Research report summarizing goals, methods, results, and conclusions

**Note:** We recommend using Jupyter notebooks for implementation to enable better quantitative analysis by the Consistency Evaluator. 

### 1. Exam Designer (`exam_designer.txt`)

**Purpose:** Creates comprehensive assessments from research documentation to test understanding of documented facts and ability to apply concepts.

**Input**: plan + implementaiton code + code walkthrough + documentation

**Output Directory:** `exam/`

**Output Files:**
- `exam_documentation.ipynb` - Notebook containing generated questions and gold answers
- `exam_{task_name}.json` - Structured exam data in JSON format
  - Contains: question type (multiple-choice or free-generation), question text, correct answer, choices (if applicable), and reference to documentation section

---

### 2. Exam Grader (`grader.txt`)

**Purpose:** Evaluates student answers to exams, checking both correctness and whether answers rely only on provided documentation.

**Input**: exam + student's answers + documentation

**Output Directory:** `exam/grade/`

**Output Files:**
- `grading_results.json` - Per-question grading results with scores, feedback, and external reference detection
  - Contains: question_id, question_type, question text, gold_answer, student_answer, score, feedback, reference, external_reference flag
- `grading_summary.md` - Readable summary with:
  - Quantitative performance metrics
  - Qualitative analysis
  - Overall score and grade level (Excellent/Good/Fair/Needs Improvement/Fail)
  - Count of questions using external references

---

### 3. Instruction Following Evaluator (`instruction_following.txt`)

**Purpose:** Evaluates whether student project aligns with instructor's goals and tests stated hypotheses.

**Input**: plan + implementaiton code + code walkthrough + documentation + original instructions

**Output Directory:** `evaluation/`

**Output Files:**
- `goal_matching.ipynb` - Assessment of alignment between student goals and instructor goals
- `hidden_test.ipynb` - Test cases verifying neurons match hypothesized functions
- `eval_summary_ts.ipynb` - Short summary of the evaluation

---

### 4. Consistency Evaluator (`consistency_evaluation.txt`)

**Purpose:** Evaluates code correctness, checks result-conclusion consistency, and assesses plan adherence.

**Input**: plan + implementaiton code + code walkthrough + documentation

**Output Directory:** `evaluation/`

**Output Files:**
- `code_critic_evaluation.ipynb` - Code quality metrics:
  - Runnable: Percentage of executable code blocks
  - Correctness: Percentage of correctly implemented blocks
  - Correction Rate: Percentage of blocks initially wrong but later corrected
  - Redundancy: Percentage of duplicate work
  - Irrelevance: Percentage of unnecessary code
- `self_matching.ipynb` - Verification that conclusions match implementation results
- `matching_report` - Report on plan-implementation alignment
- `eval_summary_self.ipynb` - Short evaluation summary

---

### 5. Replicator Model (`replicator_model.txt`)

**Purpose:** Independently replicates experiment results without copying original code.

**Input**: plan + implementaiton code + code walkthrough

**Output Directory:** `evaluations/replications/` (timestamped subdirectory)

**Output Files:**
- `replication.ipynb` - Reimplementation notebook with independent code
- `documentation_replication.md` - New documentation of replicated work including:
  - Goal, Data, Method, Results, Analysis
- `evaluation_replication.md` - Reflection and quantitative scores (1-5 scale):
  - Implementation Reconstructability
  - Environment Reproducibility
  - Result Fidelity
  - Determinism/Seed Control
  - Error Transparency
  - Final Replication Score (mean of above)

---

### 6. Replicator-Documentation Evaluator (`replicator_evaluator.txt`)

**Purpose:** Verifies that replicated results and conclusions match the original experiment.

**Input**: plan + implementaiton code + code walkthrough + documentation + replications

**Output Directory:** `evaluations/replication/` (same directory as documentation_replication.md)

**Output Files:**
- `documentation_evaluation_summary.md` - Comparison report containing:
  - Results comparison (metrics, figures, statements)
  - Conclusions comparison
  - External/hallucinated information detection
  - Documentation Match Score (1-5 scale) across:
    - Result Fidelity
    - Conclusion Consistency
    - External Reference Discipline
  - Final decision (Pass / Revise)

## Notices
The evaluations will be in the repo you want to evaluate. There will be another copied saved in another dir under runs. 


