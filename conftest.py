import sys
from pathlib import Path

# Ensure the project root is on sys.path so `from src.xxx import yyy` works
# regardless of where pytest is invoked from.
sys.path.insert(0, str(Path(__file__).parent))
