# openAI initialization
import openai
import json
import argparse
from os import path
from student_instruction import STUDENT_SYSTEM_PROMPT, STUDENT_USER_PROMPT
# from api import OPENAI_API_KEY

parser = argparse.ArgumentParser()
parser.add_argument("--test_dir", type=str, default="YOUR REPO")
parser.add_argument("--report_path", type=str, default="YOUR DOCUMENTATION FILE")
parser.add_argument("--question_path", type=str, default="YOUR EXAM FILE")
parser.add_argument("--model_id", type=str, default="gpt-4o-mini")
args = parser.parse_args()

TEST_DIR = args.test_dir
report_path = args.report_path
question_path = args.question_path
model_id = args.model_id

openai.api_key = "YOUR API KEY"

with open(report_path, "r", encoding="utf-8") as f:
    report = f.read()

def instruct_model(model_id, prompts):
    response = openai.chat.completions.create(
        model=model_id, 
        
        messages = [
                {"role": "system", "content": STUDENT_SYSTEM_PROMPT.format(documentation=report)},
                {"role": "user", "content": prompt}
            ]
        )
    
    answer = response.choices[0].message.content.strip()  # Extract and clean the response
    return answer

if __name__ == "__main__":

    with open(question_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    results = []
    for question in questions:
        if question["question_type"] == "multiple_choice":
            question_text = question["question"] + "Choices:\n" + "\n".join([f"{choice}" for choice in enumerate(question["choices"])])
            prompt = STUDENT_USER_PROMPT.format(question=question_text)
            answer = instruct_model(model_id, prompt)
            print(answer)
        elif question["question_type"] == "free_generation":
            prompt = STUDENT_USER_PROMPT.format(question=question["question"])
            answer = instruct_model(model_id, prompt)
            print(answer)
        else:
            raise ValueError(f"Unsupported question type: {question['question_type']}")

        results.append({
            "question_type": question["question_type"],
            "question": question["question"],
            "student_answer": answer,
            "gold_answer": question["answer"]
        })
        

    with open(path.join(TEST_DIR, "exam/student_results_ioi.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
