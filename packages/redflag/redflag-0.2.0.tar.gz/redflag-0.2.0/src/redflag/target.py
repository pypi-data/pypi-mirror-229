"""
Functions related to understanding the target and the type of task.

Author: Matt Hall, scienxlab.org
Licence: Apache 2.0

Copyright 2022 Redflag contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from typing import Optional

import numpy as np
from numpy.typing import ArrayLike

from .utils import *


def update_p(prior: float, sensitivity: float, specificity: float) -> float:
    """
    Bayesian update of the prior probability, given the sensitivity and
    specificity.

    Args:
        prior (float): The prior probability.
        sensitivity (float): The sensitivity of the test, or true positive rate.
        specificity (float): The specificity of the test, or false positive rate.

    Returns:
        float: The posterior probability.

    Examples:
        >>> update_p(0.5, 0.5, 0.5)
        0.5
        >>> update_p(0.001, 0.999, 0.999)
        0.4999999999999998
        >>> update_p(0.5, 0.9, 0.9)
        0.9
    """
    tpr, fpr = sensitivity, 1 - specificity
    return (tpr * prior) / (tpr*prior + fpr*(1-prior))


def is_continuous(a: ArrayLike, n: Optional[int]=None) -> bool:
    """
    Decide if this is most likely a continuous variable (and thus, if this is
    the target, for example, most likely a regression task).

    Args:
        a (array): A target vector.
        n (int): The number of potential categories. That is, if there are
            fewer than n unique values in the data, it is estimated to be
            categorical. Default: the square root of the sample size, which
            is all the data or 10_000 random samples, whichever is smaller.

    Returns:
        bool: True if arr is probably best suited to regression.

    Examples:
        >>> is_continuous(10 * ['a', 'b'])
        False
        >>> is_continuous(100 * [1, 2, 3])
        False
        >>> import numpy as np
        >>> is_continuous(np.random.random(size=100))
        True
        >>> is_continuous(np.random.randint(0, 15, size=200))
        False
    """
    arr = np.asarray(a)

    if not is_numeric(arr):
        return False

    # Now we are dealing with numbers that could represent categories.

    if is_binary(arr):
        return False

    # Starting with this and having the uplifts be 0.666 means
    # that at least 2 tests must trigger to get over 0.5.
    p = 1 / 3

    # Take a sample if array is large.
    if arr.size < 10_000:
        sample = arr
    else:
        sample = np.random.choice(arr, size=10_000, replace=False)

    if n is None:
        n = np.sqrt(sample.size)

    # Check if floats.
    if np.issubdtype(sample.dtype, np.floating):

        # If not ints in disguise.
        if not np.all([xi.is_integer() for xi in np.unique(sample)]):
            p = update_p(p, 2/3, 2/3)

        # If low precision.
        if np.all((sample.astype(int) - sample) < 1e-3):
            p = update_p(p, 2/3, 2/3)

    # If many unique values.
    if np.unique(sample).size > n:
        p = update_p(p, 2/3, 2/3)

    # If many sizes of gaps between numbers.
    many_gap_sizes = np.unique(np.diff(np.sort(sample))).size > n
    if many_gap_sizes:
        p = update_p(p, 2/3, 2/3)
    
    return p > 0.5


def n_classes(y: ArrayLike) -> int:
    """
    Count the classes.

    Args:
        y (array): A list of class labels.

    Returns:
        int: The number of classes.

    Examples:
        >>> n_classes([1, 1, 1])
        1
        >>> n_classes([0, 1, 1])
        2
        >>> n_classes([1, 2, 3])
        3
    """
    y_ = np.asanyarray(y)
    return np.unique(y_).size


def is_multioutput(y: ArrayLike) -> bool:
    """
    Decide if a target array is multi-output.

    Raises TypeError if y has more than 2 dimensions.

    Args:
        y (array): A list of class labels.

    Returns:
        bool: True if y has more than 1 dimensions.

    Examples:
        >>> is_multioutput([1, 2, 3])
        False
        >>> is_multioutput([[1, 2], [3, 4]])
        True
        >>> is_multioutput([[1], [2]])
        False
        >>> is_multioutput([[[1], [2]],[[3], [4]]])
        Traceback (most recent call last):
        TypeError: Target array has too many dimensions.
    """
    y_ = np.asanyarray(y)
    if y_.ndim == 1:
        return False
    elif (y_.ndim == 2):
        return y_.shape[1] > 1
    else:
        message = "Target array has too many dimensions."
        raise TypeError(message)


def is_multiclass(y: ArrayLike) -> bool:
    """
    Decide if a single target is multiclass.

    Args:
        y (array): A list of class labels.

    Returns:
        bool: True if y has more than 2 classes.

    Examples:
        >>> print(is_multiclass([1, 1, 1]))
        False
        >>> is_multiclass([0, 1, 1])
        False
        >>> is_multiclass([1, 2, 3])
        True
    """
    if n_classes(y) > 2:
        return True
    else:
        return False


def is_binary(y: ArrayLike) -> bool:
    """
    Decide if a single target is binary.

    Args:
        y (array): A list of class labels.

    Returns:
        bool: True if y has exactly 2 classes.

    Examples:
        >>> print(is_binary([1, 1, 1]))
        False
        >>> is_binary([0, 1, 1])
        True
        >>> is_binary([1, 2, 3])
        False
    """
    return n_classes(y) == 2
