#!/usr/bin/env python

import sys
import ROOT
import math


def savehist(hist, histname):
    """At the end of the function, there are no more references to `file`.
    The `TFile` object gets deleted, which in turn saves and closes
    the ROOT file."""
    myfile.WriteObject(hist, histname)


printStuff = False
# mult_switch = GenJet.NCharged + GenJet.NNeutrals
# mult_switch = GenJet.NCharged

try:
    input = raw_input
except:
    pass

if len(sys.argv) < 3:
    print(" Usage: loop.py input_root_file results_name")
    sys.exit(1)

print("Beginning...")
if os.path.exists('/.dockerenv'):
    print("Running in docker container")
    ROOT.gSystem.Load('/usr/local/share/delphes/delphes/libDelphes')
else:
    ROOT.gSystem.Load("libDelphes")

try:
    ROOT.gInterpreter.Declare('#include "classes/DelphesClasses.h"')
    ROOT.gInterpreter.Declare('#include "external/ExRootAnalysis/ExRootTreeReader.h"')
except:
    pass

inputFile = sys.argv[1]

# Create .root file to save histograms
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

# Some constants and such
partonID = [1, 2, 3, 4, 5, 6, 7, 8, 9, 21, -1, -2, -3, -4, -5, -6, -7, -8, -9, -21]
deltaRMax = 0.4

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

# Loop over all events
for entry in range(0, numberOfEntries):
    # Load selected branches with data from specified event
    treeReader.ReadEntry(entry)

    # If event contains at least 1 GenJet
    for ijet in range(branchGenJet.GetEntries()):
        GenJet = branchGenJet.At(ijet)
        highestEnergyParticle = 0
        particleIndex = -1
        highestEnergyPID = 0

        # Determines if a parton initiated the jet
        for iparticle in range(branchParticle.GetEntries()):
            Particle = branchParticle.At(iparticle)
            if Particle.PID in partonID:
                ParticleEta = Particle.Eta
                ParticlePhi = Particle.Phi
                JetEta = GenJet.Eta
                JetPhi = GenJet.Phi
                deltaEta = abs(JetEta - ParticleEta)
                deltaPhi = abs(JetPhi - ParticlePhi)
                if deltaPhi > math.pi:
                    deltaPhi = deltaPhi - (2 * math.pi)
                delta_R = math.sqrt(math.pow(deltaEta, 2) + math.pow(deltaPhi, 2))
                trackingEnergy = Particle.E
                if delta_R < deltaRMax and trackingEnergy > highestEnergyParticle:
                    highestEnergyParticle = trackingEnergy
                    particleIndex = iparticle
                    highestEnergyPID = Particle.PID

        # If the initiating parton is a gluon, throws away the jet
        if highestEnergyPID == 21:
            continue

        # Plot GenGet.M() and then throw away GenJets that have a low mass
        histGenJetM.Fill(GenJet.Mass)
        if GenJet.Mass < 0.01:
            continue

        # Plot GenJet transverse momentum
        P = GenJet.PT * math.cosh(GenJet.Eta)
        histGenJetP.Fill(P)
        histPartVsP.Fill(P, GenJet.NCharged + GenJet.NNeutrals)
        histGenJetPT.Fill(GenJet.PT)
        histPartVsPT.Fill(GenJet.PT, GenJet.NCharged + GenJet.NNeutrals)

        # Print GenJet transverse momentum
        if printStuff:
            print("GenJet.P ", GenJet.P)
            print("GenJet.Particles ", GenJet.Particles)
            print("GenJet.NCharged ", GenJet.NCharged)

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
