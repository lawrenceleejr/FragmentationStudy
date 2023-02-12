#!/usr/bin/env python

import sys, os
import ROOT
import math
import numpy as np
import uproot4


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

if os.path.exists('/usr/local/share/delphes/delphes/libDelphes.so'):
    ROOT.gSystem.Load('/usr/local/share/delphes/delphes/libDelphes')
else:
    ROOT.gSystem.Load("libDelphes")

# ROOT.gSystem.Load("libDelphes")

try:
    ROOT.gInterpreter.Declare('#include "classes/DelphesClasses.h"')
    ROOT.gInterpreter.Declare('#include "external/ExRootAnalysis/ExRootTreeReader.h"')
except:
    pass

inputFile = sys.argv[1]

f = uproot4.open(inputFile)

# Create .root file to save histograms
myfile = ROOT.TFile.Open("../FragmentationStudy/root_files/violin_files/"+sys.argv[2]+"_histograms.root", "RECREATE")

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


jetconst_refs = f["Delphes/GenJet.Particles"].array(library="np")
jetpt_refs    = f["Delphes/GenJet.PT"].array(library="np")
jeteta_refs   = f["Delphes/GenJet.Eta"].array(library="np")
jetphi_refs   = f["Delphes/GenJet.Phi"].array(library="np")
jetm_refs     = f["Delphes/GenJet.Mass"].array(library="np")

pid_refs      = f["Delphes/Particle.PID"].array(library="np")
status_refs   = f["Delphes/Particle.Status"].array(library="np")
px_refs       = f["Delphes/Particle.Px"].array(library="np")
py_refs       = f["Delphes/Particle.Py"].array(library="np")
pz_refs       = f["Delphes/Particle.Pz"].array(library="np")
e_refs        = f["Delphes/Particle.E"].array(library="np")

h_n50_p = ROOT.TH2D(f"h_n50_p","; Jet P; n50",10,0,250,100,0,10)
h_n80_p = ROOT.TH2D(f"h_n80_p","; Jet P; n80",10,0,250,100,0,20)
h_n90_p = ROOT.TH2D(f"h_n90_p","; Jet P; n90",10,0,250,100,0,30)
h_n95_p = ROOT.TH2D(f"h_n95_p","; Jet P; n95",10,0,250,100,0,30)
h_n99_p = ROOT.TH2D(f"h_n99_p","; Jet P; n99",10,0,250,100,0,30)

# Loop over all events
for entry, event in enumerate(jetconst_refs[:]):
    # for entry in range(0, numberOfEntries):
    # Load selected branches with data from specified event
    treeReader.ReadEntry(entry)

    # If event contains at least 1 GenJet
    for ijet in range(branchGenJet.GetEntries()):
        GenJet = branchGenJet.At(ijet)
        highestEnergyParticle = 0
        particleIndex = -1
        highestEnergyPID = 0

        # Plot GenGet.M() and then throw away GenJets that have a low mass
        histGenJetM.Fill(GenJet.Mass)
        if GenJet.Mass < 0.01:
            continue

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

        # Find jet four vector
        jetp4 = ROOT.TLorentzVector()
        jetp4.SetPtEtaPhiM(
            jetpt_refs[entry][ijet],
            jeteta_refs[entry][ijet],
            jetphi_refs[entry][ijet],
            jetm_refs[entry][ijet],
        )

        # Throw away nonisolated jets
        isIsolated = True
        for jjet in range(branchGenJet.GetEntries()):
            if jjet == ijet:
                continue
            jjetp4 = ROOT.TLorentzVector()
            jjetp4.SetPtEtaPhiM(
                jetpt_refs[entry][jjet],
                jeteta_refs[entry][jjet],
                jetphi_refs[entry][jjet],
                jetm_refs[entry][jjet],
            )
            if jetp4.DeltaR(jjetp4) < 0.8:
                isIsolated = False
                break
        if not isIsolated:
            continue

        const_indices = [x - 1 for x in list(event[ijet])]

        listOfConstituentMomenta = []
        for tmpconst in const_indices:
            tmp_p4 = ROOT.TLorentzVector(
                px_refs[entry][tmpconst],
                py_refs[entry][tmpconst],
                pz_refs[entry][tmpconst],
                e_refs [entry][tmpconst],
                )
            listOfConstituentMomenta.append(tmp_p4)

        listOfConstituentMomenta = sorted(listOfConstituentMomenta, key=lambda x: x.E(), reverse=True)
        runningp4sum = ROOT.TLorentzVector()

        tmpGraph = ROOT.TGraph(len(listOfConstituentMomenta))

        for i, tmpconst in enumerate(listOfConstituentMomenta):
            runningp4sum += tmpconst
            try:
                index = math.floor(jetp4.E() / 50)
                # h_jetfrag[index*50].Fill(i,runningp4sum.E() / jetp4.E() )
            except:
                pass

            tmpGraph.SetPoint(i, runningp4sum.E() / jetp4.E(), i)

        h_n50_p.Fill(jetp4.P(), tmpGraph.Eval(0.5))
        h_n80_p.Fill(jetp4.P(), tmpGraph.Eval(0.8))
        h_n90_p.Fill(jetp4.P(), tmpGraph.Eval(0.9))
        h_n95_p.Fill(jetp4.P(), tmpGraph.Eval(0.95))
        h_n99_p.Fill(jetp4.P(), tmpGraph.Eval(0.99))


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

for thing in [h_n50_p, h_n80_p, h_n90_p, h_n95_p, h_n99_p]:
    thing.Smooth()
    thing.SetFillColor(ROOT.kRed)
    thing.SetFillStyle(2)
    thing.Write()
    thing.ProfileX().Write()
    thing.QuantilesX(0.5).Write()
    thing.QuantilesX(0.25).Write()
    thing.QuantilesX(0.75).Write()

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
h_n50_p.Draw()
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_h_n50_p.png")
c0.Clear()

c0.Update()
h_n80_p.Draw()
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_h_n80_p.png")
c0.Clear()

c0.Update()
h_n90_p.Draw()
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_h_n90_p.png")
c0.Clear()

c0.Update()
h_n95_p.Draw()
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_h_n95_p.png")
c0.Clear()

c0.Update()
h_n99_p.Draw()
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_h_n99_p.png")
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
savehist(h_n50_p, "h_n50_p")
savehist(h_n80_p, "h_n80_p")
savehist(h_n90_p, "h_n90_p")
savehist(h_n95_p, "h_n95_p")
savehist(h_n99_p, "h_n99_p")


print("Done!")
