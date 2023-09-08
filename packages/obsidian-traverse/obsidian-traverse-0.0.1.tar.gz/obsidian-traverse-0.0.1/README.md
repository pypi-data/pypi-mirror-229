# obsidian-traverse

Recursively list all files linked by Obsidian note.

## Installation
```sh
pip install obsidian-traverse
```

## Usage
```
usage: obsidian-traverse [-h] -d DIRECTORY [--abspath] NOTES [NOTES ...]

Recursively list all files linked by Obsidian note.

positional arguments:
  NOTES                 Notes to traverse

options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Vault directory
  --abspath             Output absolute paths of linked files
```

Fixes for emergent parsing problems are welcome!
