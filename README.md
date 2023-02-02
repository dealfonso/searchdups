# Search Duplicates (searchdups)

This is a simple application that searches for duplicate files in a set of folders. To check whether the files are identical or not, it makes use of `md5` or `sha256` algorithms, but the application calculates a _smart hash_ to enhance performance: the idea is to calculate a partial hash and finalize the calculation only if needed.

Additionally, this application includes a pseudo _hash_ that consists of checking whether the name of the files is the same. If using this _"hash algorithm"_, if the name of two files is the same, they are considered to be the same even if the content is not the same.

The basic usage is

```bash
$ searchdups -r . 
> 8f8db820d89c39029a0629094e0f18c9*
/Users/calfonso/Programacion/norepo/searchdups/a1.jpg
/Users/calfonso/Programacion/norepo/searchdups/a11.jpg
```

Some other features are:

- Select the hash algorithm (using parameter `-H`).
- Searching in subfolders (using flag `-r`).
- Considering hidden folders and files (using flag `-a`).
- Show a progress bar during the process (using flag `-p`).
- Selecting which files are processed (using `-f` parameter for _sh-like_ filters, or `-e` parameter for regular expressions).
- Exclude the files to process (using `-F` parameter for _sh-like_ filters, or `-E` parameter for regular expressions).
- Summarize the amount of files and folders considered (using flag `-s`).
- Get the result in a file (using parameter `-o`).

Please check the CLI help to get updated information about the usage of this tool.

## Installation

To install the tool you can clone the code and execute the next command inside the cloned folder

```shell
$ pip install .
```

or install it from the repositories:

```shell
$ pip install searchdups
```