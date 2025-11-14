#!/usr/bin/env python3
"""
ICoT Replication Script: Linear Regression Probing
Replicates the experiment from probe_c_hat.py
"""

import os
import sys
os.chdir('/home/smallyan/critic_model_mechinterp/icot')
sys.path.insert(0, '/home/smallyan/critic_model_mechinterp/icot')

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 80)
print("ICoT REPLICATION: Linear Regression Probing")
print("=" * 80)

# Check GPU availability
print(f"\nCUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    device = "cuda"
else:
    print("Warning: Running on CPU - this will be slow")
    device = "cpu"

# Import model utilities
from src.model_utils import load_hf_model, load_c_hat_model
from src.HookedModel import convert_to_hooked_model
from src.ActivationCache import record_activations
from src.probes import RegressionProbe

print("\nSuccessfully imported custom modules")

# Load ICoT model
BASE_DIR = "/home/smallyan/critic_model_mechinterp/icot"
# Model checkpoint is in external storage
model_path = "/net/scratch2/smallyan/icot/train_models/4_by_4_mult/gpt2/finetune_2L4H_layer2/checkpoint_12"
config_path = os.path.join(model_path, "config.json")
state_dict_path = os.path.join(model_path, "state_dict.bin")

print("\n" + "-" * 80)
print("STEP 1: Loading Models")
print("-" * 80)
print("Loading ICoT model...")
icot_model, tokenizer = load_hf_model(config_path, state_dict_path, cpu=(device=="cpu"))
icot_model.to(device).eval()
convert_to_hooked_model(icot_model)
print("ICoT model loaded successfully")

# Load SFT model
print("\nLoading SFT model...")
sft_model_path = os.path.join(BASE_DIR, "ckpts/vanilla_ft/ckpt.pt")
try:
    sft_model, _ = load_c_hat_model(sft_model_path)
    sft_model.to(device).eval()
    print("SFT model loaded successfully")
    has_sft = True
except Exception as e:
    print(f"Warning: Could not load SFT model: {e}")
    has_sft = False

# Load validation data
print("\n" + "-" * 80)
print("STEP 2: Loading and Preparing Data")
print("-" * 80)
data_path = os.path.join(BASE_DIR, "data/processed_valid.txt")

with open(data_path, "r") as f:
    texts = f.readlines()

# Parse operands from file format
texts = [
    text.replace(" ", "").replace("\n", "").split("||")[0].split("*")
    for text in texts
    if text != "\n"
]

# Convert to correct decimal order
operands = [(int(a[::-1]), int(b[::-1])) for a, b in texts]

print(f"Loaded {len(operands)} multiplication problems")
print(f"Example: {operands[0][0]} × {operands[0][1]} = {operands[0][0] * operands[0][1]}")

# Create input prompts
def multiply(a: int, b: int, return_reverse=False) -> str:
    """Multiply a, b, optionally return the result in reverse order."""
    ans = str(a * b)
    if return_reverse:
        return ans[::-1]
    return ans

def prompt_ci_operands(operands, i, tokenizer, device="cpu"):
    """Generate prompts for c_i position."""
    answers = [multiply(a, b, return_reverse=True) for a, b in operands]
    suffixes = ["" for _ in answers]
    if i >= 1:
        suffixes = [" " + " ".join(ans[:i]) for ans in answers]

    prompt_txts = [
        " " + " ".join(str(a))[::-1] + " * " + " ".join(str(b))[::-1] + " "
        for a, b in operands
    ]
    eos = tokenizer.eos_token
    prompt_txts = [
        f"{txt}{eos}{eos} ####{suffix}" for txt, suffix in zip(prompt_txts, suffixes)
    ]

    prompt_token_ids = tokenizer(prompt_txts, return_tensors="pt", padding=True).input_ids
    prompt_token_ids = prompt_token_ids.to(device)
    return prompt_txts, prompt_token_ids

# Create prompts with full answer (i=8 for 8-digit output)
prompt_text, tokens = prompt_ci_operands(operands, 8, tokenizer, device=device)
print(f"\nCreated {len(tokens)} prompts")

# Compute ground truth labels
print("\n" + "-" * 80)
print("STEP 3: Computing Ground Truth Labels (c_hat values)")
print("-" * 80)

def get_c_hats(a, b):
    """Compute running sums (c_hat) for multiplication of a and b."""
    c_hats = []
    carrys = []
    pair_sums = []

    # Convert to digit arrays (least significant first)
    a_digits = [int(d) for d in str(a)[::-1]]
    b_digits = [int(d) for d in str(b)[::-1]]
    total_len = len(a_digits) + len(b_digits)

    for ii in range(total_len):
        aibi_sum = 0
        # Sum products along the diagonal ii
        for a_ii in range(ii, -1, -1):
            b_ii = ii - a_ii
            if 0 <= a_ii < len(a_digits) and 0 <= b_ii < len(b_digits):
                aibi_sum += a_digits[a_ii] * b_digits[b_ii]

        pair_sums.append(aibi_sum)

        # Add carry from previous running sum
        if len(c_hats) > 0:
            aibi_sum += c_hats[-1] // 10

        c_hats.append(aibi_sum)
        carrys.append(aibi_sum // 10)

    return c_hats, carrys, pair_sums

# Compute labels for all operands
labels = []
for a, b in operands:
    c_hats, carrys, pair_sums = get_c_hats(a, b)
    labels.append(c_hats)

labels = torch.tensor(labels, dtype=torch.float32)
print(f"Computed labels shape: {labels.shape}")

# Split data
print("\n" + "-" * 80)
print("STEP 4: Splitting Data (Train/Val)")
print("-" * 80)
torch.manual_seed(123)  # For reproducibility
shuffle_idx = torch.randperm(len(tokens))
tokens = tokens[shuffle_idx]
labels = labels[shuffle_idx]

val_size = 1024
val_tokens = tokens[-val_size:].to(device)
val_labels = labels[-val_size:].to(device)

train_tokens = tokens[:-val_size].to(device)
train_labels = labels[:-val_size].to(device)

print(f"Training samples: {len(train_tokens)}")
print(f"Validation samples: {len(val_tokens)}")

# Record activations
print("\n" + "-" * 80)
print("STEP 5: Recording Activations from Models")
print("-" * 80)

hook_modules = [
    "0.hook_resid_mid",
    "0.hook_resid_post",
    "1.hook_resid_mid",
    "1.hook_resid_post",
]

print("Recording validation activations from ICoT model...")
with torch.no_grad():
    with record_activations(icot_model, hook_modules) as cache:
        _ = icot_model(val_tokens)

# Stack activations: [num_modules, batch, seq_len, hidden_dim]
val_acts = torch.stack(
    [cache[m][:, -val_labels.shape[1]:] for m in hook_modules],
    dim=0,
)

print(f"Validation activations shape: {val_acts.shape}")

# Train or load probes
print("\n" + "-" * 80)
print("STEP 6: Loading/Training Linear Probes")
print("-" * 80)

num_modules, val_batch_size, seq, d_model = val_acts.shape
probe_shape = (num_modules, seq, d_model, 1)

# Try to load pre-trained ICoT probe
probe_path = os.path.join(BASE_DIR, "ckpts/icot_c_hat_probe/probe.pth")
icot_probe = RegressionProbe(probe_shape, 1e-3)

if os.path.exists(probe_path):
    print(f"Loading pre-trained ICoT probe from {probe_path}")
    icot_probe.load_weights(probe_path)
else:
    print("Pre-trained ICoT probe not found. Training new probe...")
    print("Recording training activations...")
    with torch.no_grad():
        with record_activations(icot_model, hook_modules) as cache:
            _ = icot_model(train_tokens)

    train_acts = torch.stack(
        [cache[m][:, -train_labels.shape[1]:] for m in hook_modules],
        dim=0,
    )

    print("Training probe (100 epochs)...")
    for epoch in range(100):
        loss = icot_probe.train_step(train_acts, train_labels)
        if (epoch + 1) % 20 == 0:
            print(f"Epoch {epoch+1}/100, Loss: {loss:.4f}")

# Try to load pre-trained SFT probe
sft_probe_path = os.path.join(BASE_DIR, "ckpts/sft_c_hat_probe/probe.pth")
sft_probe = RegressionProbe(probe_shape, 1e-3)

if has_sft and os.path.exists(sft_probe_path):
    print(f"\nLoading pre-trained SFT probe from {sft_probe_path}")
    sft_probe.load_weights(sft_probe_path)
    has_sft_probe = True
else:
    print("\nWarning: Pre-trained SFT probe not found. Skipping SFT comparison.")
    has_sft_probe = False

# Evaluate probes
print("\n" + "-" * 80)
print("STEP 7: Evaluating Probes")
print("-" * 80)

print("Evaluating ICoT probe...")
with torch.no_grad():
    icot_val_preds = icot_probe(val_acts)

icot_metrics = icot_probe.evaluate_probe(val_acts, val_labels)
icot_mae = icot_metrics[-1][2]  # Extract MAE for layer 1 post-residual

print(f"\nICoT MAE by digit position:")
for i, mae in enumerate(icot_mae):
    print(f"  c{i}: {mae:.3f}")

if has_sft_probe:
    print("\nEvaluating SFT probe...")
    with torch.no_grad():
        sft_val_preds = sft_probe(val_acts)

    sft_metrics = sft_probe.evaluate_probe(val_acts, val_labels)
    sft_mae = sft_metrics[-1][2]

    print(f"\nSFT MAE by digit position:")
    for i, mae in enumerate(sft_mae):
        print(f"  c{i}: {mae:.3f}")
else:
    sft_val_preds = None
    sft_mae = None

# Visualize results
print("\n" + "-" * 80)
print("STEP 8: Creating Visualizations")
print("-" * 80)

val_labels_np = val_labels.cpu().numpy()
icot_val_preds_np = icot_val_preds.cpu().numpy()

if sft_val_preds is not None:
    sft_val_preds_np = sft_val_preds.cpu().numpy()
    n_rows = 2
else:
    n_rows = 1

n_cols = 5
fig, axes = plt.subplots(
    n_rows, n_cols, figsize=(15, 3*n_rows), gridspec_kw={"hspace": 0.4}
)

if n_rows == 1:
    axes = axes.reshape(1, -1)

for row in range(n_rows):
    if row == 0 and sft_val_preds is not None:
        probe_preds = sft_val_preds_np
        metrics = sft_mae
        model_name = "SFT"
    else:
        probe_preds = icot_val_preds_np
        metrics = icot_mae
        model_name = "ICoT"

    for col_idx, c_i in enumerate(range(2, 7)):
        ax = axes[row, col_idx]
        _val_labels = val_labels_np[:, c_i]
        _val_preds = probe_preds[2, :, c_i]  # Layer 1 mid-residual

        min_val = min(_val_labels.min(), _val_preds.min())
        max_val = max(_val_labels.max(), _val_preds.max())
        diagonal_line = np.linspace(min_val, max_val, 100)

        sorted_indices = np.argsort(_val_labels)
        sorted_labels = _val_labels[sorted_indices]
        sorted_preds = _val_preds[sorted_indices]

        mae = metrics[c_i]

        ax.plot(
            diagonal_line,
            diagonal_line,
            "r--",
            alpha=0.7,
            linewidth=2,
            label="Perfect predictions",
        )

        ax.scatter(
            sorted_labels,
            sorted_preds,
            alpha=0.5,
            s=5,
            label="Predictions",
            color="blue",
        )
        ax.set_title(f"{model_name}: c_hat_{c_i} (MAE {mae:.2f})", fontsize=12)

        if row == n_rows - 1:
            ax.set_xlabel(f"True c_hat_{c_i}", fontsize=11)

        if col_idx == 0:
            ax.set_ylabel(f"Predicted c_hat", fontsize=11)
            if row == 0:
                ax.legend(fontsize=9)
        ax.set_aspect("equal", adjustable="box")

plt.tight_layout()
output_path = "evaluation/replications/probe_results.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"Saved visualization to {output_path}")

# Summary
print("\n" + "=" * 80)
print("REPLICATION RESULTS SUMMARY")
print("=" * 80)

print("\nICoT Model - Mean Absolute Error by digit:")
for i in range(2, 7):
    print(f"  c_hat_{i}: {icot_mae[i]:.3f}")
print(f"  Average (c2-c6): {icot_mae[2:7].mean():.3f}")

if sft_mae is not None:
    print("\nSFT Model - Mean Absolute Error by digit:")
    for i in range(2, 7):
        print(f"  c_hat_{i}: {sft_mae[i]:.3f}")
    print(f"  Average (c2-c6): {sft_mae[2:7].mean():.3f}")

    print("\nImprovement (SFT MAE - ICoT MAE):")
    for i in range(2, 7):
        improvement = sft_mae[i] - icot_mae[i]
        print(f"  c_hat_{i}: {improvement:.3f} ({improvement/sft_mae[i]*100:.1f}% better)")

print("\n" + "=" * 80)
print("INTERPRETATION:")
print("Lower MAE indicates the model better represents intermediate values.")
print("ICoT should show significantly lower MAE than SFT, confirming it")
print("learns to represent running sums during multiplication.")
print("=" * 80)

print("\nReplication completed successfully!")
