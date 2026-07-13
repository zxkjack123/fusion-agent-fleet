---
name: scikit-learn-ml
description: "General-purpose machine learning for nuclear engineering — classification, regression, clustering, dimensionality reduction, model selection. Use when: simulation result classification, TBR regression prediction, parameter clustering analysis, feature importance for design parameters. 通用机器学习：仿真结果分类、TBR 回归预测、参数聚类分析、设计参数特征重要性。"
revision: 1
---

# Scikit-Learn — General-Purpose ML for Nuclear Engineering

## When to Use

- Training classification/regression models on simulation or experimental data
- Clustering simulation results to identify regimes or failure modes
- Dimensionality reduction for high-dimensional parameter spaces
- Feature importance analysis for nuclear design parameters
- Building surrogate models for expensive Monte Carlo simulations
- Hyperparameter tuning with grid/random/Bayesian search
- Quick baselines before moving to deep learning

## When NOT to Use

- For molecular-specific featurization — use `deepchem-ml` skill (has CircularFingerprint/MolGraphConvFeaturizer)
- For very large datasets (>10M rows) — use `polars-data` for ETL first, then subsample
- For graph-structured data — use `networkx-analysis` skill
- For deep learning — consider PyTorch/TensorFlow directly

## Core Capabilities

### 1. Data Preprocessing

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
```

### 2. Supervised Learning — Quick Selection Guide

| Problem | < 1K samples | 1K-100K | > 100K |
|---------|-------------|---------|--------|
| Classification | LogisticRegression, SVC | RandomForest, XGBoost | HistGradientBoosting |
| Regression | Ridge, Lasso | RandomForestRegressor | HistGradientBoostingRegressor |
| Interpretability | Linear models, DecisionTree | RandomForest feature_importances_ | SHAP |

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
pred = model.predict(X_test)
print(f"R² = {r2_score(y_test, pred):.4f}, MAE = {mean_absolute_error(y_test, pred):.4f}")
```

### 3. Clustering — Simulation Result Grouping

```python
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA

# Dimensionality reduction for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

# Clustering
kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(X)
```

### 4. Feature Importance for Design Parameters

```python
# For RandomForest
importances = model.feature_importances_
for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
    print(f"{name}: {imp:.4f}")

# Permutation importance (model-agnostic)
from sklearn.inspection import permutation_importance
result = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42)
```

### 5. Model Selection & Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20]}
grid = GridSearchCV(RandomForestRegressor(), param_grid, cv=5)
grid.fit(X_train, y_train)
print(f"Best params: {grid.best_params_}")
```

## Nuclear Engineering Applications

### Scenario 1: TBR Surrogate Model
Train a RandomForest/GradientBoosting regressor on OpenMC TBR simulation results (input: breeder thickness, Li-6 enrichment, multiplier thickness → output: TBR). Use feature importance to rank design parameters.

### Scenario 2: Shutdown Dose Rate (SDR) Regime Classification
Cluster SDR results into regimes (high/medium/low) based on cooling time and geometry features. Use PCA for visualization of the parameter space.

### Scenario 3: Activation Product Grouping
Use KMeans/DBSCAN to cluster FISPACT-II activation products by half-life, activity, and dose rate — identify dominant contributors.

### Scenario 4: Anomaly Detection in Simulation Outputs
Use IsolationForest or OneClassSVM to flag anomalous Monte Carlo tally results that deviate from expected physical ranges.

### Scenario 5: Parameter Sensitivity Ranking
Use permutation importance on a surrogate model trained on parametric sweep results to rank design parameters by impact on TBR/SDR/DPA.

## Installation

```bash
uv pip install scikit-learn pandas numpy
```

Already installed in standard scientific Python environments.

## Integration with Other Skills

- **parametric-sweep**: Post-process sweep results with ML models
- **data-analyst agent**: Delegate for publication-grade ML plots and analysis
- **polars-data**: Use polars for ETL on large sweep datasets before feeding to sklearn
- **experimental-design**: Design DOE matrices, then analyze with sklearn models

## Best Practices

1. **Always scale features** for distance-based models (SVM, KNN, KMeans)
2. Use `train_test_split` with fixed `random_state` for reproducibility
3. Prefer `RandomizedSearchCV` over `GridSearchCV` for >3 hyperparameters
4. Cross-validate with `cv=5` as minimum; use `StratifiedKFold` for imbalanced classes
5. For nuclear simulation data with <5% statistical uncertainty: exclude high-error cases before training

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from K-Dense-AI/scientific-agent-skills scikit-learn skill, with nuclear engineering applications | Agent science capability upgrade plan |
