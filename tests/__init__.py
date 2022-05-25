from pathlib import Path

here = Path(__file__).parent
datadir = here / "data"
outdir = here / "outputs"

INPUT_FILES = [p for p in datadir.glob("*.json")]

