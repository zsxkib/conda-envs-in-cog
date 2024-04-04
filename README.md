# Using Conda with Replicate Cog Containers

This README provides a comprehensive guide on how to use Conda to install packages into a Replicate Cog container. By following these instructions, you can leverage the power of Conda environments within your Cog container, allowing you to manage dependencies and install packages that may not be available through pip.

## Important Considerations

Before getting started, please keep the following crucial points in mind:

1. **Python Version Consistency:**
   - The Python version specified in `cog.yaml` must match the Python version used in the Miniconda installation URL, the version used when creating the Conda environment, and the version specified in `predict.py` when appending the site-packages path.
   - If you change the Python version in `cog.yaml`, you must update the corresponding values in the Miniconda installation URL, the Conda environment creation command, and the `sys.path.append` statement in `predict.py` to maintain consistency.

2. **Manual Package Installation:**
   - You need to manually add the desired packages to the `run` section of `cog.yaml`.
   - Specify the package name and version explicitly to ensure reproducibility.

3. **Environment Name Consistency:**
   - If you change the name of the Conda environment (`myenv` in the provided examples), make sure to update the corresponding values in `predict.py` as well.

4. **Path Configuration:**
   - In `predict.py`, you need to append the path to the site-packages directory of your Conda environment to `sys.path` to make the installed packages accessible.
   - Ensure that the appended path in `predict.py` matches the Python version specified in `cog.yaml` and the Conda environment creation command.

5. **Pip Packages (Untested):**
   - You can potentially install pip packages outside of the Conda environment using the `python_packages` section in `cog.yaml`.
   - However, this relies on the assumption that everything is running the same version of Python and that the site-packages are compatible.
   - Exercise caution when using this approach as it is largely untested and may lead to unexpected behavior or conflicts.

## Step 1: Configure `cog.yaml`

In your project directory, create a `cog.yaml` file to define the configuration for your Cog container. Here's an example configuration that demonstrates how to set up Conda within the container:

```yaml
# Configuration for Cog ⚙️
# Reference: https://github.com/replicate/cog/blob/main/docs/yaml.md

build:
  # set to true if your model requires a GPU
  gpu: false

  # a list of ubuntu apt packages to install
  # system_packages:
  #   - "libgl1-mesa-glx"
  #   - "libglib2.0-0"

  # python version in the form '3.11' or '3.11.4'
  python_version: "3.10"

  # a list of packages in the format <package-name>==<version>
  # python_packages:
  # (Optional) List of pip packages to install as well as conda packages in run (untested)
  #   - "numpy==1.19.4"
  #   - "torch==1.8.0"
  #   - "torchvision==0.9.0"

  # commands run after the environment is setup
  run:
    # Download and install Miniconda (make sure the Python version matches)
    - curl -O https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Linux-x86_64.sh
    - bash Miniconda3-py310_23.3.1-0-Linux-x86_64.sh -b -p /cog/miniconda

    # Initialize Conda for bash
    - /cog/miniconda/bin/conda init bash

    # Create a new conda environment named 'myenv' with Python 3.10
    - /bin/bash -c "source /cog/miniconda/bin/activate && conda create -n myenv python=3.10 -y"

    # Activate the 'myenv' environment and install NumPy from the conda-forge channel
    - /bin/bash -c "source /cog/miniconda/bin/activate && conda activate myenv && conda install -c conda-forge numpy=1.24.3 -y"

    # Activate the 'myenv' environment and install the cog package using pip
    - /bin/bash -c "source /cog/miniconda/bin/activate && conda activate myenv && pip install cog>=0.7.2"

    # Export the path to ensure the conda environment 'myenv' is activated by default
    - export PATH=/cog/miniconda/envs/myenv/bin:$PATH

# predict.py defines how predictions are run on your model
predict: "predict.py:Predictor"
```

## Step 2: Update `predict.py`

In your `predict.py` file, make the following changes to ensure that your code can access the packages installed in the Conda environment:

```python
# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

from cog import BasePredictor, Input
import subprocess

# Accessing conda env "myenv"'s libs
import sys

# Define the name of your Conda environment
ENV_NAME = "myenv"

# Append the path to the site-packages directory of your Conda environment
# Make sure the Python version matches the one specified in cog.yaml
sys.path.append(f"/cog/miniconda/envs/{ENV_NAME}/lib/python3.10/site-packages")

# Import packages installed in the Conda environment
import numpy as np  # Numpy was installed via conda (see run section of cog.yaml) it was NOT installed via python_packages


class Predictor(BasePredictor):
    def setup(self):
        # Get the list of installed packages in the conda environment
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

    def predict(
        self,
        input_matrix: str = Input(
            description="Input numpy matrix to be squared", default="[[1, 2], [3, 4]]"
        ),
    ) -> str:
        # Use the packages from the Conda environment
        # Convert the input string to a NumPy array
        matrix = np.array(eval(input_matrix))

        # Print the operation with the actual matrix
        print("Operation: ")
        print(matrix)
        print("(dot)")
        print(matrix)

        # Perform the dot product operation
        result = np.dot(matrix, matrix)

        # Print the result of the dot product
        print("= Result:")
        print(result)

        return f"The dot product of the input matrix {input_matrix} with itself, using NumPy installed from the Conda environment, results in: {result}"
```

## Step 3: Build and Run the Container

With the `cog.yaml` and `predict.py` files configured, you can now build and run your Cog container using the following commands:

```shell
cog build
cog predict -i input_data="[1, 2, 3]"
```

The `cog build` command will create the container image based on the specifications in `cog.yaml`, including the installation of Miniconda and the specified packages.

The `cog predict` command will run the container and execute the `predict` function defined in `predict.py`, passing the provided input.

## Modifying the Configuration

To adapt this configuration to your specific needs, you can make the following changes:

1. **Python Version:**
   - Update the `python_version` in `cog.yaml` to match your desired Python version.
   - Modify the Miniconda installation URL in the `run` section of `cog.yaml` to use the corresponding Python version.
   - Update the `sys.path.append` statement in `predict.py` to match the Python version.

2. **Conda Packages:**
   - Add or remove Conda packages in the `run` section of `cog.yaml` based on your requirements.
   - Specify the package name and version explicitly to ensure reproducibility.

3. **Pip Packages (Untested):**
   - If needed, you can add pip packages to the `python_packages` section in `cog.yaml`.
   - Note that this approach is untested and may lead to unexpected behavior or conflicts.

4. **Environment Name:**
   - If you change the name of the Conda environment (`myenv` in the provided examples), update the `ENV_NAME` variable in `predict.py` accordingly.

Remember to keep the Python version consistent across `cog.yaml`, the Miniconda installation URL, the Conda environment creation command, and the `sys.path.append` statement in `predict.py`.

## Conclusion

By following this guide and considering the important details and caveats mentioned, you can effectively use Conda to install packages and manage dependencies within your Replicate Cog container. This allows you to leverage a wide range of packages and tools in your machine learning workflows.

If you encounter any issues or have further questions, please refer to the Replicate Cog documentation or seek assistance from the community.

Happy coding with Conda and Replicate Cog!