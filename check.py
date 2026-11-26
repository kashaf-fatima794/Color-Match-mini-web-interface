import pandas as pd

df=pd.read_csv("color_pedia.csv")

rgb=df[["R", "G", "B"]]

print("Data types:")
print(rgb.dtypes)

print("Missing values:")
print(rgb.isna().sum())

print("Invalid non-numeric values:")
numeric=rgb.apply(pd.to_numeric, errors="coerce")
print((numeric.isna()&rgb.notna()).sum())

print("Values outside 0-255:")
print(((numeric<0)|(numeric>255)).sum())

print("First 5 RGB rows:")
print(rgb.head())