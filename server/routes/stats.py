"""
Stats API — Summary statistics, coverage gaps, data quality metrics.
"""

from fastapi import APIRouter
from server.data_loader import get_dataset_stats, get_state_stats, get_trust_distribution, get_column_completeness

router = APIRouter(tags=["stats"])


@router.get("/stats")
def stats():
    return get_dataset_stats()


@router.get("/stats/states")
def state_stats():
    return get_state_stats()


@router.get("/stats/trust-distribution")
def trust_distribution():
    return get_trust_distribution()


@router.get("/stats/column-completeness")
def column_completeness():
    return get_column_completeness()
