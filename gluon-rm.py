#!/usr/bin/env python

import sys
import ROOT
import math
import numpy as np


printStuff = True

try:
    input = raw_input
except:
    pass

if len(sys.argv) < 3:
    print(" Usage: loop.py input_root_file results_name")
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

# Loop over all events
# numberOfEntries
partonID = [1, 2, 3, 4, 5, 6, 7, 8, 9, 21, -1, -2, -3, -4, -5, -6, -7, -8, -9, -21]
deltaRMax = 0.4
# Four momentum vector
px, py, pz, E = 0, 0, 0, 0

# Book histograms
# TH1F::TH1F(const char* name, const char* title, int nbinsx, double xlow, double xup) =>
histStatusCode = ROOT.TH1F("Status_Code", "Status Code; Status Code; #", 100, 0.0, 20.0)
histDeltaR = ROOT.TH1F("Delta_R", "Delta R; Delta R; #", 100, 0.0, deltaRMax)
# TH2F::TH2F(const char* name, const char* title, int nbinsx, double xlow, double xup, int nbinsy, double ylow,
# double yup) =>
histDeltaRVsRatio = ROOT.TH2F(
    "Delta R Vs E/jetE", "Delta R Vs E/jetE; E/JetE; Delta R",
    100, 0.0, 10.0, 100, 0.0, deltaRMax)

for entry in range(0, 100):
    # Load selected branches with data from specified event
    treeReader.ReadEntry(entry)

    # If event contains at least 1 GenJet
    for ijet in range(branchGenJet.GetEntries()):
        GenJet = branchGenJet.At(ijet)
        highestEnergyParticle = 0
        jetEnergy = 0
        particleIndex = -1
        # PID = 0
        highestEnergyPID = 0
        particleStatus = -1
        # particle_dict = GenJet.Particles
        highestDeltaR = 0
        # Not required
        # for zparticle in range(GenJet.Particles.GetEntries()):
        # Particle = particle_dict[zparticle]
        # jetEnergy += Particle.E
        # Required
        for iparticle in range(branchParticle.GetEntries()):
            Particle = branchParticle.At(iparticle)
            # PID = Particle.PID
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
                    particleStatus = Particle.Status
                    highestDeltaR = delta_R
                    histStatusCode.Fill(particleStatus)
        histDeltaR.Fill(highestDeltaR)
        histDeltaRVsRatio.Fill(highestEnergyParticle/jetEnergy, highestDeltaR)

        if highestEnergyPID == 21 and printStuff is True:
            print(
                "Event: %d, Jet: %d, particleIndex: %d, highestEnergy: %f, jetEnergy: %f, PID: %d" % (
                entry, ijet, particleIndex, highestEnergyParticle, jetEnergy, highestEnergyPID))

c0 = ROOT.TCanvas()
c0.Update()
histStatusCode.Draw()
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_StatusCode.png")
c0.Clear()

c0.Update()
histDeltaR.Draw()
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_DeltaR.png")
c0.Clear()

c0.Update()
histDeltaRVsRatio.SetContour(1000)
histDeltaRVsRatio.Draw("colz")
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_DeltaRVsRatio.png")
c0.Clear()

print("Done!")

