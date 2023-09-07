import os
from typing import List
import assorthead
import inspect

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def map_axis_to_bool(axis: int) -> bool:
    """Validate and map axis to a boolean.

    Args:
        axis (int): 0 for rows or 1 for columns.

    Raises:
        ValueError: If axis is not 0 or 1.

    Returns:
        bool: True if axis is 0 else False.
    """
    if not (axis == 0 or axis == 1):
        raise ValueError(f"Axis must be 0 or 1, provided {axis}")

    return True if axis == 0 else False


def map_order_to_bool(order: str) -> bool:
    """Validate and map order to a boolean.

    Args:
        order (str): Dense matrix representation, ‘C’, ‘F’,
            row-major (C-style) or column-major (Fortran-style) order.

    Raises:
        ValueError: If order is not 'C' or 'F'.

    Returns:
        bool: True if order is 'C' else False.
    """
    if not (order == "C" or order == "F"):
        raise ValueError(f"Order must be 'C' or 'F', provided {order}")

    return True if order == "C" else False


def includes() -> List[str]:
    """Provides access to C++ headers (including tatami) for downstream packages.

    Returns:
        List[str]: List of paths to the header files.
    """
    dirname = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return [
        assorthead.includes(),
        os.path.join(dirname, "include"),
    ]
