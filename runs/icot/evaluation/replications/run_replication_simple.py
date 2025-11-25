#!/usr/bin/env python3
"""
ICoT Replication Script: Simplified Model Inference Test
This script replicates the basic functionality of the ICoT model by:
1. Loading the model
2. Processing input data
3. Generating predictions
4. Computing accuracy metrics
"""

import os
import sys
os.chdir('/home/smallyan/critic_model_mechinterp/icot')
sys.path.insert(0, '/home/smallyan/critic_model_mechinterp/icot')

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("=" * 80)
print("ICoT REPLICATION: Model Inference and Accuracy Test")
print("=" * 80)

# Check GPU
print(f"\nCUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    device = "cuda"
else:
    device = "cpu"

# Import utilities
from src.model_utils import load_hf_model
from src.data_utils import read_operands, format_operands, multiply, get_ci_from_operands

print("\n" + "-" * 80)
print("STEP 1: Loading ICoT Model")
print("-" * 80)

BASE_DIR = "/home/smallyan/critic_model_mechinterp/icot"
model_path = "/net/scratch2/smallyan/icot/train_models/4_by_4_mult/gpt2/finetune_2L4H_layer2/checkpoint_12"
config_path = os.path.join(model_path, "config.json")
state_dict_path = os.path.join(model_path, "state_dict.bin")

print(f"Loading model from: {model_path}")
model, tokenizer = load_hf_model(config_path, state_dict_path, cpu=(device=="cpu"))
model.to(device).eval()
print("Model loaded successfully!")
print(f"Model config: {model.config}")

print("\n" + "-" * 80)
print("STEP 2: Loading and Preparing Data")
print("-" * 80)

data_path = os.path.join(BASE_DIR, "data/processed_valid.txt")
operands = read_operands(data_path, flip_operands=False, as_int=True)
print(f"Loaded {len(operands)} multiplication problems")
print(f"Example operand pair: {operands[0]}")
print(f"Expected result: {operands[0][0]} × {operands[0][1]} = {operands[0][0] * operands[0][1]}")

# Format operands for model input
tokens = format_operands(operands, tokenizer, flip_operands=False, add_special_tokens=True)
print(f"Tokenized input shape: {tokens.input_ids.shape}")

print("\n" + "-" * 80)
print("STEP 3: Generating Predictions")
print("-" * 80)

# Generate predictions for a sample
num_samples = min(100, len(operands))
print(f"Generating predictions for {num_samples} samples...")

correct_digits = [0] * 8  # Track correct digits at each position
total_correct = 0

with torch.no_grad():
    for i in range(num_samples):
        # Get single example
        input_ids = tokens.input_ids[i:i+1].to(device)

        # Generate output
        try:
            output = model.generate(
                input_ids,
                max_new_tokens=30,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )

            # Decode output
            generated_text = tokenizer.decode(output[0], skip_special_tokens=False)

            # Extract answer (after ####)
            if "####" in generated_text:
                predicted_answer = generated_text.split("####")[1].strip()
                # Remove spaces and get digits
                predicted_digits = predicted_answer.replace(" ", "").replace(tokenizer.eos_token, "")

                # Compute true answer (in reverse order)
                true_answer = multiply(operands[i][0], operands[i][1], return_reverse=True)

                # Compare
                is_correct = (predicted_digits[:len(true_answer)] == true_answer)
                if is_correct:
                    total_correct += 1

                # Track digit-wise accuracy
                for j in range(min(len(predicted_digits), len(true_answer))):
                    if j < len(predicted_digits) and j < len(true_answer):
                        if predicted_digits[j] == true_answer[j]:
                            correct_digits[j] += 1

                if i < 5:  # Print first 5 examples
                    print(f"\nExample {i+1}:")
                    print(f"  Input: {operands[i][0]} × {operands[i][1]}")
                    print(f"  True answer: {true_answer}")
                    print(f"  Predicted: {predicted_digits[:len(true_answer)]}")
                    print(f"  Correct: {is_correct}")

        except Exception as e:
            print(f"Error generating for sample {i}: {e}")
            continue

        if (i + 1) % 20 == 0:
            print(f"Processed {i + 1}/{num_samples} samples...")

print("\n" + "-" * 80)
print("STEP 4: Computing Accuracy Metrics")
print("-" * 80)

overall_accuracy = total_correct / num_samples
print(f"\nOverall Accuracy: {overall_accuracy:.2%} ({total_correct}/{num_samples})")

print(f"\nDigit-wise Accuracy:")
for i in range(8):
    digit_accuracy = correct_digits[i] / num_samples
    print(f"  Position c{i}: {digit_accuracy:.2%} ({correct_digits[i]}/{num_samples})")

print("\n" + "-" * 80)
print("STEP 5: Creating Visualization")
print("-" * 80)

# Plot digit-wise accuracy
fig, ax = plt.subplots(figsize=(10, 6))
positions = list(range(8))
accuracies = [correct_digits[i] / num_samples for i in range(8)]

ax.bar(positions, accuracies, color='steelblue', alpha=0.7)
ax.set_xlabel('Digit Position', fontsize=12)
ax.set_ylabel('Accuracy', fontsize=12)
ax.set_title('ICoT Model: Digit-wise Accuracy', fontsize=14, fontweight='bold')
ax.set_xticks(positions)
ax.set_xticklabels([f'c{i}' for i in range(8)])
ax.set_ylim([0, 1])
ax.axhline(y=overall_accuracy, color='r', linestyle='--', label=f'Overall: {overall_accuracy:.2%}')
ax.legend()
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
output_path = "evaluation/replications/accuracy_results.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"Saved visualization to {output_path}")

print("\n" + "=" * 80)
print("REPLICATION RESULTS SUMMARY")
print("=" * 80)
print(f"\nTested on {num_samples} samples from validation set")
print(f"Overall accuracy: {overall_accuracy:.2%}")
print(f"\nDigit accuracy by position:")
for i in range(8):
    print(f"  c{i}: {accuracies[i]:.2%}")

print("\n" + "=" * 80)
print("INTERPRETATION:")
print("The ICoT model should achieve high accuracy on 4×4 digit multiplication.")
print("Digit-wise accuracy shows which positions are harder to predict.")
print("Lower accuracy at later positions indicates increased difficulty with")
print("carrying and accumulating errors.")
print("=" * 80)

print("\nReplication completed successfully!")

# Save results to file
with open("evaluation/replications/results_summary.txt", "w") as f:
    f.write("ICoT REPLICATION RESULTS\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Dataset: {num_samples} validation samples\n")
    f.write(f"Overall Accuracy: {overall_accuracy:.4f}\n\n")
    f.write("Digit-wise Accuracy:\n")
    for i in range(8):
        f.write(f"  c{i}: {accuracies[i]:.4f}\n")

print("\nSaved results summary to evaluation/replications/results_summary.txt")
