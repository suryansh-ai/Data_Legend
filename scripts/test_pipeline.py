"""Verify the full data pipeline works with 10K scored parquet."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.data_loader import load_facilities, get_dataset_stats, get_trust_distribution, get_column_completeness, get_state_stats, get_facility_by_id

df = load_facilities()
print(f"Loaded: {len(df)} facilities, {len(df.columns)} columns")
print()

stats = get_dataset_stats()
print("Dataset stats:")
for k, v in stats.items():
    print(f"  {k}: {v}")
print()

trust = get_trust_distribution()
print("Trust distribution:")
for k, v in trust.items():
    print(f"  {k}: {v}")
print()

completeness = get_column_completeness()
print("Column completeness (top 10):")
for k, v in sorted(completeness.items(), key=lambda x: -x[1])[:10]:
    pct = v / len(df) * 100
    print(f"  {k}: {v}/{len(df)} ({pct:.1f}%)")
print()

state_stats = get_state_stats()
print(f"States: {len(state_stats)}")
print("Top 5 states:")
for s in state_stats[:5]:
    print(f"  {s['state']}: {s['total']} facilities, avg trust {s['avg_trust']}")
print()

# Test facility by ID
sample_id = df.iloc[0]["unique_id"]
fac = get_facility_by_id(sample_id)
if fac:
    print(f"Sample facility: {fac.get('name', 'N/A')}")
    print(f"  Trust score: {fac.get('_trust_score')}")
    print(f"  Trust signal: {fac.get('_trust_signal')}")
    print(f"  City: {fac.get('address_city')}")
    print(f"  State: {fac.get('address_stateOrRegion')}")
