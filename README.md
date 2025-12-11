# OSproject3
## This project implements a command-line B-Tree index file manager for CS4348 Project 3 (Fall 2025).
## The program supports creating, inserting, searching, loading, printing, and extracting entries from a disk-based B-Tree.
## The index file format follows the project specification exactly:
###   - 512-byte fixed blocks
###   - Block 0 = file header
###   - Blocks 1..N = B-Tree nodes
###   - All integers stored as 8-byte big-endian
###   - Only three nodes maximum may be in memory at one time
###   - The B-Tree uses minimal degree T = 10, allowing:
###   - up to 19 keys per node
###   - up to 20 children


## The project contains the follwoing:
### project3.py: python file which handles the commands and executes the actions like creating index, insert key and value, searching key, loading index file to csv, printing index file contents, and extracting index file to output file
### tes.idx: index file created from program storing key header and contents
### output.txt: file used to load and extract key and value contents

## To run the program and all of its functionalities, one command is created for each function as follows:
### python3 project3.py create (indexfile)
### python3 project3.py insert (indexfile) (key) (value)
### python3 project3.py search (indexfile) (key)
### python3 project3.py load (indexfile) (csvfile)
### python3 project3.py print (indexfile)
### python3 project3.py extract (indexfile) (outputfile)
