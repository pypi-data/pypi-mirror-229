import os
from typing import Union, Tuple, Sequence
import assorthead
import inspect
import numpy as np

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def includes() -> list[str]:
    """Provides access to C++ headers (including tatami) for downstream packages.

    Returns:
        list[str]: List of paths to the header files.
    """
    dirname = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return [
        assorthead.includes(),
        os.path.join(dirname, "include"),
    ]


def _sanitize_subset(
    subset: Sequence[int], full: int
) -> Tuple[bool, Union[np.ndarray, None]]:
    is_noop = True
    if len(subset) == full:
        for i, x in enumerate(subset):
            if i != x:
                is_noop = False
                break
    else:
        is_noop = False

    if is_noop:
        return True, None

    if not isinstance(subset, np.ndarray):
        subset = np.array(subset, dtype=np.int32)
    else:
        subset = subset.astype(
            np.int32, copy=not (subset.flags.C_CONTIGUOUS or subset.flags.F_CONTIGUOUS)
        )

    return False, subset
