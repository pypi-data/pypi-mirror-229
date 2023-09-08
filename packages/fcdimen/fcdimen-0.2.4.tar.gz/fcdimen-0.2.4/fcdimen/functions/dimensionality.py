def calc_dimension(supercell_indices, supercell_doubled_indices):
    """Calculating dimensionality

    Parameters:
    supercell_indices: list
     generate list of initial Supercell clusters indices
    supercell_doubled_indices: list
     generate list of doubled Supercell clusters indices

    Returns:
    dimensionality: String
     Dimensionality of structure (0D, 1D, 2D, 3D, mix or unknown)
    """
    supercell_clusters = {}
    for i in range(len(supercell_indices)):
        supercell_clusters[min(list(supercell_indices[i]))] = len(list(supercell_indices[i]))

    supercell_doubled_clusters = {}
    for i in range(len(supercell_doubled_indices)):
        supercell_doubled_clusters[min(list(supercell_doubled_indices[i]))] = len(list(supercell_doubled_indices[i]))

    dimensionalities = []
    for i in supercell_clusters.keys():
        if supercell_clusters[i] == supercell_doubled_clusters[i] / 2:
           dimensionalities.append(1)
        elif supercell_clusters[i] == supercell_doubled_clusters[i] / 4:
           dimensionalities.append(2)
        elif supercell_clusters[i] == supercell_doubled_clusters[i] / 8:
           dimensionalities.append(3)
        else:
           dimensionalities.append(0)
           
           
    # Preparing dimensionality string
    l = sorted(list(set(dimensionalities)))
    ans = ' '
    for i in l:
        ans = ans + str(i)

    if ans == ' ':
        dimensionality = "Unknown"
    else:
        dimensionality = ans + "D"
        dimensionality = dimensionality.strip()
        
    return dimensionality
