import numpy as np


def force_matrix(forceconstants):
    """Read Force constants matrix and prepare requirements matrices

    Parameters:
    forceconstants: ndarray
      array of force constants matrix

    Returns:
    natom: Integer
     number of atoms
    forceconstants_zero_diagonal: ndarray
     force constants matrix where diagonal elements are zero
    forceconstants_reshaped: ndarray
     Transpose of reshaped force constants matrix
    """
    force_mat = []
    for i in range(len(forceconstants)):
        for j in range(len(forceconstants)):
            for k in range(3):
                force_mat.append(forceconstants[i][j][k])

    natom = int(np.sqrt(len(force_mat) / 3))
    w = np.reshape(np.transpose(force_mat), [3, natom, natom, 3])
    forceconstants_reshaped = np.transpose(w, [0, 1, 3, 2])
    forceconstants_zero_diagonal = np.zeros((natom, natom))

    for i in range(natom):
        for j in range(natom):
            forceconstants_zero_diagonal[i, j] = np.linalg.norm(np.squeeze(forceconstants_reshaped[:, i, :, j]))

    for i in range(natom):
        forceconstants_zero_diagonal[i, i] = 0

    return natom, forceconstants_zero_diagonal, forceconstants_reshaped
