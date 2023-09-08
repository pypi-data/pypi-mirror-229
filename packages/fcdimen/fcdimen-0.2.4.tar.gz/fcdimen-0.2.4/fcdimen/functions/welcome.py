from pkg_resources import parse_version
import fcdimen


# logo made by http://www.network-science.de/ascii/
def welcome_logo():
    """Show package logo"""
    print(
      r""" 
         _____ ____ ____  _                      
        |  ___/ ___|  _ \(_)_ __ ___   ___ _ __  
        | |_ | |   | | | | | '_ ` _ \ / _ \ '_ \ 
        |  _|| |___| |_| | | | | | | |  __/ | | |
        |_|   \____|____/|_|_| |_| |_|\___|_| |_|""")

    print("""
 *------------------------------------------------------*""")
    print(" |                FCDimen "+str(parse_version(fcdimen.__version__))+" (2023)                  |")
    print(""" |   Developers: M. Bagheri, E. Berger & H.-P. Komsa    |
 |   Documentation : https://github.com/fcdimen         |
 |   More information about method and citation:        |
 |   https://doi.org/10.1021/acs.jpclett.3c01635        |
 *------------------------------------------------------*
 """)
