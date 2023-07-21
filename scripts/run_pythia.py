#!/usr/bin/python3

import os,sys

shower = 2 #using vincia
if len(sys.argv)>1 and sys.argv[1]=="1":
    shower = 1 #using pythia shower
    print("Using PYTHIA shower")
else:
    print("Using VINCIA shower")


def RunOn(LHEF):
    IMAGE='matthewfeickert/pythia-python:latest'

    COMPILER="g++ main00.cc -o main00 -I/usr/local/venv/include -O2 -pedantic -W -Wall -Wshadow -fPIC -pthread \
        -std=c++14 -DGZIP -lz -L/usr/local/venv/lib -Wl,-rpath,/usr/local/venv/lib -lpythia8 -ldl \
        -I/usr/local/venv/include -L/usr/local/venv/lib -Wl,-rpath,/usr/local/venv/lib \
        -lHepMC3 -DHEPMC3;"

    EXECUTOR="./main00 -e 1000 -s {} -f {};".format(shower, LHEF)

    CLEANER="rm main00"

    CMD="$COMPILER";"$EXEC";"$CLEANER"

    CMD="docker run -i --rm  -u `id -u $USER`:`id -g` -v $PWD:/home/docker/work {} '{} {} {}'".format(IMAGE,COMPILER,EXECUTOR,CLEANER)

    os.system(CMD)

#LHEF = sys.argv[1] #eeToZgamma_50k_unweighted_events.lhe.gz
#RunOn(LHEF)

inputLHE=["data/eeToJJJ_50k_unweighted_events.lhe.gz"]


for i,f in enumerate(inputLHE):
    RunOn(f)
    #os.system('mv {} {}/'.format(ff,path))