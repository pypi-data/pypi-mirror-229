
import numpy as np

# Create a sample NumPy array with empty columns
arr = np.array([[1, 2, 0, 4],
                [5, 6, 0, 8],
                [0, 0, 0, 0],
                [0, 0, 0, 0]])

# Find empty columns by checking if all elements in each column are zeros
empty_columns = np.all(arr == 0, axis=0)

# Use boolean indexing to remove empty columns
result = arr[:, ~empty_columns]

# Print the result
print(result)
