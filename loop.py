#!/usr/bin/env python

import sys

import ROOT


def savehist(hist, histname):
    """At the end of the function, there are no more references to `file`.
    The `TFile` object gets deleted, which in turn saves and closes
    the ROOT file."""
    # myfile = ROOT.TFile.Open("histo.root", "RECREATE")
    myfile.WriteObject(hist, histname)
    print("Wrote %s to histo.root"%histname)


printStuff = False

try:
    input = raw_input
except:
    pass

if len(sys.argv) < 2:
    print(" Usage: Example1.py input_file")
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
myfile = ROOT.TFile.Open("histo.root", "RECREATE")

# Create chain of root trees
chain = ROOT.TChain("Delphes")
chain.Add(inputFile)

# Create object of class ExRootTreeReader
treeReader = ROOT.ExRootTreeReader(chain)
numberOfEntries = treeReader.GetEntries()

# Get pointers to branches used in this analysis
branchGenJet = treeReader.UseBranch("GenJet")
# branchElectron = treeReader.UseBranch("Electron")

# Book histograms
# TH1F::TH1F(const char* name, const char* title, int nbinsx, double xlow, double xup) =>
histGenJetPT = ROOT.TH1F("GenJet_pt", "GenJet P_{T}; GenJet PT; #", 100, 0.0, 100.0)
histGenJetM = ROOT.TH1F("GenJet_mass", "GenJet Mass; GenJet Mass; #", 100, 0.0, 10.0)
# TH2F::TH2F(const char* name, const char* title, int nbinsx, double xlow, double xup, int nbinsy, double ylow,
# double yup) =>
histPartVsPT = ROOT.TH2F(
    "# of particles Vs pt", "Number of Particles Vs GenJet P_{T}; GenJet P_{T}; # of particles",
    100, 0.0, 500.0, 50, 0.0, 50.0)

# Loop over all events
for entry in range(0, numberOfEntries):
    # Load selected branches with data from specified event
    treeReader.ReadEntry(entry)

    # If event contains at least 1 GenJet
    # if branchGenJet.GetEntries() > 0:
    for ijet in range(branchGenJet.GetEntries()):
        # Take first GenJet
        GenJet = branchGenJet.At(ijet)

        # Plot GenGet.M() and then throw away GenJets that have a low mass
        histGenJetM.Fill(GenJet.Mass)
        if GenJet.Mass < 1:
            continue

        # Plot GenJet transverse momentum
        histGenJetPT.Fill(GenJet.PT)
        histPartVsPT.Fill(GenJet.PT, GenJet.NCharged)

        # Print GenJet transverse momentum
        if printStuff:
            print("GenJet.PT ", GenJet.PT)
            print("GenJet.Particles ", GenJet.Particles)
            print("GenJet.NCharged ", GenJet.NCharged)

# Show resulting histograms
c0 = ROOT.TCanvas()
c0.Update()
histGenJetPT.Draw()
c0.Print("GenJetPT.png")
c0.Clear()

c0.Update()
histGenJetM.Draw()
c0.Print("GenJetMass.png")
c0.Clear()

c0.Update()
histPartVsPT.SetContour(1000)
profx = histPartVsPT.ProfileX("profilex", 0, 100)
profx.Draw()
c0.Print("PartVsPTprofx.png")
savehist(histPartVsPT, "PartVsPT")
# histPartVsPT.SetStats(0)
histPartVsPT.Draw("colz")
c0.Print("PartVsPT.png")
c0.Clear()

# Save resulting histograms to .root file
savehist(histGenJetPT, "GenJetPT")


print("Done!")
