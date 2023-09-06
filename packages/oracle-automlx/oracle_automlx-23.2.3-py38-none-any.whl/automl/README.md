### Automated Machine Learning with Explainability (AutoMLx)

The AutoMLx package provides advanced automated machine learning solutions and machine learning model explanations for tabular and text datasets.

The [AutoML Pipeline](https://docs.oracle.com/en-us/iaas/tools/automlx/latest/html/multiversion/latest/automl.html) automatically preprocesses, selects and engineers high-quality features in your dataset, which are then given to an automatically chosen and tuned machine learning model.

The [MLExplainer](https://docs.oracle.com/en-us/iaas/tools/automlx/latest/html/multiversion/latest/mlx.html) offers a wide variety of visual and interactive explanations. For example, these include (local and global) feature importance, feature dependence and counterfactual explanations. These explanations provide multi-facetted insights into what your (AutoMLx or scikit-learn-style) model has learned and whether or not you should trust it.

The [fairness module](https://docs.oracle.com/en-us/iaas/tools/automlx/latest/html/multiversion/latest/fairness.html) offers tools to help you diagnose and understand the unintended bias present in your dataset and model so that you can make steps towards more inclusive and fair applications of machine learning.

### Installation

There are two ways to use AutoMLx.

#### Direct Installation

AutoMLx can be installed on x86 or ARM machines in a python 3.8 or 3.10 environment using:

```
pip3 install oracle-automlx
```

Several AutoMLx dependencies are optional and can be installed with:

```
pip3 install oracle-automlx[option]
```

where "option" can be one of:
 - "viz", which provides visualization functionality for explanations and the AutoML time-series forecaster,
 - "forecasting", which installs the forecasting models needed for the AutoML time-series forecaster,
 - "deep-learning", which installs some torch-based deep-learning models for the AutoML classifier, regressor and anomaly detector, and
 - "onnx", which installs the onnx-related libraries needed to export AutoML models to the ONNX format.

Multiple optional dependencies can be installed simultaneously using a comma-separated list. For example:

```
pip3 install oracle-automlx[forecasting,viz]
```

#### Oracle Cloud Infrastructure (OCI) Data Science (DS) Conda Pack

AutoMLx is also available in the [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/) [Data Science](https://www.oracle.com/artificial-intelligence/data-science/) service in the [AutoMLx](https://docs.oracle.com/en-us/iaas/data-science/using/conda-automlx-fam.htm) conda pack. 

### Getting Started

Head to our [Quick Start](https://docs.oracle.com/en-us/iaas/tools/automlx/latest/html/multiversion/latest/guides/quickstart.html).

### License

Copyright (c) 2023 Oracle and/or its affiliates. Licensed under the [NFTC License](https://www.oracle.com/downloads/licenses/no-fee-license.html).
