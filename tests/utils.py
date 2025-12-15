"""Utilties for test suite."""

import os

from vestacrystparser.utilities import parse_line


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(TEST_DIR, 'data')


def compare_vesta_strings(str1: str, str2: str, prec: int = None) -> bool:
    """
    Takes two VESTA strings, does basic parsing so no formatting,
    then checks if they are equivalent.

    If provided, prec means floats are compared to prec digits of precision.
    """
    data1 = [parse_line(x) for x in str1.strip().split('\n')]
    data2 = [parse_line(x) for x in str2.strip().split('\n')]
    # Compare
    if not len(data1) == len(data2):
        return False
    for line1, line2 in zip(data1, data2):
        if not line1 == line2:
            if prec is not None:
                for x1, x2 in zip(line1, line2):
                    if isinstance(x1, str) or isinstance(x2, str):
                        if x1 != x2:
                            return False
                    else:
                        if abs(x1-x2) >= 10**(-prec):
                            return False
            else:
                return False
    return True


def compare_matrices(M1, M2, prec: int = None) -> bool:
    """
    Takes two matrix-like objects and compares them.

    If provided, prec means floats are compared to prec digits of precision.
    """
    # Check first dimension is the same length.
    if not len(M1) == len(M2):
        return False
    for i in range(len(M1)):
        # Check second dimension is the same length
        if not len(M1[i]) == len(M2[i]):
            return False
        for j in range(len(M1[i])):
            # Compare elements
            if prec is None:
                if not M1[i][j] == M2[i][j]:
                    return False
            else:
                if not abs(M1[i][j] - M2[i][j]) <= 10**(-prec):
                    return False
    return True
