import pandas as pd

# Specify the path to your CSV file
csv_file = './SmallGrid_Requests.csv'

# Read the CSV file into a dataframe
df = pd.read_csv(csv_file)

# Now you can work with the dataframe
# For example, you can print the first few rows
print(df.head())