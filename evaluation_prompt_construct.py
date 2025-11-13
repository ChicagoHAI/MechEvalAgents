import sys
import os
import argparse
from pathlib import Path

def fill_evaluation_prompts(repo_path, task_name, system_prompt_path=None, replication_path=None, skip_replication=False):
    """
    Fill in REPO_PATH, SYSTEM_PROMPT_PATH, and REPLICATION_PATH in evaluation prompt files.

    Args:
        repo_path: Path to the repository
        system_prompt_path: Path to system prompt (for instruction_following.txt)
        replication_path: Path to replication output (for replicator_evaluator.txt)
    """
    prompts_dir =  "prompts/templates"
    output_dir = f"prompts/{task_name}"
    os.makedirs(output_dir, exist_ok=True)

    evaluation_prompts = [
        "consistency_evaluation.txt",
        "exam_designer.txt",
        "instruction_following.txt",
        "replicator_model.txt",
        "grader.txt"
    ]

    if skip_replication:
        evaluation_prompts = ["replicator_evaluator.txt"]
    
    if student:
        evaluation_prompts = ["student.txt"]

    print(f"Filling prompts with REPO_PATH: {repo_path}\n")

    for prompt_file in evaluation_prompts:
        template_path = f"{prompts_dir}/{prompt_file}"
        if not os.path.exists(template_path):
            continue

        text = open(template_path, "r").read()

        # Build replacements based on the specific file
        replacements = {"REPO_PATH": repo_path}

        if prompt_file == "instruction_following.txt" or prompt_file == "instruction_following_l3.txt":
            replacements["SYSTEM_PROMPT"] = system_prompt_path or ""

        if prompt_file == "replicator_evaluator.txt":
            replacements["REPLICATION_PATH"] = replication_path or ""

        if prompt_file == "student.txt":
            replacements["EXAM_PATH"] = exam_path or ""
            replacements["DOCUMENTATION_PATH"] = documentation_path or ""
        
        filled = text.format(**replacements)

        
        output_path = f"{output_dir}/{prompt_file}"
        with open(output_path, "w") as f:
            f.write(filled)
        print(f"✅ {prompt_file}")

    print(f"\nDone! Saved to: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--replication", type=bool, default=False)
    parser.add_argument("--task_name", type=str, default="ioi_l2")
    parser.add_argument("--repo_path", type=str, default="YOUR REPO")
    parser.add_argument("--system_prompt_path", type=str, default="YOUR SYSTEM PROMPT")
    parser.add_argument("--replication_path", type=str, default="YOUR REPLICATION PATH")

    parser.add_argument("--student", type=bool, default=False)
    parser.add_argument("--exam_path", type=str, default="YOUR EXAM PATH")
    parser.add_argument("--documentation_path", type=str, default="YOUR DOCUMENTATION PATH")


    args = parser.parse_args()
    skip_replication = args.skip_replication
    task_name = args.task_name
    repo_path = args.repo_path
    system_prompt_path = args.system_prompt_path
    replication_path = args.replication_path


    fill_evaluation_prompts(repo_path, task_name, system_prompt_path, replication_path)
