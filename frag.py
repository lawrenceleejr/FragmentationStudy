#!/usr/bin/env python

import sys
import ROOT
import math
import numpy as np


def savehist(hist, histname):
    """At the end of the function, there are no more references to `file`.
    The `TFile` object gets deleted, which in turn saves and closes
    the ROOT file."""
    myfile.WriteObject(hist, histname)


printStuff = True
printHistograms = False

try:
    input = raw_input
except:
    pass

if len(sys.argv) < 3:
    print(" Usage: frag.py LEP-1000.root results_name")
    sys.exit(1)

print("Beginning...")
ROOT.gSystem.Load("libDelphes")

try:
    ROOT.gInterpreter.Declare('#include "classes/DelphesClasses.h"')
    ROOT.gInterpreter.Declare('#include "external/ExRootAnalysis/ExRootTreeReader.h"')
except:
    pass

inputFile = sys.argv[1]

# Create .root file to save histograms
# Path starts in Delphes directory
myfile = ROOT.TFile.Open("../FragmentationStudy/root_files/"+sys.argv[2]+"_histograms.root", "RECREATE")

# Create chain of root trees
chain = ROOT.TChain("Delphes")
chain.Add(inputFile)

# Create object of class ExRootTreeReader
treeReader = ROOT.ExRootTreeReader(chain)
numberOfEntries = treeReader.GetEntries()

# Get pointers to branches used in this analysis
branchGenJet = treeReader.UseBranch("GenJet")
branchParticle = treeReader.UseBranch("Particle")
branchGenMissingET = treeReader.UseBranch("GenMissingET")

if printHistograms is True:
    # Book histograms
    # TH1F::TH1F(const char* name, const char* title, int nbinsx, double xlow, double xup) =>
    histGenJetP = ROOT.TH1F("GenJet_p", "GenJet P; GenJet P; #", 100, 0.0, 100.0)
    histGenJetPT = ROOT.TH1F("GenJet_pt", "GenJet PT; GenJet PT; #", 100, 0.0, 100.0)
    histGenJetM = ROOT.TH1F("GenJet_mass", "GenJet Mass; GenJet Mass; #", 100, 0.0, 10.0)
    # TH2F::TH2F(const char* name, const char* title, int nbinsx, double xlow, double xup, int nbinsy, double ylow,
    # double yup) =>
    histPartVsP = ROOT.TH2F(
        "# of particles Vs p", "Number of Particles Vs GenJet P; GenJet P; # of particles",
        100, 0.0, 500.0, 50, 0.0, 50.0)
    histPartVsPT = ROOT.TH2F(
        "# of particles Vs pt", "Number of Particles Vs GenJet PT; GenJet PT; # of particles",
        100, 0.0, 500.0, 50, 0.0, 50.0)

# Four momentum vector
px, py, pz, E = 0, 0, 0, 0
four_vector = [px, py, pz, E]

# Loop over all events
event_num = 0
pt_num = 0

#for entry in range(0, numberOfEntries):
for entry in range(0, 10):
    event_num += 1
    # four_vector = [px, py, pz, E]
    # Load selected branches with data from specified event
    treeReader.ReadEntry(entry)

    # Determines if event has a high PT photon
    highPtPhoton = False
    hasJetAbove50GeV = False

    # Determines if event has a jet with pt < 50 GeV
    for ijet in range(branchGenJet.GetEntries()):
        GenJet = branchGenJet.At(ijet)
        if 100 < GenJet.PT < 150:
            jetInInterval = True
            print(GenJet.Particles.GetEntries())
            sumPT = 0
            sumE = 0
            for iparticle in range(GenJet.Particles.GetEntries()):
                Particle = GenJet.Particles.At(iparticle)
                four_vector[0] += Particle.Px
                four_vector[1] += Particle.Py
                four_vector[2] += Particle.Pz
                four_vector[3] += Particle.E
                sumPT += Particle.PT
                sumE += Particle.E
                # print(Particle.E)

            mag = np.array(four_vector)
            print(four_vector)
            print("Magnitude of four-vector: %f" % np.linalg.norm(mag))
            print("GenJet.PT: %f" % GenJet.PT)
            print("SumPT of particles: %f" % sumPT)
            print("SumE of particles: %f" % sumE)
            break

    if hasJetAbove50GeV is True:
        for ijet in range(branchGenJet.GetEntries()):
            # Take first GenJet
            GenJet = branchGenJet.At(ijet)
            # GenMissingET = branchGenMissingET.At(ijet)
            # if GenJet.PT < 50:
                # hasJetAbove50GeV = True
            if printStuff:
                P = GenJet.PT * math.cosh(GenJet.Eta)
                print("Event: %d" % event_num)
                print("Jet: %d" % ijet)
                # print("GenMissingET.MET", GenMissingET.MET)
                # print("GenJet.Particles ", GenJet.Particles)
                # print("Particle Unique ID: ", Particle.fUniqueID)
                print("GenJet.PT: %f" % GenJet.PT)
                print("GenJet.P: %f" % P)
                # print("GenJet.Eta: ", GenJet.Eta)
                # print("GenJet.Phi: ", GenJet.Phi)
                print("GenJet.NCharged %d" % GenJet.NCharged)
                print("GenJet.NNeutrals %d" % GenJet.NNeutrals)

            if printHistograms is True:
                P = GenJet.PT * math.cosh(GenJet.Eta)
                histGenJetM.Fill(GenJet.Mass)
                histGenJetP.Fill(P)
                histPartVsP.Fill(P, GenJet.NCharged + GenJet.NNeutrals)
                histGenJetPT.Fill(GenJet.PT)
                histPartVsPT.Fill(GenJet.PT, GenJet.NCharged + GenJet.NNeutrals)

        print(" ")
        for iparticle in range(branchParticle.GetEntries()):
            Particle = branchParticle.At(iparticle)
            # four_vector[0] += Particle.Px
            # four_vector[1] += Particle.Py
            # four_vector[2] += Particle.Pz
            # four_vector[3] += Particle.E
            # print("Particle Status: %d" % Particle.Status)
            print("Particle ID: %d, Particle Status: %d, Px: %f, Py: %f, Pz: %f, E: %f" % (Particle.PID, Particle.Status, Particle.Px, Particle.Py, Particle.Pz, Particle.E))

        mag = np.array(four_vector)
        print("Magnitude of particle four vector: %f" % np.linalg.norm(mag))
        print(" ")

    if hasJetAbove50GeV is True:
        pt_num += 1
        # mag = np.array(four_vector)
        # print("Magnitude: %f" % np.linalg.norm(mag))
        print(" ")

# print("number of events PT < 50: %d" % pt_num)
# mag = np.array(four_vector)
# print("Magnitude: ", np.linalg.norm(mag))
# print("num of status=1 ", num)

if printHistograms is True:
    # Show resulting histograms
    c0 = ROOT.TCanvas()
    c0.Update()
    histGenJetP.Draw()
    c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_GenJetP.png")
    c0.Clear()

    c0.Update()
    histGenJetPT.Draw()
    c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_GenJetPT.png")
    c0.Clear()

    c0.Update()
    histGenJetM.Draw()
    c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_GenJetMass.png")
    c0.Clear()

    c0.Update()
    histPartVsP.SetContour(1000)
    profx = histPartVsP.ProfileX("profilex", 0, 100)
    profx.Draw()
    c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPprofx.png")
    histPartVsP.Draw("colz")
    c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsP.png")
    c0.Clear()

    c0.Update()
    histPartVsPT.SetContour(1000)
    pt_profx = histPartVsPT.ProfileX("profilex", 0, 100)
    pt_profx.Draw()
    c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPTprofx.png")
    histPartVsPT.Draw("colz")
    c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPT.png")
    c0.Clear()

    # Save resulting histograms to .root file
    savehist(histPartVsP, "PartVsP")
    savehist(histGenJetP, "GenJetP")
    savehist(profx, "PartVsPprofx")
    savehist(histPartVsPT, "PartVsPT")
    savehist(histGenJetPT, "GenJetPT")
    savehist(pt_profx, "PartVsPTprofx")
    savehist(histGenJetM, "GenJetMass")


print("Done!")
