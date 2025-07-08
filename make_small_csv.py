import pandas as pd
df = pd.read_csv('data/bank_branches.csv')
df.head(100).to_csv('data/bank_branches_small.csv', index=False)