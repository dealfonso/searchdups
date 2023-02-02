import glob
import os.path
import hashlib
from tqdm import tqdm
import itertools
import re
import sys
from .version import VERSION

hashAlgorithm = None

def get_digest(file_path, full = False):
    global hashAlgorithm

    if hashAlgorithm == "md5":
        h = hashlib.md5()
    elif hashAlgorithm == "sha256":
        h = hashlib.sha256()
    else: 
        return None

    blockSize = 4 * 1024 # h.block_size

    if full:
        maxSize = None
    else:
        maxSize = blockSize

    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(blockSize)
            if not chunk:
                break
            h.update(chunk)
            if maxSize is not None:
                maxSize = maxSize - h.block_size
                if maxSize < 0:
                    break

    return h.hexdigest()

def annotateDigest(fileToProcess, filesFound, digest = None):
    if digest is None:
        digest = get_digest(fileToProcess, True) + "*"

    if digest not in filesFound:
        filesFound[digest] = []

    filesFound[digest].append(os.path.realpath(fileToProcess))

def searchFiles(folders, regexps = [re.compile(".*")], regexpouts = [], showProgress = False, recurse = False, showHidden = False):
    filesFound = {}
    iFolder = 0
    totalFiles = 0

    if showProgress:
        progressBar = tqdm(total = len(folders), unit="folder")

    def selectHidden(f):
        if showHidden:
            return not os.path.basename(f) in [ ".", ".." ]
        else:
            return not os.path.basename(f).startswith(".")

    while iFolder < len(folders):
        folderToProcess = folders[iFolder]
        folderToProcess = folderToProcess.rstrip("/")
        iFolder = iFolder + 1

        if showHidden:
            possibleFiles = list(itertools.chain(glob.glob(f"{folderToProcess}/*"), glob.glob(f"{folderToProcess}/.*")))
        else:
            possibleFiles = glob.glob(f"{folderToProcess}/*")

        if recurse:
            subFolders = [ d for d in map(lambda x: os.path.realpath(x), possibleFiles) if os.path.isdir(d) and selectHidden(d) and (d not in folders) ]
            folders.extend(subFolders)
            if showProgress:
                progressBar.total = progressBar.total + len(subFolders)

        possibleFiles
        filesToProcess = [ d for d in map(lambda x: os.path.realpath(x), possibleFiles) if os.path.isfile(d) and selectHidden(d) ]

        for fileToProcess in filesToProcess:

            matches = False
            filenameToProcess = os.path.basename(fileToProcess)
            for regexp in regexps:
                if regexp.match(filenameToProcess):
                    matches = True
                    break

            if not matches: continue

            matches = False
            for regexp in regexpouts:
                if regexp.match(filenameToProcess):
                    matches = True
                    break

            if matches: continue

            # calculate the number of total files
            totalFiles = totalFiles + 1

            if hashAlgorithm is None:
                # Not using hash
                if filenameToProcess not in filesFound:
                    filesFound[filenameToProcess] = []
                filesFound[filenameToProcess].append(fileToProcess)

            else:
                # Using hash
                digest = get_digest(fileToProcess, False)

                # If the digest exists, we'll reconsider to calculate the new digest
                if digest in filesFound:

                    if isinstance(filesFound[digest], list):
                        # we'll calculate the full digest for each
                        for file in filesFound[digest]:
                            annotateDigest(file, filesFound)

                        # Delete the list to not to use the partial digest anymore
                        filesFound[digest] = None

                    annotateDigest(fileToProcess, filesFound)
                else:
                    annotateDigest(fileToProcess, filesFound, digest)
        if showProgress:
            progressBar.update()
    return filesFound, iFolder, totalFiles

def searchdups():
    """Application that searches for duplicate files in a folder.
    """
    import argparse
    parser = argparse.ArgumentParser(allow_abbrev=False, description=searchdups.__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(help="Folders to check", dest="foldersToCheck", nargs="*", default=["."])
    parser.add_argument("-f", "--filter", dest="filters", action="append", default=[], help="filter for the name of the file, using sh-like wildcards (e.g. *.jpg); the filter only for the base name of the file (neither for the whole path, nor the relative path)")
    parser.add_argument("-F", "--filter-out", dest="filterouts", action="append", default=[], help="filter out the name of the file, using sh-like wildcards (e.g. *.jpg); the filter only for the base name of the file (neither for the whole path, nor the relative path)")
    parser.add_argument("-e", "--regexp", dest="regexps", action="append", default=[], help="regular expression for the name of the file; the regular only for the base name of the file (neither for the whole path, nor the relative path)")
    parser.add_argument("-E", "--regexp-exclude", dest="regexpouts", action="append", default=[], help="regular expression for the name of the file to exclude it; the regular only for the base name of the file (neither for the whole path, nor the relative path)")
    parser.add_argument("-H", "--hash", dest="useHash", default="md5", choices=["filename", "md5", "sha256"], help="use hashes instead of filenames")
    parser.add_argument("-p", "--progress", dest="progress", default=False, action="store_true", help="show a progress bar")
    parser.add_argument("-r", "--recurse", dest="recurse", default=False, action="store_true", help="get into found folders to search for files")
    parser.add_argument("-a", "--hidden-files", dest="hidden", default=False, action="store_true", help="consider hidden files and folders")
    parser.add_argument("-s", "--summarize", dest="summarize", default=False, action="store_true", help="summarize the amount of files and folder checked")
    parser.add_argument("-o", "--output-file", dest="outputFile", default=None, help="name of the file to where output the result (otherwise the output will go to stdout)")
    parser.add_argument("--force", dest="force", default=False, action="store_true", help="force overwrite if output file exists")
    parser.add_argument("-v", "--version", help="Show the version of the program", action="version", version=VERSION)

    args = parser.parse_args()

    filesFound = {}

    if args.useHash == "filename":
        args.useHash = None

    if args.outputFile is not None:
        if os.path.exists(args.outputFile) and not args.force:
            print(f"refusing to overwrite file {args.outputFile}")
            sys.exit(1)

    regexps = []
    for filter in args.filters:
        filter = filter.replace("**/", "<<DAST>>")
        filter = filter.replace("**", "*")
        filter = filter.replace("*", "<<SAST>>")
        filter = filter.replace(".", "\\.")
        filter = filter.replace("?", ".")
        filter = filter.replace("/", "\\/")
        filter = filter.replace("<<SAST>>", "[^\/]*")
        filter = filter.replace("<<DAST>>", "(.+\\/)*")
        filter = f"^{filter}$"
        regexps.append(re.compile(filter))

    for regexp in args.regexps:
        regexps.append(re.compile(regexp))

    if len(regexps) == 0:
        regexps = [ re.compile(".*") ]

    regexpouts = []
    for filter in args.filterouts:
        filter = filter.replace("**/", "<<DAST>>")
        filter = filter.replace("**", "*")
        filter = filter.replace("*", "<<SAST>>")
        filter = filter.replace(".", "\\.")
        filter = filter.replace("?", ".")
        filter = filter.replace("/", "\\/")
        filter = filter.replace("<<SAST>>", "[^\/]*")
        filter = filter.replace("<<DAST>>", "(.+\\/)*")
        filter = f"^{filter}$"
        regexpouts.append(re.compile(filter))

    for regexp in args.regexpouts:
        regexpouts.append(re.compile(regexp))

    global hashAlgorithm
    hashAlgorithm = args.useHash

    filesFound, totalFolders, totalFiles = searchFiles(args.foldersToCheck, regexps=regexps, regexpouts=regexpouts, showProgress=args.progress, recurse=args.recurse, showHidden=args.hidden)

    duplicateFiles = 0

    if args.outputFile is None:
        for digest, files in filesFound.items():
            if files is None:
                continue
            if len(files) > 1:
                duplicateFiles = duplicateFiles + 1
                print(f"> {digest}\n" + "\n".join(files))
    else:
        with open(args.outputFile, "wt") as outputFile:
            for digest, files in filesFound.items():
                if files is None:
                    continue
                if len(files) > 1:
                    duplicateFiles = duplicateFiles + 1
                    outputFile.write(";".join(files)+"\n")

    if args.summarize:
        print(f'inspected {totalFolders} folders and {totalFiles} files')
        print(f'found {duplicateFiles} duplicate file(s)')