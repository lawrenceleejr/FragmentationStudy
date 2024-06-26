#!/usr/bin/env python

import sys, os
import ROOT
import math
import numpy as np
import uproot4
from array import array
import csv

def savehist(hist, histname):
    """At the end of the function, there are no more references to `file`.
    The `TFile` object gets deleted, which in turn saves and closes
    the ROOT file."""
    myfile.WriteObject(hist, histname)


printStuff = False

try:
    input = raw_input
except:
    pass

if len(sys.argv) < 3:
    print(" Usage: ROC.py input_root_file results_name")
    sys.exit(1)

print("Beginning...")

if os.path.exists('/usr/local/share/delphes/delphes/libDelphes.so'):
    ROOT.gSystem.Load('/usr/local/share/delphes/delphes/libDelphes')
else:
    ROOT.gSystem.Load("libDelphes")

try:
    ROOT.gInterpreter.Declare('#include "classes/DelphesClasses.h"')
    ROOT.gInterpreter.Declare('#include "external/ExRootAnalysis/ExRootTreeReader.h"')
except:
    pass

inputFile = sys.argv[1]
namer = inputFile[:inputFile.index("_")]

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
histhighestID = ROOT.TH1F("highestID", "highestID; HighestID", 300, -50.0, 50.0)

# TH2F::TH2F(const char* name, const char* title, int nbinsx, double xlow, double xup, int nbinsy, double ylow,
# double yup) =>

histPartVsPT = ROOT.TH2F(
    "# of particles Vs pt", "Number of Particles Vs GenJet PT; GenJet PT; # of particles",
    100, 0.0, 500.0, 50, 0.0, 100.0)

histPartVsPTq = ROOT.TH2F(
    "# of particles Vs pt_q", "Number of Particles Vs GenJet PTq; GenJet PT; # of part\
icles",
    100, 0.0, 500.0, 50, 0.0, 100.0)

histPartVsPTg = ROOT.TH2F(
    "# of particles Vs pt_g", "Number of Particles Vs GenJet PTg; GenJet PT; # of part\
icles",
    100, 0.0, 500.0, 50, 0.0, 100.0)

# defining const for two different processes  
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


print("looping...")
 
for entry, event in enumerate(jetconst_refs[:]):
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
histPartVsPT.Draw("colz")
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPT.png")
c0.Clear()

c0.Update()
histPartVsPTq.SetContour(1000)
histPartVsPTq.Draw("colz")
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPTq.png")
c0.Clear()

c0.Update()
histPartVsPTg.SetContour(1000)
histPartVsPTg.Draw("colz")
c0.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_PartVsPTg.png")
c0.Clear()

c1 = ROOT.TCanvas("c1","SLice cutout of", 800,800 )

cutout = [ ["50-100-slice",50,100], ["100-150-slice",100,150], ["150-200-slice",150,200], ["200-250-slice",200,250] ]


for i, val in enumerate(cutout):
        #loops over cutout and use the array of arrays as variables to fill .ProjectionY
        pt_projy = histPartVsPT.ProjectionY("projectionY", histPartVsPT.GetXaxis().FindBin(val[1]), histPartVsPT.GetXaxis().FindBin(val[2]) )
        pt_projyg = histPartVsPTg.ProjectionY("GluonProjectionY", histPartVsPTg.GetXaxis().FindBin(val[1]),histPartVsPTg.GetXaxis().FindBin(val[2]) )
        pt_projyq = histPartVsPTq.ProjectionY("QuarkProjectionY", histPartVsPTq.GetXaxis().FindBin(val[1]), histPartVsPTq.GetXaxis().FindBin(val[2]) )
        pt_projy.Scale(1.0/pt_projy.Integral(0,pt_projy.GetNbinsX()+1)  )
        pt_projyg.Scale(1.0/pt_projyg.Integral() )
        pt_projyq.Scale(1.0/pt_projyq.Integral() )
        #makes empty array so it can soon be filled
        x = [None] * pt_projyq.GetNbinsX()
        y = [None] * pt_projyg.GetNbinsX()
        #opens a empty .csv file
        OPENcsv =  open("../FragmentationStudy/output_csv/" + namer + "_" + val[0] + "_" +sys.argv[2] + ".csv", "w" , newline="") 
        WRITERcsv = csv.writer(OPENcsv)
        #loops over the pt_projq&g array to fill into x&y
        for j in range(pt_projyg.GetNbinsX()):
            #print("q", pt_projyq.Integral(j,pt_projyq.GetNbinsX()+1) )
            #print("g", pt_projyg.Integral(j,pt_projyg.GetNbinsX()+1) )
            x[j] =  pt_projyq.Integral(j,pt_projyq.GetNbinsX()+1)
            y[j] =  pt_projyg.Integral(j,pt_projyg.GetNbinsX()+1)
        WRITERcsv.writerow( x )
        WRITERcsv.writerow( y )
        OPENcsv.close()
        #plots histograms
        pt_projy.SetLineColor(1)
        pt_projyg.SetLineColor(2)
        pt_projyq.SetLineColor(3)
        pt_projyq.GetMaximum(pt_projy.GetMaximum()*2)
        pt_projyq.Draw("hist 1")
        pt_projyg.Draw("hist 1 same")
        pt_projy.Draw("hist 1 same")
        pt_projyq.SetTitle("Number of Particles Vs GenJet PT slice " + "[" +str(val[1]) + "," +str(val[2]) + "]") 
        c1.BuildLegend()
        c1.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_"+val[0]+"_YprojectionALL.png")
        c1.Clear()

c1.Update()
histhighestID.Draw()
c1.Print("../FragmentationStudy/plots/"+sys.argv[2]+"_highestID.png")
c1.Clear()

# Save resulting histograms to .root file
savehist(histPartVsPT, "PartVsPT")
savehist(histPartVsPTg, "PartVsPTq")
savehist(histPartVsPTq, "PartVsPTg")

savehist(pt_projy, "PartVsPTprojY")
savehist(pt_projyg, "PartVsPTprojYg")
savehist(pt_projyq, "PartVsPTprojYq")

myfile.Write()

print("Done!")
