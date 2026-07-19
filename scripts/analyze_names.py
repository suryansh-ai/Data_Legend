"""Analyze state and city variants in the dataset."""
import pandas as pd

df = pd.read_parquet(r"C:\Users\Ghanshyam\Desktop\Data_Legend\data\facilities_scored.parquet")

print("=== ALL STATES/UTs (sorted by count) ===")
states = df["address_stateOrRegion"].value_counts()
for s, c in states.items():
    print(f"  {c:>5}  {s}")
print(f"\nTotal unique: {len(states)}")
print(f"Total facilities: {len(df)}")

print("\n=== ALL CITIES (sorted by count, top 80) ===")
cities = df["address_city"].value_counts()
for s, c in cities.head(80).items():
    print(f"  {c:>5}  {s}")
print(f"\nTotal unique cities: {len(cities)}")
print(f"Cities with 1 facility: {(cities == 1).sum()}")
print(f"Cities with 2-5 facilities: {((cities >= 2) & (cities <= 5)).sum()}")
print(f"Cities with >5 facilities: {(cities > 5).sum()}")
