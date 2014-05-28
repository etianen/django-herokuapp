"""
Settings used by {{ project_name }} project.

This consists of the general production settings, with an optional import of any local
settings.
"""

# Import production settings.
from {{ project_name }}.settings.production import *

# Import optional local settings.
try:
    from {{ project_name }}.settings.local import *
except ImportError:
    pass
