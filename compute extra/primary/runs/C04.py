"""Entry point for C04; see RUN_GUIDE.txt for inputs and interpretation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run import main

if __name__ == "__main__":
    main("C04")
