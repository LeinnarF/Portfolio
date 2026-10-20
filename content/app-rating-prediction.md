---
title: App Rating & Hit Prediction
summary: Exploring the factors behind Google Play Store ratings and install milestones.
disciplines:
  - data-science
technologies:
  - Python
  - PCA
  - Scikit-learn
year: 2026
links:
  - label: GitHub
    url: https://github.com/LeinnarF/ML-Google-Playstore
  - label: Dataset
    url: https://www.kaggle.com/datasets/lava18/google-play-store-apps
---

## The Problem

Millions of apps compete on the Google Play Store, and only a fraction ever gain real traction. We wanted to know whether an app's surface-level traits—its category, size, price, and content rating—can predict whether it will break through. Defining a "hit" as an app with more than 100,000 installs, we set out to classify hits versus misses from metadata alone and uncover what actually drives success on the store.

## The Approach

We worked with the Kaggle Google Play Store dataset, which quickly proved how messy real-world scraped data can be. Of its 10,841 rows, only 9,660 represented unique apps because popular titles like ROBLOX appeared up to nine times. Ratings were missing for 1,474 entries, and one corrupted row had its columns shifted left—giving it a rating of 19 on a 5-point scale—so we dropped it.

Most numerical fields were stored as formatted text: prices carried dollar signs, installs read like `"10,000+"`, and sizes mixed `"19M"`, `"201k"`, and `"Varies with device"` (1,227 apps). We standardized sizes into kilobytes, isolated variable-size apps with an indicator flag, inferred a missing pricing tier from its price, and merged rare content ratings into adjacent groups. After deduplication and cleaning, 9,659 unique apps remained across nine structured features.

## Exploratory Analysis

A first pass at the numbers revealed just how lopsided the Play Store economy is. The average app has roughly 216,000 reviews and 7.8 million installs, yet the median app has only 967 reviews and 100,000 installs. A tiny class of viral giants pulls the averages far above what a typical release ever experiences. User ratings, by contrast, are much more forgiving, clustering around a median of 4.2 out of 5.

![[app-eda-category-rating.png|Category Rating Distribution]]

Breaking ratings down across the fifteen largest categories shows distinct behavioral patterns. Games average 4.17 stars with tightly clustered ratings, whereas Business and Medical apps sit much lower (around 3.14 for Business) with wide variance—suggesting that utility and enterprise users judge reliability much more harshly than casual players.

## The Result

### Predicting a Hit with Random Forest

Our first model was a Random Forest classifier trained strictly on pre-launch metadata: category, app size, pricing type, price, and content rating. Because roughly 40% of apps in the dataset cross the 100,000-install mark, the classes were well balanced. Out of the box, the baseline forest reached 70.4% accuracy and a 0.762 ROC-AUC. Five-fold cross-validation averaged 63% with noticeable variance across folds—a useful reminder that a single train/test split can flatter a model. After a randomized hyperparameter search, test accuracy climbed to **73.9%** with a **0.809 ROC-AUC**.

![[app-rf-evaluation.png|Random Forest Evaluation and Feature Importances]]

The feature importance ranking held the biggest surprise. **App size** was the dominant signal by far at 37%, followed by whether the size varied by device at 20%. Paid status (7%) and price (6%) came next, while category indicators played a much smaller role. Larger binaries and device-tailored builds often serve as a proxy for engineering investment and feature depth.

### Uncovering Structure with PCA

Next, we applied Principal Component Analysis (PCA) to five continuous variables—installs, rating, reviews, price, and size—after log-transforming the heavily skewed distributions. The first two principal components captured **67.7%** of the total variance and mapped cleanly onto two intuitive market dynamics:

| Component | Variance Explained | Cumulative | Interpretation |
| --------- | ------------------ | ---------- | -------------- |
| PC1       | 47.8%              | 47.8%      | Viral Reach (installs, reviews, rating) |
| PC2       | 20.0%              | 67.7%      | Premium Penalty (price) |
| PC3       | 18.7%              | 86.5%      | — |
| PC4       | 12.7%              | 99.2%      | — |
| PC5       | 0.8%               | 100%       | — |

![[app-pca-loadings.png|PCA Component Loadings]]

The component loadings confirm what each axis measures: installs and reviews heavily drive PC1 (*Viral Reach*), while price single-handedly dominates PC2 (*Premium Penalty*).

![[app-pca-scatter.png|Apps Projected onto Viral Reach and Premium Penalty Axes]]

Projecting all 9,659 apps onto these two axes makes the commercial tradeoff visible at a glance. Free apps span the entire *Viral Reach* spectrum, whereas expensive paid apps sit isolated in the high-*Premium Penalty* corner, rarely reaching mass-market scale.

## Evaluation & The Data Leakage Lesson

To see how well the PCA space separated hits from misses, we trained a K-Nearest Neighbors classifier (K = 49, tuned via cross-validation) on the first two components. On paper, it crushed the Random Forest, posting **93.7% accuracy** and a **0.987 ROC-AUC**.

| Model                    | Accuracy | F1    | ROC-AUC |
| ------------------------ | -------- | ----- | ------- |
| Random Forest (baseline) | 70.4%    | 0.703 | 0.762   |
| Random Forest (tuned)    | 73.9%    | 0.730 | 0.809   |
| KNN on PCA (K = 49)      | 93.7%    | 0.937 | 0.987   |

![[app-knn-decision-boundary.png|KNN Decision Boundary in PCA Space]]

As clean as that decision boundary looks, the score is a textbook case of **target leakage**. Because `installs`—the exact threshold used to define a "hit"—was included as one of the five inputs to the PCA, PC1 effectively encoded the target label inside the feature space.

![[app-model-comparison.png|Model Performance Comparison]]

Comparing the three models side by side illustrates why the tuned Random Forest's **73.9% accuracy** is the true benchmark of predictive performance. It never saw post-launch installs or review counts, relying solely on traits known before an app ever ships.

## Takeaway

Build size and pricing strategy say far more about an app's odds of reaching 100,000 installs than its category or content rating, and free distribution remains the primary path to viral scale. Just as importantly, this project reinforced a foundational rule of data science: when a model's metric looks too good to be true, interrogate the pipeline before celebrating the score.
