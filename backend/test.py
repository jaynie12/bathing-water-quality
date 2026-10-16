import pandas as pd

url = "https://environment.data.gov.uk/data/bathing-water-quality/in-season/slice/point/13100.csv"
df = pd.read_csv(url)

# Print all available column names to see what measurement metrics (like E. coli or Enterococci) are included
print(df.columns.tolist())

# Print sample rows
print(df[["observation > sample week", "uri"]].head(10))