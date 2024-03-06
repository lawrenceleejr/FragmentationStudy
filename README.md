# FragmentationStudy

Using MadGraph, we aim to produce particle level samples of pure QCD, like:

```
e+ e- > j j j
```

(And later we may want to have `p p > j j j`)

and also samples that happen via boosted color singlets such as

```
e+ e- > z a (z > j j)
```

And then we'll compare their fragmentation as a function of lab frame pT.


## Run on LHE file and produce hepmc file

<!--### HERWIG

1. Read an input file (config file) and creates a run file named `LHE.run`
    ```bash
    cd scripts
    ./herwig.sh read herwig_lhe.in
    ```
2. Once `LHE.run` file is created, the next step reads the run file and generates events. The result is saved in an `hepmc` file.
    ```bash
    ./scripts/herwig.sh run LHE.run -N 50000
    ```-->

### PYTHIA

Run using vincia shower
```bash
./run_pythia
```

The above command compile and run `main00.cc`. The main command is `./main00 -e -1 -s {} -f {}`, where `-e` is number of events (`-1` over all generated events), and `-s` for shower mode and `-f` for LHE input file.

The output is HEPMC file with same basename as LHE input file defined inside ` run_pythia`.

Note: To run pythia shower use `./run_pythia 1`


## Run on HEPMC file and produce ROOT TREE


Make ROOT tree using Delphes that reads the `hepmc` file.
```bash
./run_delphes card.tcl input_hepmc_file
```

## newloop.py

## Run loop.py

```bash
./run_delphes loop.py input_root_file results_name
```
