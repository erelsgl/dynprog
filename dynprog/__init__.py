"""
Generic dynamic programming in the iterative method.

Programmer: Erel Segal-Halevi.
Since: 2021-11.
"""
import pathlib, logging

logger = logging.getLogger(__name__)

HERE = pathlib.Path(__file__).parent
__version__ = (HERE / "VERSION").read_text().strip()
