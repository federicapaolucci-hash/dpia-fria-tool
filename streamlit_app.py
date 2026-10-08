"""Entry point: wiring only. The app lives in src/digcon/ui, the logic in src/digcon/engine."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from digcon.ui.app import main  # noqa: E402

main()
