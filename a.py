import pandas as pd

# Sample DataFrame
data = {'col1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'col2': [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}
df = pd.DataFrame(data)

# Parameters
window_size = 5  # Number of consecutive indices to access
start_idx = 1   # Starting index

# Iterate over the DataFrame
for i in range(0, len(df) - window_size + 1, window_size):
    for j in range(0, len(df.columns)):
        # Extract data from the current window
        window_data = df.iloc[i:i + window_size, j].values
        print(f"Data from row {i}-{i+window_size-1}, column {df.columns[j]}: {window_data}")