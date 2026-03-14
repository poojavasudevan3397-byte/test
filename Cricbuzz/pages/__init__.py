"""
Pages module for Cricbuzz LiveStats application
"""

from . import live_matches
from . import player_stats_2
from . import sql_analytics
from . import crud_operations

__all__ = [
    "live_matches",
    "player_stats_2",
    "sql_analytics",
    "crud_operations",
]
