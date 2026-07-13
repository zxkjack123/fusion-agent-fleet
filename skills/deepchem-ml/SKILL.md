---
name: deepchem-ml
description: "Molecular ML for nuclear engineering — property prediction (ADMET, toxicity) with featurizers, graph neural networks, transfer learning. Use when: irradiation product property prediction, coolant chemistry analysis, corrosion product identification, molecular featurization for ML models. 分子机器学习：辐照产物性质预测、冷却剂化学分析、腐蚀产物识别。"
revision: 1
---

# DeepChem — Molecular Machine Learning for Nuclear Engineering

## When to Use

- Predicting molecular properties (solubility, toxicity, binding affinity) for nuclear-relevant molecules
- Loading and processing molecular data (SMILES strings, SDF files)
- Training graph neural networks on molecular structures
- Applying transfer learning from pretrained ChemBERTa/GROVER/MolFormer models
- Using MoleculeNet benchmark datasets as baselines
- Screening corrosion inhibitors, coolant additives, or radiolytic products

## When NOT to Use

- For nuclear cross-section or decay data — use `nuclear-data-mcp`
- For Monte Carlo particle transport — use `simulation-builder` or `fusion-chain-runner`
- For general ML without molecular structure — use `scikit-learn-ml` skill
- For materials crystal structure analysis — use `pymatgen-materials` skill

## Core Capabilities

### 1. Molecular Featurization — Decision Tree

```
Is the model a graph neural network?
├─ YES → Use MolGraphConvFeaturizer or DMPNNFeaturizer
└─ NO → What type of model?
    ├─ Traditional ML (RF, XGBoost) → CircularFingerprint (ECFP)
    ├─ Deep learning (non-graph) → CircularFingerprint
    ├─ Sequence models (LSTM, Transformer) → SmilesToSeq
    └─ 3D structure analysis → CoulombMatrix
```

```python
import deepchem as dc

# Fingerprints for traditional ML
fp = dc.feat.CircularFingerprint(radius=2, size=2048)

# Graph features for GNNs
graph_feat = dc.feat.MolGraphConvFeaturizer()
```

### 2. Model Selection Guide

| Dataset Size | Recommended Model | Featurizer |
|-------------|-------------------|------------|
| < 1K samples | SklearnModel (RandomForest) | CircularFingerprint |
| 1K-100K | GBDTModel or MultitaskRegressor | CircularFingerprint |
| > 100K | GCNModel, AttentiveFPModel | MolGraphConvFeaturizer |
| Small + novel | Transfer learning (ChemBERTa/GROVER) | Model-specific |

### 3. Critical: Scaffold Splitting

**Always** use `ScaffoldSplitter` for molecular datasets to prevent data leakage:

```python
splitter = dc.splits.ScaffoldSplitter()
train, valid, test = splitter.train_valid_test_split(dataset)
```

### 4. Transfer Learning

```python
# ChemBERTa — pretrained on 77M molecules
model = dc.models.HuggingFaceModel(
    model='seyonec/ChemBERTa-zinc-base-v1',
    task='classification', n_tasks=1,
    learning_rate=2e-5  # Lower LR for fine-tuning
)
model.fit(train, nb_epoch=10)
```

## Nuclear Engineering Applications

### Scenario 1: Coolant Chemistry — Radiolytic Product Toxicity
Predict LD50 and Ames mutagenicity of water radiolysis products (H₂O₂, O₂, H₂) and their secondary reaction products with corrosion metals.

### Scenario 2: Corrosion Inhibitor Screening
Use GNN-based property prediction to screen organic corrosion inhibitors for PbLi and FLiBe compatibility — predict solubility, thermal stability, and activation cross-section avoidance.

### Scenario 3: Tritium Extraction — Getter Material Binding Affinity
Train binding affinity models for hydrogen isotope getter candidates (ZrCo, Zr₂Fe, U) using transfer learning from existing hydrogen storage datasets.

### Scenario 4: Activated Corrosion Product (ACP) Identification
Featurize and classify activated corrosion product species transported in primary cooling loops — predict mobility and deposition propensity.

## Installation

```bash
uv pip install deepchem
uv pip install 'deepchem[torch]'  # For GNNs and transfer learning
```

## Integration with Other Skills

- **scikit-learn-ml**: Use DeepChem featurizers with scikit-learn models via `SklearnModel` wrapper
- **pymatgen-materials**: Cross-reference molecular properties with solid-state phase stability
- **parametric-sweep**: Automate molecular property screening across composition libraries

## Best Practices

1. **Always use ScaffoldSplitter** for molecular data — random splitting leaks information
2. Start with RandomForest + CircularFingerprint as baseline
3. Normalize features and targets with `NormalizationTransformer`
4. For small datasets (< 1000 samples), use transfer learning
5. Avoid memory issues: use `DiskDataset` for large datasets, reduce batch size

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from K-Dense-AI/scientific-agent-skills deepchem skill, with nuclear engineering focus | Agent science capability upgrade plan |
