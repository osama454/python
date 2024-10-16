import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    'col1': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'],
    'col2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
})

# Parameters for slicing
slice_size = 5
start_idx = 1  # Starting index (inclusive)

# Iterate over the DataFrame with a sliding window
for i in range(0, len(df) - slice_size + 1, slice_size):
    for j in range(0, len(df.columns), 2):  # Iterate over columns with step 2
        col1_slice = df.iloc[i:i + slice_size, j]  # Slice of 'col1'
        col2_slice = df.iloc[i:i + slice_size, j + 1]  # Slice of 'col2'

        print(f"Window starting at index {i} for columns {j} and {j+1}:")
        print("col1:", list(col1_slice))
        print("col2:", list(col2_slice))
        print("-" * 20)