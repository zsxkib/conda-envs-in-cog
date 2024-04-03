# Using Conda with Replicate Cog Containers

This README provides a step-by-step guide on how to use Conda to install packages into a Replicate Cog container. By following these instructions, you can leverage the power of Conda environments within your Cog container, allowing you to manage dependencies and install packages that may not be available through pip.

## Important Considerations

Before getting started, please keep the following important points in mind:

1. Python Version Consistency:
   - The Python version specified in `cog.yaml` must match the Python version used in the Miniconda installation URL and the version used when creating the Conda environment.
   - If you change the Python version in `cog.yaml`, make sure to update the corresponding values in the Miniconda installation URL and the Conda environment creation command.

2. Manual Package Installation:
   - You need to manually add the desired packages to the `run` section of `cog.yaml`.
   - Specify the package name and version explicitly to ensure reproducibility.

3. Environment Name Consistency:
   - If you change the name of the Conda environment (`myenv` in this example), make sure to update the corresponding values in `predict.py` as well.

4. Path Configuration:
   - In `predict.py`, you need to append the path to the site-packages directory of your Conda environment to `sys.path` to make the installed packages accessible.
   - Ensure that the paths in `cog.yaml` and `predict.py` are consistent and aligned with your setup.

5. Pip Packages:
   - You can install pip packages outside of the Conda environment using the `python_packages` section in `cog.yaml`.
   - However, these packages will use the Python version specified in `cog.yaml`, so make sure all Python versions match.

## Step 1: Configure `cog.yaml`

In your project directory, create a `cog.yaml` file to define the configuration for your Cog container. Here's an example configuration that demonstrates how to set up Conda within the container:

```yaml
build:
  gpu: false
  python_version: "3.10"
  
  run:
    - curl -O https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Linux-x86_64.sh
    - bash Miniconda3-py310_23.3.1-0-Linux-x86_64.sh -b -p /cog/miniconda
    - /cog/miniconda/bin/conda init bash
    - /bin/bash -c "source /cog/miniconda/bin/activate && conda create -n myenv python=3.10 -y"
    - /bin/bash -c "source /cog/miniconda/bin/activate && conda activate myenv && conda install -c conda-forge numpy=1.24.3 -y"
    - /bin/bash -c "source /cog/miniconda/bin/activate && conda activate myenv && pip install cog>=0.7.2"
    - export PATH=/cog/miniconda/envs/myenv/bin:$PATH

predict: "predict.py:Predictor"
```

## Step 2: Update `predict.py`

In your `predict.py` file, make the following changes to ensure that your code can access the packages installed in the Conda environment:

```python
from cog import BasePredictor, Input
import subprocess

ENV_NAME = "myenv"
sys.path.append(f"/cog/miniconda/envs/{ENV_NAME}/lib/python3.10/site-packages")

import numpy as np

class Predictor(BasePredictor):
    def setup(self):
        package_list = subprocess.check_output(
            [
                "/bin/bash",
                "-c",
                f"source /cog/miniconda/bin/activate && conda activate {ENV_NAME} && conda list",
            ],
            universal_newlines=True,
        )
        print("Installed packages:")
        print(package_list)

    def predict(self, input_matrix: str = Input(description="Input numpy matrix to be squared", default="[[1, 2], [3, 4]]")) -> str:
        matrix = np.array(eval(input_matrix))
        result = np.dot(matrix, matrix)
        return f"The dot product of the matrix with itself, using NumPy installed from the Conda environment, results in: {result}"
```

## Step 3: Build and Run the Container

With the `cog.yaml` and `predict.py` files configured, you can now build and run your Cog container using the following commands:

```shell
cog build
cog predict -i input_matrix="[[1, 2], [3, 4]]"
```

The `cog build` command will create the container image based on the specifications in `cog.yaml`, including the installation of Miniconda and the specified packages.

The `cog predict` command will run the container and execute the `predict` function defined in `predict.py`, passing the provided input.

## Conclusion

By following these steps and keeping the important considerations in mind, you can effectively use Conda to install packages and manage dependencies within your Replicate Cog container. This allows you to leverage a wide range of packages and tools in your machine learning workflows.

Please note that this approach involves several moving parts and requires careful configuration to ensure consistency between `cog.yaml` and `predict.py`. Double-check the paths, environment names, and Python versions to avoid any discrepancies.

If you encounter any issues or have further questions, please refer to the Replicate Cog documentation or seek assistance from the community.