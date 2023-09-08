import pandas as pd
import numpy as np

# Converts categorical value to numerical values
def categorical_to_numerical(df: pd.DataFrame, column_name: str, inplace: bool = False):
    unique_values = np.unique(df[column_name])
    unique_nums = list(range(0, unique_values.__len__()))
    if inplace:
        df[column_name] = df[column_name].replace(unique_values, unique_nums)
    else:
        return df[column_name].replace(unique_values, unique_nums)
    
# Normalizes the features
def normalize(df: pd.DataFrame, column: str, inplace: bool):
    mean = np.mean(df[column])
    std = np.std(df[column])
    if inplace:
        df[column] = (df[column] - mean) / std
        return (mean, std)
    else:
        new_col = (df[column] - mean) / std
        return (new_col, mean, std)
   

def train_test_split(df: pd.DataFrame, train_portion: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    m = df.shape[0]
    train_m = int(m * train_portion)
    train_samples = np.random.choice(m, train_m, False)
    train_df = df.iloc[train_samples, :]
    total_samples = list(range(m))
    test_samples = np.delete(total_samples, train_samples)
    test_df = df.iloc[test_samples, :]
    return train_df, test_df