# Contributing to MechEvalAgent

Thanks for helping improve **MechEvalAgent: Grounded Evaluation of Research Agents in Mechanistic Interpretability**. This document captures how changes flow through the repository and what we look for in pull requests. If you are unsure about any step, open an issue before investing significant effort.

## 1. Ground Rules
- Keep discussions constructive, document your reasoning, and assume good intent.
- Prefer small, reviewable pull requests (PRs) that focus on one feature or bug fix.
- Avoid committing generated artifacts under `runs/`, `logs/`, or large `.ipynb_checkpoints`; these directories should only contain reproducible outputs from automation scripts.

## 2. Repository Tour
- `run_experiment.sh` — launches circuit-analysis experiments (see README for arguments).
- `run_critic.sh` — orchestrates the full evaluation pipeline (consistency, instruction following, question design, replication).
- `evaluation_prompt_construct.py` — fills prompt templates for evaluators and replicators.
- `prompts/`, `notebooks/` — source assets that should remain readable and lightly versioned. Please trim notebook outputs before committing.
- `runs/`, `logs/` — Git-tracked for reference, but contributors should avoid editing historical outputs unless they are fixing something reproducible.

## 3. Environment Setup
Use Python 3.10+ with `pip`. The repository now contains a `requirements.txt`, so a typical bootstrap flow is:

```bash
git clone <your-fork-url>
cd critic_model_mechinterp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Add any new dependency you introduce to both `requirements.txt` and the README so other researchers can reproduce your work.

## 4. Development Workflow
1. **Create an issue** describing the change (bug, feature, or documentation). Reference relevant prompts or evaluation stages.
2. **Branching**: `git checkout -b feature/<short-description>`.
3. **Implementation**:
   - Keep Python code formatted with `black` or `ruff format` and type-check critical modules with `mypy` when feasible.
   - Shell scripts should be POSIX/Bash compatible and include `set -euo pipefail`.
   - When editing notebooks, clear long logs and rely on markdown or short cells for explanations.
4. **Documentation**: Update `README.md`, prompt templates, or inline comments so that others can rerun the pipeline with your changes.

## 5. Testing and Validation
- **Experiments**: Use `./run_experiment.sh --prompts <prompt_paths>` to confirm circuit runs still succeed.
- **Evaluation stages**: For new prompts or pipeline changes run a targeted subset, e.g.:
  ```bash
  ./run_critic.sh --prompts prompts/<task>/consistency_evaluation.txt
  ```
  Include only the prompts your PR affects to keep runtimes manageable.
- **Prompt construction**: If you modify prompt templates or `evaluation_prompt_construct.py`, regenerate one example via:
  ```bash
  python evaluation_prompt_construct.py \
    --task_name <task> \
    --repo_path runs/<example_run> \
    --system_prompt_path prompts/<task>/system.txt
  ```
- Capture the relevant command outputs (or a summary) in the PR description so reviewers know what you ran.

## 6. Submitting a Pull Request
1. Rebase on the latest `main` (or `master`) branch and resolve conflicts locally.
2. Verify that only the intended files are staged (`git status` should be clean besides your changes).
3. Push your branch and open a PR that includes:
   - Problem statement and motivation.
   - Description of the solution, including new prompts, scripts, or evaluations.
   - How you tested the change (commands + results).
   - Follow-up work or known limitations.
4. Respond to review feedback promptly. If you force-push, leave a short comment summarizing what changed since the last review.

## 7. Security and API Keys
- Never commit API keys, access tokens, or private datasets. Use environment variables or `.env` files that you keep out of git.
- When sharing logs, scrub sensitive metadata (model keys, email addresses, etc.).

## 8. Getting Help
- For implementation questions, open a GitHub Discussion or issue tagged with the relevant component (`prompts`, `evaluation`, etc.).
- For private matters (security disclosures, responsible AI concerns), contact the maintainers directly via the email address in the README or repository profile.

Thank you for strengthening the automated research agent evaluation ecosystem!
