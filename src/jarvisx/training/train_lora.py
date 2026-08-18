"""Jarvis X: QLoRA Fine-Tuning Script for Local GPU Nodes.

Trains lightweight LoRA adapters on Qwen2.5-Coder-7B or DeepSeek-R1-7B using 4-bit quantization,
and exports directly to GGUF format for 1-click Ollama deployment.
"""

from __future__ import annotations
import os
import sys
import argparse

# Usage:
# python -m jarvisx.training.train_lora --dataset ./jarvis_fine_tune_dataset.jsonl --output ./jarvis_lora_adapter

def train(
    dataset_path: str = "./jarvis_fine_tune_dataset.jsonl",
    base_model: str = "unsloth/qwen2.5-coder-7b-instruct-bnb-4bit",
    output_dir: str = "./jarvis_lora_adapter",
    max_seq_length: int = 4096,
    lora_r: int = 16,
    lora_alpha: int = 16,
    batch_size: int = 2,
    num_epochs: int = 3
):
    """Executes QLoRA fine-tuning with 4-bit quantization and LoRA adapters."""
    print("========================================================")
    print("  🔥 JARVIS X: QLoRA LOCAL GPU FINE-TUNING PIPELINE")
    print("========================================================")
    print(f"  Base Model     : {base_model}")
    print(f"  Dataset Path   : {dataset_path}")
    print(f"  Max Seq Length : {max_seq_length}")
    print(f"  LoRA Rank (r)  : {lora_r} (Alpha: {lora_alpha})")
    print(f"  Output Dir     : {output_dir}")
    print("========================================================\n")

    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import load_dataset
        import torch

        # 1. Load 4-bit Quantized Base Model
        print("[*] Loading 4-bit base model into GPU VRAM...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=base_model,
            max_seq_length=max_seq_length,
            load_in_4bit=True,
        )

        # 2. Add LoRA Adapters
        print("[*] Attaching LoRA rank adapters to target projection layers...")
        model = FastLanguageModel.get_peft_model(
            model,
            r=lora_r,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_alpha=lora_alpha,
            lora_dropout=0.0,
            bias="none",
            use_gradient_checkpointing="unsloth",
        )

        # 3. Load & Format Dataset
        print(f"[*] Loading training dataset from '{dataset_path}'...")
        dataset = load_dataset("json", data_files=dataset_path, split="train")

        # 4. Configure Trainer
        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=dataset,
            dataset_text_field="text",
            max_seq_length=max_seq_length,
            args=TrainingArguments(
                per_device_train_batch_size=batch_size,
                gradient_accumulation_steps=4,
                warmup_steps=5,
                max_steps=60,
                learning_rate=2e-4,
                fp16=not torch.cuda.is_bf16_supported(),
                bf16=torch.cuda.is_bf16_supported(),
                logging_steps=1,
                optim="adamw_8bit",
                output_dir=output_dir,
            ),
        )

        # 5. Run Training
        print("\n🚀 Starting QLoRA Fine-Tuning...")
        trainer.train()
        print(f"\n[+] Fine-tuning complete! Saving adapter to: {output_dir}")
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        # 6. Export to GGUF for Ollama
        print("[*] Exporting model to GGUF format (Q4_K_M)...")
        model.save_pretrained_gguf(f"{output_dir}_gguf", tokenizer, quantization_method="q4_k_m")
        print(f"[+] GGUF exported to {output_dir}_gguf! Load into Ollama via 'ollama create'.")

    except ImportError:
        print("  ℹ️ Unsloth/Torch CUDA not detected on this machine.")
        print("  💡 This script is designed to run directly on Worker Node 1 (NVIDIA RTX 3050) or Google Colab.")
        print("  💡 Dataset is prepared and ready for execution on your GPU worker node!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jarvis X QLoRA Fine-Tuning")
    parser.add_argument("--dataset", type=str, default="./jarvis_fine_tune_dataset.jsonl")
    parser.add_argument("--base_model", type=str, default="unsloth/qwen2.5-coder-7b-instruct-bnb-4bit")
    parser.add_argument("--output", type=str, default="./jarvis_lora_adapter")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Batch size per device")
    parser.add_argument("--lora_r", type=int, default=16, help="LoRA rank dimension")
    args = parser.parse_args()

    train(
        dataset_path=args.dataset,
        base_model=args.base_model,
        output_dir=args.output,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        lora_r=args.lora_r
    )
