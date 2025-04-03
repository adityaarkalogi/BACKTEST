import os
import pandas as pd

file_path = os.path.join(os.getcwd(), 'BANKNIFTY_JF_FNO_11042023.feather')
df = pd.read_feather(file_path)
file_path = file_path.replace('.feather','.csv')
df.to_csv(file_path)

