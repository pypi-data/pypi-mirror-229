import os
import phonopy
from ase import Atoms


def read_data(filename="phonon.yaml"):
    """Read yaml file from phonopy phonon calculations.

    Parameters:
    filename: string
       name of phonopy generated yaml file
       *Note: FORCE_SETS file should be present in same folder as yaml file

    Returns:
    phonon: Phonopy object
     force calculations results
    unitcell_structure: ASE Atoms object
     unitcell of loaded Phonopy object
    forceconstants: ndarray
      array of force constants matrix
    supercell_structure: ASE Atoms object
      supercell of loaded Phonopy object    
    """
    try:
        # Load forces from phonopy object
        phonon = phonopy.load(filename, force_sets_filename="FORCE_SETS")
        unitcell = phonon.unitcell
        unitcell_structure = Atoms(unitcell.symbols, positions=unitcell.positions, cell=unitcell.cell, pbc=True)
        # Generate Force constants matrix
        phonon.produce_force_constants()
        forceconstants = phonon.force_constants
        # Generate Supercell
        supercell = phonon.supercell
        supercell_structure = Atoms(supercell.symbols, positions=supercell.positions, cell=supercell.cell, pbc=True)
    except:
        print("Compact version yaml file selected")
        # if FORCE_SETS not exist, yaml file should include force constants compact constants
        phonon = phonopy.load(filename, is_compact_fc=True, log_level=1)
        unitcell = phonon.unitcell
        unitcell_structure = Atoms(unitcell.symbols, positions=unitcell.positions, cell=unitcell.cell, pbc=True)
        phonon.produce_force_constants()
        forceconstants = phonon.force_constants
        supercell = phonon.supercell
        supercell_structure = Atoms(supercell.symbols, positions=supercell.positions, cell=supercell.cell, pbc=True)

    return phonon, unitcell_structure, forceconstants, supercell_structure
