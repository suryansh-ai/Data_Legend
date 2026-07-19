"""Analyze remaining city data quality issues."""
import pandas as pd

df = pd.read_parquet(r"C:\Users\Ghanshyam\Desktop\Data_Legend\data\facilities_scored.parquet")
cities = df["address_city"].value_counts()
singles = cities[cities == 1].index.tolist()

print(f"Total unique cities: {len(cities)}")
print(f"Cities with 1 facility: {len(singles)}")
print()

# Check for garbage/invalid city names
garbage_cities = []
for c in singles:
    s = str(c).lower()
    if any(g in s for g in ["{", "[", '"', "kie", "internal", "dentistry", "sector", "salt lake", "area"]):
        garbage_cities.append(c)
    elif len(s) <= 2:
        garbage_cities.append(c)
    elif s.isdigit():
        garbage_cities.append(c)

print(f"Garbage cities (coords, text, numbers, too short): {len(garbage_cities)}")
for g in garbage_cities[:40]:
    print(f"  {g}")
print()

# Check cities that are actually neighborhoods/streets
neighborhood_cities = []
for c in singles:
    s = str(c).lower()
    if any(g in s for g in ["nagar", "road", "sector", "east", "west", "south", "north", "central", "area", "colony", "mandir", "temple", "park", "gate", "cross", "main road", "st.", "street"]):
        neighborhood_cities.append(c)

print(f"Likely neighborhoods/streets: {len(neighborhood_cities)}")
for g in neighborhood_cities[:30]:
    print(f"  {g}")
print()

# Cities > 50 facilities
big_cities = cities[cities > 50]
print(f"Major cities (>50 facilities): {len(big_cities)}")
for s, c in big_cities.items():
    print(f"  {c:>5}  {s}")
