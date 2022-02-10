"""
Generic dynamic programming in the iterative method.

Programmer: Erel Segal-Halevi.
Since: 2021-11.
"""
import pathlib, logging

logger = logging.getLogger(__name__)

PARENT = pathlib.Path(__file__).parent.parent
__version__ = (PARENT / "VERSION").read_text().strip()
