import numpy as np
import networkx as nx
from ase import Atoms
from fcdimen.functions.pbar import progressbar


def doubled_fc(natom, forceconstants, supercell):
    """Generating doubled supercells force constants

    Parameters:
    natom: integer
     Number of atoms in the initial supercell
    forceconstants: ndarray
     Force constant matrix of the initial supercell
    supercell: ASE Atoms object
      Initial supercell

    Returns:
    forceconstants_doubled : ndarray
     Force constant matrices array of the doubled supercell
    """
    print('Supercell chemical formula : ' + supercell.get_chemical_formula(mode='metal'))
    
    # Get initial Supercell properties
    ions = supercell.get_positions()
    basisvec = supercell.cell
    distances = supercell.get_all_distances(mic=True, vector=True)
    MaxFC = max(forceconstants.max(axis=0))

    # Create the doubled Supercell
    natom_doubled = natom * 8
    forceconstants_doubled = np.zeros([natom_doubled, natom_doubled, 3])
    basisvec_doubled = np.block([basisvec]) * 2

    ions_doubled = np.block([[ions], [ions + basisvec[0, :]]])
    ions_doubled = np.block([[ions_doubled], [ions_doubled + basisvec[1, :]]])
    ions_doubled = np.block([[ions_doubled], [ions_doubled + basisvec[2, :]]])

    supercell_doubled = Atoms(positions=ions_doubled, cell=basisvec_doubled, pbc=True)
    distancesNew = supercell_doubled.get_all_distances(mic=True, vector=True)
    # Initial value for Maximum force in new supercell
    Fmax = 0

    for k in progressbar(range(natom_doubled), "Progress: ", 40):
        nk = np.mod(k, natom)
        for m in range(natom_doubled):
            distances_diff = np.sum(((distancesNew[k, m, :] - distances[nk, :, :]) ** 2), axis=1)
            distances_diff = np.squeeze(distances_diff)
            mindiff = np.nonzero(distances_diff == min(distances_diff))[0][0]
            if (min(distances_diff) < 1e-8) and (check_dist(distances[nk, mindiff, :], basisvec) is True):
                forceconstants_doubled[k, m, 0] = forceconstants[nk, mindiff]
                forceconstants_doubled[k, m, 1] = forceconstants[nk, mindiff]
                forceconstants_doubled[k, m, 2] = forceconstants[nk, mindiff]

            elif (check_dist(distances[nk, mindiff, :], basisvec) is False) and (Fmax < forceconstants[nk, mindiff]):
                Fmax = forceconstants[nk, mindiff]
    
    if (Fmax / MaxFC) > 0.2:
         print("""
 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 !                    WARNING!                          !
 !       Hopefully, you know what are you doing.        !
 !       Supercell size is not big enough,              !
 !          results may not be reliable!!               !
 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 """)
        
    return forceconstants_doubled


def check_dist(distances, mindiff):
    """Check distances in doubled Supercell smaller
    than half of the value in the initial supercell and more than
    20% of MaxFC

    Parameters:
    distances: ndarray
     atomic distances in the initial supercell
    mindiff: integer
     Difference between atomic distances and minimum distance

    Returns:
    Boolean
     True if atomic distances are big enough
    """
    for i in range(3):
        if abs(np.sum(distances * mindiff[i]) / np.linalg.norm(mindiff[i])) > 0.48 * np.linalg.norm(mindiff[i]):
            return False
        else:
            return True


def connectivity(forceconstants, forceconstants_doubled, thresholds):
    """Checking connectivity of atoms

    Parameters:
    forceconstants: ndarray
     Force constant matrix of the initial supercell
    forceconstants_doubled : ndarray
     Force constant matrices array of the doubled supercell
    thresholds : float
     selected threshold(s)

    Returns:
    supercell_indices: list
     generate list of initial Supercell clusters indices
    supercell_doubled_indices: list
     generate list of doubled Supercell clusters indices
    """
    # Check NetworkX version
    if int(nx.__version__.split(".")[0]) < 3:
        supercell_graph = nx.from_numpy_matrix(forceconstants >= thresholds)
        supercell_doubled_graph = nx.from_numpy_matrix(forceconstants_doubled[:, :, 0] >= thresholds)
    else:
        supercell_graph = nx.from_numpy_array(forceconstants >= thresholds)
        supercell_doubled_graph = nx.from_numpy_array(forceconstants_doubled[:, :, 0] >= thresholds)

    # Get the indices of the simple supercell
    supercell_indices = [c for c in nx.connected_components(supercell_graph)]
    supercell_doubled_indices = [c for c in nx.connected_components(supercell_doubled_graph)]

    return supercell_indices, supercell_doubled_indices
