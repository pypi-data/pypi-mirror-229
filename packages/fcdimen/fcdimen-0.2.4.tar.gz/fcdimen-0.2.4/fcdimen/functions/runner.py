#! /usr/bin/env python

from argparse import ArgumentParser
from fcdimen.functions.reader import read_data
from fcdimen.functions.fcmat import force_matrix
import os
import numpy as np
from fcdimen.functions.welcome import welcome_logo
from fcdimen.functions.score import calc_score, scanner


def run():
    parser = ArgumentParser(description="Example: fcdimen -p PATH -i phonon.yaml")
    parser.set_defaults(
        input_file="phonon.yaml",
        path=os.getcwd(),
        threshold=None
    )
    parser.add_argument("-i", "--input_file", help="Phonopy yaml file name, default= phonon.yaml")
    parser.add_argument("-p", "--path", help="Path to phonopy yaml file with FORCE_SET file,"
                                             " default= Current directory")
    parser.add_argument("-t", "--threshold", help="Choose a specific threshold")
    args = parser.parse_args()
    if args.path != None:
        os.chdir(args.path)

    welcome_logo()

    phonon, unitcell, forceconstants, supercell = read_data(filename=args.input_file)
    natom, forceconstants_zero_diagonal, forceconstants_reshaped = force_matrix(forceconstants)
    maximumforce = max(forceconstants_zero_diagonal.max(axis=0))
    # Generating thresholds for scanning
    pl0 = np.round(np.arange(0, 50, 0.1), 2).tolist()
    pl1 = np.arange(50, maximumforce, 1).tolist()
    pl = pl0+pl1

    print("MaxFC between atoms: ")
    for i in range(natom):
        x = np.where(forceconstants_zero_diagonal[i] == max(forceconstants_zero_diagonal.max(axis=0)))[0]
        if len(x) != 0:
           print("{}, {} = {:.2f} eV/A^2".format(supercell.symbols[i], supercell.symbols[x[0]],
                                                 forceconstants_zero_diagonal[i][x[0]]))
           break

    print("MinFC between atoms: ")
    for i in range(natom):
        x = np.where(forceconstants_zero_diagonal[i] == min(forceconstants_zero_diagonal.max(axis=0)))[0]
        if len(x) != 0:
           print("{}, {} = {:.2f} eV/A^2".format(supercell.symbols[i], supercell.symbols[x[0]],
                                                 forceconstants_zero_diagonal[i][x[0]]))
           break

    if args.threshold == None:
        ths = [x for x in pl if x <= maximumforce]
        fcdimlist, dimensionality1, dimensionality2 = scanner(natom, forceconstants_zero_diagonal, supercell, ths)
        if dimensionality1 != None:
          print("Dimensionality with Class. I: {}".format(dimensionality1))

        if dimensionality2 != None:
          print("Dimensionality with Class. II: {}".format(dimensionality2))

        if fcdimlist != None:
          scores = calc_score(fcdimlist, maximumforce)
          print("Dimensionality with Class. III: {}".format(max(scores, key=scores.get)))
          print("Scores: {}".format(scores))

    else:
        assert float(args.threshold) >= 0.0, "ERROR: negative Negative threshold"
        ths = [float(args.threshold)]
        fcdimlist, dimensionality1, dimensionality2 = scanner(natom, forceconstants_zero_diagonal, supercell, ths)
        print("Dimensionality for t = {} eV/A^2 is: {}".format(ths[0], dimensionality1))


if __name__ == "__main__":
    run()
