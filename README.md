# MechEvalAgent: Grounded Evaluation of Research Agents in Mechanistic Interpretability

We introduce MechEvalAgents as the first step towards rethinking research evaluation.
<img width="895" height="497" alt="Screenshot 2025-11-17 at 13 09 37" src="https://github.com/user-attachments/assets/d9cb45b0-bc99-4f9f-bc4c-318b005911eb" />

## Unified Research Agent Outputs
We argue that research agents should produce a unified set of outputs, organized around the same scientific reasoning process that humans follow.  A research trace should include:
* **Plan** outlining the hypothesis, methodology, and expected outcomes.
* **Code Implementation** that executes the plan and produces interpretable intermediate outputs.
* **Code Walkthrough** explaining how the code works and how to run it.
* **Research Report** documenting the goal, data, methods, results, analysis, and final conclusions.

## Evaluation Pipeline

* **Consistency Evaluator** verifies code correctness and result-conclusion matching
* **Instruction Following Evaluator** checks goal alignment and hypothesis testing
* **Replication**
    * **Replicator** independently replicates the experiment
    * **Replicator-Documentation Evaluator** verifies replication fidelity
* **Generalization** 
    * **Question Designer** creates assessment questions from documentation
    * **Student** (or model) answers the questions
    * **Grader** evaluates answers and detects external references

## Implementation

The pipeline uses two main scripts:
- **`run_experiment.sh`** - For running initial experiments
- **`run_critic.sh`** - For running all evaluations, questions, replications, and grading

### Common Options

Both scripts accept the following arguments:

- `--prompts`: Comma-separated list of prompt files to execute
- `--providers`: Comma-separated list of providers (e.g., `claude,gemini,codex`) [default: `claude`]
- `--concurrent`: Max concurrent sessions per provider [default: `3`]
- `--push`: Create a git branch and push results to remote [default: `false`]

**Example with push:**
```bash
./run_experiment.sh --prompts prompts/task/circuit_prompt.txt --push
# This will create a branch named "experiment-results-YYYY-MM-DD_HH-MM-SS" and push the results
```

### Step 1: Run Initial Experiments

Execute experiments with your circuit analysis tasks using `run_experiment.sh`:

```bash
./run_experiment.sh --prompts prompts/<task_name>/circuit_prompt.txt
```

This generates the initial experimental results in a timestamped directory under `runs/`.

### Step 2: Construct Evaluation Prompts

Generate evaluation prompts using the output repository from Step 1:

```bash
python evaluation_prompt_construct.py \
  --task_name <task_name> \
  --repo_path <path_to_experiment_output> \
  --system_prompt_path <path_to_system_prompt>
```

This creates filled prompt templates in `prompts/<task_name>/` for the evaluators.

### Step 3: Run Critic Evaluations

Use `run_critic.sh` to run consistency evaluation, instruction following, question design, and replication:

```bash
./run_critic.sh --prompts prompts/<task_name>/consistency_evaluation.txt,prompts/<task_name>/instruction_following.txt,prompts/<task_name>/exam_designer.txt,prompts/<task_name>/replicator_model.txt
```

**Important: Instruction Following Variants**

Choose the appropriate instruction following prompt based on your task:
- **`instruction_following.txt`** - Use when evaluating if the model **tests existing hypotheses**
- **`instruction_following_l3.txt`** - Use when evaluating if the model **comes up with and refines new hypotheses**

This step generates:
- Consistency evaluation results (`evaluation/`)
- Instruction following evaluation (`evaluation/`)
- Question files for testing understanding (`exam/`)
- Replication attempts (`evaluations/replications/`)

### Step 4: Construct Student and Replicator Evaluator Prompts

After replication results are generated, create prompts for student evaluation and replicator grading:

```bash
# For replicator evaluator prompt
python evaluation_prompt_construct.py \
  --skip_replication True \
  --task_name <task_name> \
  --repo_path <path_to_experiment_output> \
  --replication_path <path_to_replication_output>

# For student prompt
python evaluation_prompt_construct.py \
  --student True \
  --task_name <task_name> \
  --exam_path <path_to_exam_file> \
  --documentation_path <path_to_documentation>
```

### Step 5: Run Student Evaluation

Use `run_critic.sh` to have coding agents complete the question:

```bash
./run_critic.sh --prompts prompts/<task_name>/student.txt
```

**Alternative: General Models** (non-coding agents)

For general models, use the student simulator:
```bash
python student/student_simulator.py \
  --model <model_name> \
  --exam_file <path_to_exam> \
  --documentation <path_to_docs>
```

### Step 6: Grade and Evaluate Replicator

Use `run_critic.sh` for final grading and replicator evaluation:

```bash
./run_critic.sh --prompts prompts/<task_name>/replicator_evaluator.txt,prompts/<task_name>/grader.txt
```

This evaluates:
- Student's answers using the Grader (`exam/grade/`)
- Replication fidelity using the Replicator-Documentation Evaluator (`evaluations/replication/`)

## Evaluation Processes and Output Files

### Required Input Files

The input of our evaluation pipeline is [unified outputs](#unified-research-agent-outputs) of research agents.

**Note:** We recommend using Jupyter notebooks for implementation to enable better quantitative analysis by the Consistency Evaluator. 

### 1. Consistency Evaluator (`consistency_evaluation.txt`)

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


### 2. Instruction Following Evaluator (`instruction_following.txt`)

**Purpose:** Evaluates whether student project aligns with instructor's goals and tests stated hypotheses.

**Input**: plan + implementaiton code + code walkthrough + documentation + original instructions

**Output Directory:** `evaluation/`

**Output Files:**
- `goal_matching.ipynb` - Assessment of alignment between student goals and instructor goals
- `hidden_test.ipynb` - Test cases verifying neurons match hypothesized functions
- `eval_summary_ts.ipynb` - Short summary of the evaluation

---

### 3. Replicator Model (`replicator_model.txt`)

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

### 3.a. Replicator-Documentation Evaluator (`replicator_evaluator.txt`)

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

### 4. Question Designer (`exam_designer.txt`)

**Purpose:** Creates comprehensive assessments from research documentation to test understanding of documented facts and ability to apply concepts.

**Input**: plan + implementaiton code + code walkthrough + documentation

**Output Directory:** `exam/`

**Output Files:**
- `exam_documentation.ipynb` - Notebook containing generated questions and gold answers
- `exam_{task_name}.json` - Structured question data in JSON format
  - Contains: question type (multiple-choice or free-generation), question text, correct answer, choices (if applicable), and reference to documentation section

---
### 4.b. Student (`student.txt`)

**Purpose:** take the test

**Input**: documentation + question

**Output Directory:** `exam/`

**Output Files:**
- `student_answer.ipynb`: all the answers to the questions

Note: You can also use `student_simulator.ipynb` to pass in non code-agent model by using your API key.

---

### 4.b. Grader (`grader.txt`)

**Purpose:** Evaluates student answers to questions, checking both correctness and whether answers rely only on provided documentation.

**Input**: questions + student's answers + documentation

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

## Notices
The evaluations will be in the repo you want to evaluate. There will be another copied saved in another dir under runs. 

## Citation
If you find our repo helpful, please cite:
```
@software{mechinterp_evaluate_agent,
  title={MechEvalAgents: Grounded Evaluation of Research Agents in Mechanistic Interpretability},
  author={Xiaoyan Bai},
  year={2025},
  url={https://github.com/ChicagoHAI/MechEvalAgents}
}
```

