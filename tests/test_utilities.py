import pytest

from vestacrystparser.utilities import invert_matrix, matmul

from utils import compare_matrices


def test_invert_matrix():
    M = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert compare_matrices(invert_matrix(
        M), M, prec=12), "Identity matrix not matched"
    # Get a more complex inversion
    M = [[2.53, 0, 0],
         [1.2650000000000001, 2.1910442715746297, 0],
         [1.2650000000000001, 0.7303480905248766, 2.0657363497471466]]
    # Inverse from numpy.linalg.inv(M)
    Mi = [[0.39525692,  0.,  0.],
          [-0.22820169,  0.45640337,  0.],
          [-0.16136296, -0.16136296,  0.48408888]]
    assert compare_matrices(invert_matrix(M), Mi, prec=7)

def test_matmul():
    # Integer rectangular matrices
    M1 = [[4, 7, 6],
          [0, -3, 1]]
    M2 = [[0, 1],
          [-1, 3],
          [5, 0]]
    # Manually calculated answer
    M12 = [[23, 25],
           [8, -9]]
    assert compare_matrices(matmul(M1, M2), M12), \
        "Failed to multiply (2x3)x(3x2) integer matrices."
    M = [[2.53, 0, 0],
         [1.2650000000000001, 2.1910442715746297, 0],
         [1.2650000000000001, 0.7303480905248766, 2.0657363497471466]]
    # Inverse from numpy.linalg.inv(M)
    Mi = [[0.39525692,  0.,  0.],
          [-0.22820169,  0.45640337,  0.],
          [-0.16136296, -0.16136296,  0.48408888]]
    I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert compare_matrices(matmul(M, Mi), I, prec=7), \
        "Failed to mutliply two (3x3) float matrices."
