Run on LHE file and produce hepmc file

2 steps:
1. Read an input file (config file) and creates a run file
    ```bash
    ./scripts/herwig.sh read configs/herwig_lhe.in
    ```
2. Step produced `LHE.run` file, the next step reads the run file and generates events. The result is saved in an `hepmc` file.
    ```bash
    ./scripts/herwig.sh run LHE.run -N 50000
    ```
Make tree using Delphes that reads the `hepmc` file.
```bash
./scripts/delphes.sh card.tcl output.root MG5-Herwig_events.hepmc
```

Make tree using Delphes that reads the `hepmc` file.
```bash
./scripts/delphes.sh card.tcl output.root MG5-Herwig_events.hepmc
```

You can use `./scripts/delphes.sh` to run pyroot script that produce plots
```bash
./scripts/delphes.sh loop.py output.root herwig
```