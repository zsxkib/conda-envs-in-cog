# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

from cog import BasePredictor, Input
import subprocess
import sys

# Define the name of your Conda environment (as you did in the 'run' section of cog.yaml)
ENV_NAME = "myenv"

# Append the path to the site-packages directory of your Conda environment
# NOTE: Ensure that the Python version in the path matches the version specified in cog.yaml
#       Use only the major and minor version numbers in the path (e.g., Python 3.10.9 -> python3.10)
#       Update this path if you change the Python version in cog.yaml
sys.path.append(f"/cog/miniconda/envs/{ENV_NAME}/lib/python3.10/site-packages")

# Import packages installed in the Conda environment
# NOTE: These packages are the packages we installed via the 'run' section of cog.yaml using Conda
import numpy as np


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
