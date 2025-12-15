# Copyright 2025 Bernard Field
"""
Miscellaneous utility functions, such as string parsing and matrix algebra.
"""

from typing import Union

def parse_token(token: str) -> Union[int, float, str]:
    """Convert a token to int or float if possible (or leave as a string).

    Args:
        token: A string.

    Returns:
        `token` converted to :type:`int` if possible,
        or else :type:`float` if possible, or else returned
        as-is.
    """
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token


def parse_line(line: str) -> list[Union[int, float, str]]:
    """Split a line into tokens and convert each token.

    Args:
        line: String with data separated by spaces.

    Returns:
        A list of tokens (int, float, or string, as appropriate).
    """
    tokens = line.split()
    return [parse_token(tok) for tok in tokens]


def invert_matrix(mat: list[list[float]]) -> list[list[float]]:
    """Inverts a 3x3 matrix."""
    # Implementation using raw Python; importing numpy is overkill.
    # https://mathworld.wolfram.com/MatrixInverse.html
    assert len(mat) == 3, "mat must be 3x3"
    assert len(mat[0]) == 3, "mat must be 3x3"
    # Determinant of full matrix
    detfull = mat[0][0] * (mat[1][1]*mat[2][2] - mat[2][1]*mat[1][2]) \
        - mat[0][1] * (mat[1][0]*mat[2][2] - mat[1][2]*mat[2][0]) \
        + mat[0][2] * (mat[1][0]*mat[2][1] - mat[1][1]*mat[2][0])
    if detfull == 0:
        raise ValueError("Singular matrix")
    # Make determinants for each element.
    # Initialise
    inverse = [[None, None, None] for _ in range(3)]
    for i in range(3):
        # Grab the co-factor coordinates
        if i == 0:
            x1, x2 = 1, 2
        elif i == 1:
            x1, x2 = 2, 0
        else:
            x1, x2 = 0, 1
        for j in range(3):
            if j == 0:
                y1, y2 = 1, 2
            elif j == 1:
                y1, y2 = 2, 0
            else:
                y1, y2 = 0, 1
            # Each term is built from the co-factor, i.e. determinant of the
            # rest of the matrix.
            # But also, transpose the terms
            inverse[j][i] = (mat[x1][y1] * mat[x2][y2] -
                             mat[x1][y2] * mat[x2][y1]) / detfull
    return inverse

def matmul(mat1: list[list[float]], mat2: list[list[float]]) -> list[list[float]]:
    """Multiplies two matrices (NxM) x (MxL) -> (NxL)"""
    answer = []
    for i in range(len(mat1)):
        answer.append([])
        for j in range(len(mat2[0])):
            elem = 0
            assert len(mat1[i]) == len(mat2), \
                f"Mismatch in matrix dimensions, ({len(mat1)}x{len(mat1[i])})x({len(mat2)}x{len(mat2[j])})"
            for k in range(len(mat1[i])):
                elem += mat1[i][k] * mat2[k][j]
            answer[i].append(elem)
    return answer
