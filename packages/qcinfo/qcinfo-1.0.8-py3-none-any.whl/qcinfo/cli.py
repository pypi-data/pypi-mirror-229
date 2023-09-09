from resultsFile import getFile
import argparse

def main():
    # read the command line arguments
    parser = argparse.ArgumentParser(description='Provide the QC file name to be checked')
    parser.add_argument('file', metavar='file', type=str, nargs='+',
                        help='a QC calculation file to be processed')

    args = parser.parse_args()

    num_files = len(args.file)


    print("__________________________________________________________")
    print("                                                          ")
    print("             Quantum Chemistry File Insights              ")
    print("               By: Ravindra Shinde (2023)                 ")
    print("                   r.l.shinde@utwente.nl                  ")
    print("__________________________________________________________")
    print("----------------------------------------------------------")


    for ind, f in enumerate(args.file):
        file = getFile(f)
        filetype = str(file).split('.')[-1].split()[0]


        print("File ", ind+1, " of ", num_files, "  :: ", f)
        print("File type        :: ", filetype)
        print("MO types         :: ", file.mo_types)

        print("----------------------------------------------------------")


if __name__ == "__main__":
    main()