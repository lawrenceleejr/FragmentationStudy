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
partonIDq = [1, 2, 3, -1, -2, -3, ]
partonIDg = [9, 21, -9, -21]
partonID = [1, 2, 3, 4, 5, 6, 7, 8, 9, 21, -1, -2, -3, -4, -5, -6, -7, -8, -9, -21 ]


deltaRMax = 0.4

# TH1F::TH1F(const char* name, const char* title, int nbinsx, double xlow, double xup) =>
histhighestID = ROOT.TH1F("highestID", "highestID; HighestID", 300, -500.0, 500.0)

# TH2F::TH2F(const char* name, const char* title, int nbinsx, double xlow, double xup, int nbinsy, double ylow,
# double yup) =>

histPartVsPT = ROOT.TH2F(
    "# of particles Vs pt", "Number of Particles Vs GenJet PT; GenJet PT; # of particles",
    100, 0.0, 500.0, 50, 0.0, 50.0)

histPartVsPTq = ROOT.TH2F(
    "# of particles Vs pt", "Number of Particles Vs GenJet PTq; GenJet PT; # of part\
icles",
    100, 0.0, 500.0, 50, 0.0, 50.0)

histPartVsPTg = ROOT.TH2F(
    "# of particles Vs pt", "Number of Particles Vs GenJet PTg; GenJet PT; # of part\
icles",
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
       
        histhighestID.Fill(highestEnergyPID) 
                    
          #if the initiating parton is a gluon, throws away the jet
        #if highestEnergyPID in partonIDq:
            #continue

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


        # Plot GenJet transverse momentum
        P = GenJet.PT * math.cosh(GenJet.Eta)
        histPartVsPT.Fill(GenJet.PT, GenJet.NCharged + GenJet.NNeutrals)


        # Print GenJet transverse momentum
        if printStuff:
            print("GenJet.P ", GenJet.P)
            print("GenJet.Particles ", GenJet.Particles)
            print("GenJet.NCharged ", GenJet.NCharged)
        
        if highestEnergyPID in partonIDq:
            histPartVsPTq.Fill(GenJet.PT, GenJet.NCharged + GenJet.NNeutrals)
        elif highestEnergyPID in partonIDg:
            histPartVsPTg.Fill(GenJet.PT, GenJet.NCharged + GenJet.NNeutrals)




# Show resulting histograms
c0 = ROOT.TCanvas()


c0.Update()
histPartVsPT.SetContour(1000)
pt_profx = histPartVsPT.ProfileX("profilex", 0, 100)
#pt_profx.Draw()
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPTprofx.png")
histPartVsPT.Draw("colz")
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPT.png")
c0.Clear()

c0.Update()
histPartVsPTq.SetContour(1000)
pt_profxq = histPartVsPTq.ProfileX("profilexq", 0, 100)
#pt_profxq.Draw()
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPTprofxq.png")
histPartVsPTq.Draw("colz")
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPTq.png")
c0.Clear()

c0.Update()
histPartVsPTg.SetContour(1000)
pt_profxg = histPartVsPTg.ProfileX("profilexg", 0, 100)
#pt_profxg.Draw()
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPTprofxg.png")
histPartVsPTg.Draw("colz")
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPTg.png")
c0.Clear()



c0.Update()
pt_projy = histPartVsPT.ProjectionY("projectionY", histPartVsPT.GetXaxis().FindBin(200), histPartVsPT.GetXaxis().FindBin(250) )
pt_projyg = histPartVsPTg.ProjectionY("projectionYg", histPartVsPTg.GetXaxis().FindBin(200), histPartVsPTg.GetXaxis().FindBin(250) )
pt_projyq = histPartVsPTq.ProjectionY("projectionYq", histPartVsPTq.GetXaxis().FindBin(200), histPartVsPTq.GetXaxis().FindBin(250) )
pt_projy.Scale(1/pt_projy)
pt_projyg.Scale(1)
pt_projy.SetLineColor(1)
pt_projyg.SetLineColor(2)
pt_projyq.SetLineColor(3)
pt_projy.Draw("hist 1")
pt_projyg.Draw("hist 1 same")
pt_projyq.Draw("hist 1 same")


c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_YprojectionALL.png")
c0.Clear()



c0.Update()
histhighestID.Draw()
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_highestID.png")
c0.Clear()

# Save resulting histograms to .root file
savehist(histPartVsPT, "PartVsPT")
savehist(histPartVsPT, "PartVsPTq")
savehist(histPartVsPT, "PartVsPTg")

savehist(pt_projy, "PartVsPTprojY")
savehist(pt_projyg, "PartVsPTprojYg")
savehist(pt_projyq, "PartVsPTprojYq")


print("Done!")
