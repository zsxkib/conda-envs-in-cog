# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

from cog import BasePredictor, Input
import subprocess

# Accessing conda env "myenv"'s libs
import sys

ENV_NAME = "myenv"
sys.path.append(f"/cog/miniconda/envs/{ENV_NAME}/lib/python3.10/site-packages")

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

        return f"The dot product of the matrix with itself, using NumPy installed from the Conda environment, results in: {result}"
