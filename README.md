# State-based load profile generation for modeling energetic flexibility

This is the official repository for the paper _State-based load profile generation for modeling energetic flexibility_ published in TBD ...

## Structure

This repository is structured as follows:

- __data__
  - Time series for household consumption
- __experiments__
    - __bess__ / __bess_chp_hwt__ / __chp_hwt__: DER configuration
      - __classifier__: Output directory for _classifier_ training runs
      - __transition__: Output direcoty for _state estimator_ training runs
      - Jupyter Notebooks for training and evaluating ANNS
- __simulation/systems__
  -  DER simulation models

## Environment

The code found in this repository has most recently been executed in [this conda environment](environment).
Please note that we upgraded the package versions compared to those used in the paper. 
However, the results are still exactly reproducable.

### Jupyter lab

When using jupyter lab please make sure to install _jupyter-widgets/jupyterlab-manager_:
    
    jupyter labextension install @jupyter-widgets/jupyterlab-manager

### CUDA

We used GPUs to speed up the training process. For running the code on a CPU, please remove the .cuda() calls in the code.

