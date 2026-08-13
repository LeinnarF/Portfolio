---
title: App Rating Prediction
summary: Exploring the factors associated with Google Play Store application ratings.
tagline: MACHINE LEARNING
technologies:
  - Python
  - PCA
  - Scikit-learn
featured: true
order: 1
links:
  - label: GitHub
    url: https://github.com/your-username/app-rating-prediction
  - label: Dataset
    url: https://www.kaggle.com/datasets/example/google-play-store-apps
---

## Overview

This project looks at which characteristics of a Google Play Store listing
are most associated with its user rating — combining exploratory data
analysis with a supervised learning pipeline to test that relationship
rather than assume it.

## Data & Preprocessing

The raw dataset included inconsistent formatting across several columns
(install counts as strings, mixed date formats, missing size values).
Cleaning and normalizing these was most of the early effort before any
modeling could start.

## Method

- Exploratory data analysis to surface candidate features
- Principal Component Analysis (PCA) to reduce dimensionality across
  correlated numeric features
- A handful of classifiers (Logistic Regression, Random Forest, KNN)
  compared on held-out data

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=5)
reduced = pca.fit_transform(scaled_features)
```

## Results

The strongest signal came from a combination of review count and update
recency rather than category or price — install count alone was a weaker
predictor than expected.

## What I'd Do Differently

Given more time, sentiment analysis on the review text itself would
likely add more signal than any of the structured columns did.
