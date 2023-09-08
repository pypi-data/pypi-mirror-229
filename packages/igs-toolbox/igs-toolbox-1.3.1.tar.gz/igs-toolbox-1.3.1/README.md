# igs-toolbox

## Description
This repository contains tools to convert files and check whether files follow a predefined schema.
Currently there is only one converter and formatChecker for one use case is implemented, but the idea is that it can be extended to more applications.

## Installation 

igs-toolbox is pip installable.

```bash
pip install igs-toolbox
```

## Usage

All tools can be used as a command line tools.

```bash
usage: jsonChecker.py [-h] -i INPUT -s {seqMetadata}

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Filepath to json file.
  -s {seqMetadata}, --schema {seqMetadata}
                        Schema to test against.
```


```bash
usage: convertSeqMetadata.py [-h] -i INPUT -o OUTPUT [-e ERROR_LOG]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Filepath to xlsx file.
  -o OUTPUT, --output OUTPUT
                        Filepath to output folder for json files.
  -e ERROR_LOG, --error_log ERROR_LOG
                        Filepath to log file.
```

```bash
usage: convertAnswerSets.py [-h] -i INPUT -o OUTPUT [-s SPECIES [SPECIES ...]]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Filepath to folder with answerset json files.
  -o OUTPUT, --output OUTPUT
                        Filepath to output folder for answerset txt files.
  -s SPECIES [SPECIES ...], --species SPECIES [SPECIES ...]
                        List of species for which to convert answersets.
```
                        