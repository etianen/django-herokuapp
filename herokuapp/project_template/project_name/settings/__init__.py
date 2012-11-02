"""
Settings used by {{ project_name }} project.

This consists of the general produciton settings, with an optional import of any local
settings.
"""

# Import production settings.
from production import *

# Import optional local settings.
try:
    from local import *
except ImportError:
    pass