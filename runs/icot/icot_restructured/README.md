# ICoT Restructured Documentation

This directory contains restructured documentation for the ICoT (Implicit Chain-of-Thought) multiplication research.

## Files

### documentation.md
Complete research documentation following the standardized 7-section format:
1. **Goal** — Research hypothesis and circuit objectives
2. **Data** — Dataset description and formats
3. **Method** — Training procedures and analysis techniques
4. **Results** — Performance metrics and discovered mechanisms
5. **Analysis** — Learning dynamics and hypothesis refinement
6. **Next Steps** — Future research directions
7. **Main Takeaways** — Core insights and implications

### code_walkthrough.md
Comprehensive code walkthrough covering:
- Repository structure and organization
- Setup and installation instructions
- Data pipeline and formatting
- Model architecture details
- Experiment reproduction steps
- Key functions and usage examples
- Best practices and troubleshooting

## Original Repository

The original repository structure is preserved in the parent `icot/` directory:
- `src/` — Source code
- `experiments/` — Experiment scripts
- `data/` — Datasets
- `ckpts/` — Model checkpoints
- `paper_figures/` — Generated figures
- `paper.pdf` — Original research paper

## Paper Reference

**Title:** "Why Can't Transformers Learn Multiplication? Reverse-Engineering Reveals Long-Range Dependency Pitfalls"

**Authors:** Xiaoyan Bai, Itamar Pres, Yuntian Deng, Chenhao Tan, Stuart Shieber, Fernanda Viégas, Martin Wattenberg, Andrew Lee

**Abstract:** This work studies why language models fail at multi-digit multiplication by reverse-engineering a model that successfully learns via implicit chain-of-thought (ICoT). Key findings include: (1) evidence of long-range structure in successful models, (2) mechanisms using attention trees to cache/retrieve partial products, (3) geometric representations via Minkowski sums and Fourier bases, and (4) identification of optimization pitfalls in standard fine-tuning that prevent learning long-range dependencies.

---

*Restructured on: 2025-11-13*  
*Original repository: /home/smallyan/critic_model_mechinterp/icot*
