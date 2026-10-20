---
title: Benchmarking Linear Solvers in ALS Movie Recommendation
summary: Evaluating the speed, numerical stability, and convergence of five from-scratch linear system solvers in Alternating Least Squares collaborative filtering.
disciplines:
  - data-science
  - research
year: 2026
technologies:
  - Python
  - NumPy
  - Pandas
  - Matplotlib
links:
  - label: GitHub
    url: https://github.com/LeinnarF/Movie-Recommender
  - label: Manuscript
    url: https://github.com/LeinnarF/Movie-Recommender/blob/main/Latex/main.pdf
---

## The Problem

Collaborative filtering powers modern recommendation engines by uncovering shared patterns in user behavior without needing explicit item metadata. One of its workhorse algorithms is **Alternating Least Squares (ALS)**, which factors a sparse user–item rating matrix into low-rank user and item latent vectors. Because optimizing both factor matrices simultaneously is non-convex, ALS alternates between holding one matrix fixed and solving a regularized least-squares subproblem for each row of the other.

While most recommender research focuses on model architectures or regularization schemes, every single ALS iteration has to solve thousands of linear systems of the form `Ax = b`, where `A = W^T W + λI` is a symmetric positive definite (SPD) matrix. We set out to investigate what happens beneath the abstraction layer: how does the choice of linear system solver affect recommendation quality, numerical stability, and training speed?

## The Approach

We built a modular ALS engine in Python and evaluated it on the **MovieLens 100K** benchmark dataset, which contains 100,000 ratings from 943 users across 1,682 movies (93.70% sparsity).

![[movielens-rating-distribution.png|MovieLens 100K Rating Distribution|75%]]

Exploratory analysis confirmed the dataset's characteristic skew: ratings cluster heavily around 3 and 4 stars, and most users rate fewer than 100 films while maintaining an average rating above 3.5. We partitioned the observed ratings into an 80/20 train–test split (80,000 training and 20,000 test interactions) and fixed our ALS hyperparameters across every trial: latent dimension `K = 10`, regularization strength `λ = 10.0`, and `30` training epochs with an identical random seed.

To isolate the numerical and computational behavior of each algorithm without high-level LAPACK wrappers masking the differences, we implemented five linear solvers entirely from scratch:

- **Cholesky Decomposition:** Exploits the symmetric positive definite structure of `A = LL^T` via the Cholesky–Banachiewicz algorithm followed by forward and back substitution.
- **LU Decomposition:** Factors `PA = LU` using Doolittle's algorithm with partial pivoting.
- **QR Decomposition:** Applies Householder reflections (`H = I - 2vv^T`) to orthogonalize the system before back substitution.
- **Gaussian Elimination with Partial Pivoting:** Reduces the augmented matrix `[A | b]` directly to upper-triangular form with row swaps to bound elimination multipliers.
- **Explicit Matrix Inversion:** Computes `A^-1` via Gauss–Jordan elimination on `[A | I]` and multiplies `x = A^-1 b`.

## The Result

![[als-rmse-progression.png|Training and Test RMSE Convergence Across Solvers|95%]]

Across all 30 epochs, the training and test RMSE curves for every solver overlapped completely. All five implementations converged at epoch 26 to the exact same final metrics—**0.806108 Train RMSE** and **0.969133 Test RMSE**—confirming that when the subproblem matrix is well-conditioned, solver choice does not alter recommendation quality.

**ALS Convergence Trajectory (Identical Across Solvers)**

| Epoch | Train RMSE | Test RMSE | Regularized Loss | Mean Condition Number κ(A) |
| ----- | ---------- | --------- | ---------------- | -------------------------- |
| 5     | 0.8533     | 1.0046    | 138,674.65       | 18.87                      |
| 10    | 0.8166     | 0.9767    | 129,916.52       | 15.51                      |
| 15    | 0.8096     | 0.9716    | 128,839.00       | 15.14                      |
| 20    | 0.8073     | 0.9700    | 128,623.42       | 15.09                      |
| 25    | 0.8065     | 0.9694    | 128,569.10       | 15.10                      |
| 30    | 0.8061     | 0.9691    | 128,549.98       | 15.10                      |

![[als-solver-runtime.png|Total Elapsed Time and Relative Speedup by Solver|95%]]

Where the solvers diverged dramatically was computational efficiency. Because ALS solves `943 + 1,682 = 2,625` linear systems per epoch (78,750 solves over 30 epochs), per-solve overhead compounds quickly. **Cholesky decomposition** finished in **18.19 seconds**—a **4.77× speedup** over explicit matrix inversion (86.73 seconds)—because leveraging symmetry and positive definiteness halves the operation count compared to standard Gaussian elimination (`~n^3 / 3` FLOPs). Partial pivoting (25.76s), QR (27.29s), and LU decomposition (28.55s) formed a tight middle tier, each running more than 3× faster than matrix inversion.

![[als-residual-norm.png|Per-Epoch Residual Norm Progression and Solver Precision|95%]]

To evaluate numerical stability, we tracked both the matrix condition number `κ(A)` and the average residual norm `||Ax - b||`. Because regularization (`λ = 10.0`) shifts the eigenvalues of `W^T W` away from zero, the subproblems remained well-conditioned throughout training with a mean `κ(A)` of **15.91**. Even in this well-behaved regime, residual norms exposed clear floating-point precision differences: Cholesky decomposition achieved the tightest residuals (`5.15 × 10^-14`), followed closely by LU and partial pivoting (`5.85 × 10^-14`) and QR (`9.55 × 10^-14`). Explicit matrix inversion accumulated roughly 7× more rounding error (`3.64 × 10^-13`) than Cholesky.

## Evaluation

Summarizing all five solvers side by side makes the engineering tradeoff clear: every method finds the same latent factors, but their computational cost and floating-point accuracy differ substantially.

**Solver Benchmark Summary (30 Epochs, K = 10, λ = 10.0)**

| Solver | Final Train RMSE | Final Test RMSE | Elapsed Time (s) | Relative Speedup | Avg Residual `\|\|Ax - b\|\|` |
| --- | --- | --- | --- | --- | --- |
| **Cholesky Decomposition** | **0.806108** | **0.969133** | **18.19** | **4.77×** | **5.15 × 10⁻¹⁴** |
| Partial Pivoting | 0.806108 | 0.969133 | 25.76 | 3.37× | 5.85 × 10⁻¹⁴ |
| QR Decomposition | 0.806108 | 0.969133 | 27.29 | 3.18× | 9.55 × 10⁻¹⁴ |
| LU Decomposition | 0.806108 | 0.969133 | 28.55 | 3.04× | 5.85 × 10⁻¹⁴ |
| Matrix Inverse | 0.806108 | 0.969133 | 86.73 | 1.00× | 3.64 × 10⁻¹³ |

## Takeaway

In collaborative filtering via Alternating Least Squares, linear solver selection is an engineering optimization rather than a modeling hyperparameter. Because the regularized normal equations `W^T W + λI` are guaranteed to be symmetric positive definite for any `λ > 0`, **Cholesky decomposition** is the clear winner—delivering both the fastest training time and the smallest numerical residuals. Explicit matrix inversion should be avoided in production pipelines: it does nearly five times the work only to return a less precise answer.
