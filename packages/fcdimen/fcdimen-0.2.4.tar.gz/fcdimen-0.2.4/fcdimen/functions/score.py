from fcdimen.functions.cluster import doubled_fc, connectivity
from fcdimen.functions.dimensionality import calc_dimension
from fcdimen.functions.pbar import progressbar


def scanner(natom, forceconstants_zero_diagonal, supercell, thresholds):
    """ Calculating dimensionality based on selected thresholds

    Parameters:
    natom:  Integer
     number of atoms
    forceconstants_zero_diagonal: ndarray
     force constants matrix where diagonal elements are zero
    forceconstants_reshaped: ndarray
     Transpose of reshaped force constants matrix
    supercell:  ASE Atoms object
      supercell
    thresholds: List
     list of thresholds for scanning

    Returns:
    dimensionalities_thresholds: Dictionary
     Predicted dimensionalities for each thresholds
    dimensionality_class1: string
     Predicted dimensionality with classification I
    dimensionality_class2: string
     Predicted dimensionality with classification II
    """
    dimensionalities_thresholds = {}
    forceconstants_doubled = doubled_fc(natom, forceconstants_zero_diagonal, supercell)
    
    if len(thresholds) != 1:
        ind1, indices1 = connectivity(forceconstants_zero_diagonal, forceconstants_doubled, 0.5)
        dimensionality_class1 = calc_dimension(ind1, indices1)
        MinFC = min(forceconstants_zero_diagonal.max(axis=0))
        ind2, indices2 = connectivity(forceconstants_zero_diagonal, forceconstants_doubled, (MinFC - 0.01))
        dimensionality_class2 = calc_dimension(ind2, indices2)

        for p in thresholds:
            ind, indices = connectivity(forceconstants_zero_diagonal, forceconstants_doubled, p)
            dimensionality = calc_dimension(ind, indices)
            dimensionalities_thresholds[str(p)] = dimensionality
    else:
        ind, indices = connectivity(forceconstants_zero_diagonal, forceconstants_doubled, thresholds)
        dimensionality_class1 = calc_dimension(ind, indices)
        dimensionalities_thresholds = None
        dimensionality_class2 = None

    return dimensionalities_thresholds, dimensionality_class1, dimensionality_class2


def calc_score(dimensionalities_thresholds, maxforceconstant):
    """Calculating dimensionality scores

    Parameters:
    dimensionalities_thresholds: Dictionary
     calculated dimensionality of each threshold
    maxforceconstant: Float
     Maximum force constant in structure
    Returns:

    dimen_score: Dictionary
     dimensionalities and corresponding scores
    """

    th0d = []
    th1d = []
    th2d = []
    th3d = []
    th01d = []
    th02d = []
    th03d = []
    th012d = []
    th013d = []
    th023d = []
    th12d = []
    th13d = []
    th123d = []
    th23d = []

    # difference of thresholds (maximum and minimum occurrence)
    dT = {}
    for i in dimensionalities_thresholds.keys():
            if dimensionalities_thresholds[i] == "0D":
                th0d.append(float(i))

            if dimensionalities_thresholds[i] == "1D":
                th1d.append(float(i))

            if dimensionalities_thresholds[i] == "2D":
                th2d.append(float(i))

            if dimensionalities_thresholds[i] == "3D":
                th3d.append(float(i))

            if dimensionalities_thresholds[i] == "01D":
                th01d.append(float(i))

            if dimensionalities_thresholds[i] == "02D":
                th02d.append(float(i))

            if dimensionalities_thresholds[i] == "03D":
                th03d.append(float(i))

            if dimensionalities_thresholds[i] == "012D":
                th012d.append(float(i))

            if dimensionalities_thresholds[i] == "013D":
                th013d.append(float(i))

            if dimensionalities_thresholds[i] == "023D":
                th023d.append(float(i))

            if dimensionalities_thresholds[i] == "12D":
                th12d.append(float(i))

            if dimensionalities_thresholds[i] == "13D":
                th13d.append(float(i))

            if dimensionalities_thresholds[i] == "123D":
                th123d.append(float(i))

            if dimensionalities_thresholds[i] == "23D":
                th23d.append(float(i))

    # removing empty threshold list that has only one threshold

    if len(th0d) > 1:
        dT['0D'] = max(th0d) - min(th0d)

    if len(th1d) > 1:
        dT['1D'] = max(th1d) - min(th1d)

    if len(th2d) > 1:
        dT['2D'] = max(th2d) - min(th2d)

    if len(th3d) > 1:
        # 0.0 and 0.1 are always 3D so we remove them scoring
        if max(th3d) != 0.1:
           dT['3D'] = max(th3d) - min(th3d)

    if len(th01d) > 1:
        dT['01D'] = max(th01d) - min(th01d)

    if len(th02d) > 1:
        dT['02D'] = max(th02d) - min(th02d)

    if len(th03d) > 1:
        dT['03D'] = max(th03d) - min(th03d)

    if len(th012d) > 1:
        dT['012D'] = max(th012d) - min(th012d)

    if len(th013d) > 1:
        dT['013D'] = max(th013d) - min(th013d)

    if len(th023d) > 1:
        dT['023D'] = max(th023d) - min(th023d)

    if len(th12d) > 1:
        dT['12D'] = max(th12d) - min(th12d)

    if len(th13d) > 1:
        dT['13D'] = max(th13d) - min(th13d)

    if len(th123d) > 1:
        dT['123D'] = max(th123d) - min(th123d)

    if len(th23d) > 1:
        dT['23D'] = max(th23d) - min(th23d)

    #Normalize scores with Maximum force constatnt in structure
    dimen_score = {key: (value / maxforceconstant) for key, value in dT.items()}

    return dimen_score

