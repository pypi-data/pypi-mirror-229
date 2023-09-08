import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

def load_data(file_name: str, fillna: bool = False) -> pd.DataFrame:
    df = pd.read_csv(file_name)
    
    if fillna:
        # Filling NA values
        for column in df.columns:
            if df[column].dtype == pd.StringDtype:
                df[column] = df[column].fillna('N/A')
            else:
                df[column] = df[column].fillna(0)
    return df
