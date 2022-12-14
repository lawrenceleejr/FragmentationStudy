#!/usr/bin/env python

import sys
import os
import glob
from threading import Timer

def exit():
    print("Exiting due to timeout...")
    os.system("docker run --rm -t -v $PWD:$PWD -w $PWD scailfin/madgraph5-amc-nlo:mg5_amc3.3.1 'rm -r eeToJJJ/Events/*'")
    os.system("docker run --rm -t -v $PWD:$PWD -w $PWD scailfin/madgraph5-amc-nlo:mg5_amc3.3.1 'rm eeToJJJ/RunWeb'")
    os.system("docker run --rm -t -v $PWD:$PWD -w $PWD ghcr.io/scipp-atlas/mario-mapyde/delphes 'rm Delphes-3.5.0/Frag_Study/*'")
    os.system("docker run --rm -t -v $PWD:$PWD -w $PWD scailfin/madgraph5-amc-nlo:mg5_amc3.3.1 'exit'")
    os.system("docker run --rm -t -v $PWD:$PWD -w $PWD ghcr.io/scipp-atlas/mario-mapyde/delphes 'exit'")
    os._exit(os.EX_OK)

try:
    input = raw_input
except:
    pass

if len(sys.argv) < 2:
    print(" Usage: auto.py results_name")
    sys.exit(1)

# Starts a timer to end the script after ten minutes
timer = Timer(150, exit)
timer.start()


results_name = sys.argv[1]

print("Beginning...")

# Generates events after parameter change
os.system("docker run --rm -t -v $PWD:$PWD -w $PWD scailfin/madgraph5-amc-nlo:mg5_amc3.3.1 "
          "'./eeToJJJ/bin/generate_events -f'")
# Copies and unzips new .hepmc
if len(glob.glob("eeToJJJ/Events/run_01/*hepmc.gz")) == 0:
    os.system("cp eeToJJJ/Events/run_01/*.hepmc Delphes-3.5.0/Frag_Study/pythia8_events_" + results_name + ".hepmc")
elif os.path.exists(glob.glob("eeToJJJ/Events/run_01/*hepmc.gz")[0]):
    os.system("cp eeToJJJ/Events/run_01/*.hepmc.gz Delphes-3.5.0/Frag_Study/pythia8_events_"+results_name+".hepmc.gz")
    os.system("gunzip Delphes-3.5.0/Frag_Study/pythia8_events_"+results_name+".hepmc.gz")
else:
    sys.exit("No hepmc file")

timer.cancel()
# Runs .hepmc through Delphes creating a .root
os.system("docker run --rm -t -v $PWD:$PWD -w $PWD ghcr.io/scipp-atlas/mario-mapyde/delphes "
          "'./Delphes-3.5.0/DelphesHepMC2 Delphes-3.5.0/cards/delphes_card_CMS.tcl "
          "Delphes-3.5.0/Frag_Study/eeToJJJ_"+results_name+".root "
          "Delphes-3.5.0/Frag_Study/pythia8_events_"+results_name+".hepmc'")
# Creates plots from the new .root
os.system("docker run --rm -t -v $PWD:$PWD -w $PWD ghcr.io/scipp-atlas/mario-mapyde/delphes 'cd Delphes-3.5.0 && "
          "python ../FragmentationStudy/loop.py Frag_Study/eeToJJJ_"+results_name+".root "
          "eeToJJJ_"+results_name+"'")
# Removes old run files
os.system("docker run --rm -t -v $PWD:$PWD -w $PWD scailfin/madgraph5-amc-nlo:mg5_amc3.3.1 'rm -r "
          "eeToJJJ/Events/run_*'")
# Removes .hepmc files but preserves .root files
os.system("docker run --rm -t -v $PWD:$PWD -w $PWD ghcr.io/scipp-atlas/mario-mapyde/delphes 'rm "
          "Delphes-3.5.0/Frag_Study/pythia8_events_"+results_name+".hepmc'")
# Removes .hepmc and .root files
# os.system("docker run --rm -t -v $PWD:$PWD -w $PWD ghcr.io/scipp-atlas/mario-mapyde/delphes 'rm "
#           "Delphes-3.5.0/Frag_Study/*'")
# Displays profx.png
# os.system("pwd")
# os.system("display ../FragmentationStudy/plots/eeToJJJ_"+results_name+"_PartVsPprofx.png")
