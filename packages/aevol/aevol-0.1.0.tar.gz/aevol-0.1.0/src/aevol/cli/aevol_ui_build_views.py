import sys
import getopt

from aevol import __version__ as aevol_version
from aevol.models.environment import Environment
from aevol.models.individual import Individual
from aevol.visual import fitness_view, grid_view
from aevol.visual.rna_view import RnaView
from aevol.visual.protein_view import ProteinView

def main():
    """
    Create graphical views from the provided input
    """
    envfile = None
    gridfile = None
    indivfile = None
    outdir = "."
    display_legend = True

    print_header()

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "e:g:hi:o:",
                                   ["envfile=", "gridfile=", "help", "indivfile=", "outdir="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        print_usage()
        sys.exit(2)
    for opt, val in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        elif opt in ("-e", "--envfile"):
            envfile = val
        elif opt in ("-g", "--gridfile"):
            gridfile = val
        elif opt in ("-i", "--indivfile"):
            indivfile = val
        elif opt in ("-o", "--outdir"):
            outdir = val
        else:
            assert False, "unhandled option"

    # Print help if nothing to do
    if envfile is None and gridfile is None and indivfile is None:
        print("the data you have provided is not sufficient to draw anything")
        print_usage()

    individual = Individual.from_json_file(indivfile) if indivfile else None
    environment = Environment.from_json_file(envfile) if envfile else None

    # build those views whose required data have been provided
    if individual:
        rna_view = RnaView()
        out = rna_view.draw(individual, display_legend, outdir, 'RNAS')
        print('RNA view written to ' + out)

        protein_view = ProteinView()
        out = protein_view.draw(individual, display_legend, outdir, 'Proteins')
        print('Protein view written to ' + out)

    if individual and environment:
        out = fitness_view.draw(individual, environment, display_legend, outdir, 'Fitness')
        print('Fitness view written to ' + out)

    if gridfile:
        out = grid_view.draw(gridfile, display_legend, outdir, 'Grid')
        print('Grid view written to ' + out)


def print_header():
    print("aevol_build_views (" + aevol_version + ") Inria - Biotic")


def print_usage():
    print(r'''Usage : aevol_build_views -h or --help
   or : aevol_build_views [-e ENV_FILE] [-i INDIV_FILE] [-p POP_FILE] [-o OUT_DIR]''')


def print_help():
    print(r'''******************************************************************************
*                                                                            *
*                        aevol - Artificial Evolution                        *
*                                                                            *
* Aevol is a simulation platform that allows one to let populations of       *
* digital organisms evolve in different conditions and study experimentally  *
* the mechanisms responsible for the structuration of the genome and the     *
* transcriptome.                                                             *
*                                                                            *
******************************************************************************

aevol_build_views: create graphical views from the provided input 
''')
    print_usage()
    print(r'''
Options
  -h, --help
	print this help, then exit
  -e, --envfile ENV_FILE
	specify environment file
  -i, --indivfile INDIV_FILE
	specify individual file
  -p, --popfile POP_FILE
	specify population file
  -o, --outdir OUT_DIR (default: .)
	specify output directory''')


if __name__ == "__main__":
    main()
