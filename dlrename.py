#! env python3
from subprocess import run
import sys

def main(verbose, dryrun, numchars, prefix, filenames):
    for filename in filenames:
        try:
            complete = run(["shasum", "-a256", filename], capture_output=True, encoding='utf-8', check=True)
        except:
            print(f'shasum on file "{filename}" failed!', file=sys.stderr)
            exit(complete.returncode)

        output = str(complete.stdout)
        hashchars = '-'.join([output[i:min(i+4,numchars)] for i in range(0,numchars,4)])
        newfilename = prefix + '-' + hashchars + '.csv'
        if verbose:
            print(f'rename {filename} to {newfilename}')

        try:
            if not dryrun:
                complete = run(["mv", filename, newfilename], check=True)
        except:
            print(f'File rename from "{filename}" to "{newfilename}" failed!', file=sys.stderr)
            exit(complete.returncode)

def version():
    print(f"* VERSION: {argv[0]} 0.0.0")


def info():
    version()
    print(f"* INFO: command is \"{' '.join(argv)}\"")
    print(f"* INFO: using Python {sys.version}")


def usage(cmd):
    print(f"Usage: {cmd} [OPTION]... PREFIX [FILE]...")
    print("Rename files with hash-based names.")
    print()
    print("The options below may be used to control the processing of the input file.")
    print("  -h  --help             print this help information")
    print("  -v  --version          print the program version number")
    print("  -i, --info             print info about program")
    print("  -n, --num-hash-chars   number of hash chars in rename")
    print("  --dry-run              don't actually make modifications")          


if __name__ == "__main__":
    verbose = False
    dryrun = False
    numchars = 12
    prefix = ''
    filenames = []

    argv = sys.argv
    if len(argv) <= 1:
        print(f"{argv[0]}: missing arguments", file=sys.stderr)
        print(f"Try '{argv[0]} --help' for more information")
        exit(1)

    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == '--help' or arg == '-h':
            usage(argv[0])
            exit()
        elif arg == '--version' or arg == '-V':
            version()
            exit()
        elif arg == '--verbose' or arg == '-v':
            verbose = True
        elif arg == '--info' or arg == '-i':
            info()
        elif arg == '--dry-run':
            dryrun = True
        elif arg == '--num-hash-chars' or arg == '-n':
            i +=  1
            try:
                numchars = int(argv[i])
                if numchars < 8 or numchars > 64:
                    print(f"Error, number of hash chars out of range (8 to 64)", file=sys.stderr)
                    exit(1)
            except:
                print(f"Error in argment list, expected an integer after {arg}", file=sys.stderr)
                exit(1)
        elif arg[0] != '-':
            prefix = arg
            filenames = argv[i+1:]
            break
        i += 1

    # check command arguments
    if prefix == '' or ' ' in prefix:
        printf("Error, missing prefix or prefix contains a space.", file=sys.stderr)
        exit(1)
    if len(filenames) == 0:
        printf("Error, no file names given in command.", file=sys.stderr)
        exit(1)

    if verbose:
        complete = run(["pwd"], capture_output=True, encoding='utf-8')
        print(f"Running in directory {complete.stdout}")
        print(f"Renaming files: {filenames}")
        print(f"Number of hash chars: {numchars}")
        print(f"Prefix: {prefix}")
        if dryrun:
            print("Doing a dry run")
        print()

    main(verbose, dryrun, numchars, prefix, filenames)

