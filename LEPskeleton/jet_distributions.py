import ROOT
import uproot4
import sys
import awkward as ak
import fastjet
import vector
import numpy as np

def savehist(hist, histname,myfile):
    myfile.WriteObject(hist, histname)

def jet_distributions(inFile,outTag):
    #myfile = ROOT.TFile.Open("/wumbodrive/data/LEP/LEP2/output/"+output+"_"+sys.argv[2]+"_event_distributions.root", "RECREATE")
    myfile = ROOT.TFile.Open(outTag+"_jet_distributions.root", "RECREATE")
    f = uproot4.open(inFile)
    tree = f["akR4ESchemeJetTree"]
    branches = tree.arrays()

    dijet_m = ROOT.TH1D("dijet_m","Leading Dijet Invariant Mass",120,0,120)

    nref = branches["nref"]
    jtpt = branches["jtpt"]
    jteta = branches["jteta"]
    jtphi = branches["jtphi"]
    jtN = branches["jtN"]
    jtm = branches["jtm"]
    jtNPW = branches["jtNPW"]
    jtptFracPW = branches["jtptFracPW"]

    for i in range(len(branches["jtpt"])):
        
        if (len(jtpt[i]) < 2):
            continue
        jet1 = ROOT.TLorentzVector()
        jet1.SetPtEtaPhiM(jtpt[i][0],jteta[i][0],jtphi[i][0],jtm[i][0])

        jet2 = ROOT.TLorentzVector()
        jet2.SetPtEtaPhiM(jtpt[i][1],jteta[i][1],jtphi[i][1],jtm[i][1])
        
        dijet_m.Fill((jet1 + jet2).M())

    savehist(dijet_m,"dijet_m",myfile)

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print(" Usage: event_distributions.py input_root_file output_tag")
		sys.exit(1)
	jet_distributions(sys.argv[1],sys.argv[2])
