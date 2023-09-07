# pruna-engine

This is the code for the engine of the pruna engine product. It loads a pruna optimized model and runs inference based on a subscription service

## Prerequisites

You need to have Anaconda or Miniconda installed on your system to create the Conda environment. If you haven't installed it yet, refer to the Anaconda [installation instructions](https://docs.anaconda.com/anaconda/install/) or Miniconda [installation instructions](https://docs.conda.io/en/latest/miniconda.html).

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/username/myproject.git
    ```

2. Navigate to the project directory:

    ```bash
    cd myproject
    ```

3. Create a new Conda environment from the `environment.yml` file:

    ```bash
    conda env create -f environment.yml
    ```

4. Activate the new environment:

    ```bash
    conda activate pruna
    ```

5. Confirm that the new environment was installed correctly:

    ```bash
    conda env list
    ```

    You should see `pruna` in the list of your Conda environments.
6. Install the python wheel from the wheel folder:
    ```bash
    pip install pruna_engine-0.1-py3-none-any.whl
    ```

Now, you have everything you need to start using pruna-engine! Just go into notebooks and run the engine demo :)
