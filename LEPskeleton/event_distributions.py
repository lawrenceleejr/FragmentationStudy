import ROOT
import uproot4
import sys
import awkward as ak
import fastjet
import vector
import numpy as np

def savehist(hist, histname,myfile):
    myfile.WriteObject(hist, histname)

def event_distributions(inFile,outTag):
    #myfile = ROOT.TFile.Open("/wumbodrive/data/LEP/LEP2/output/"+output+"_"+sys.argv[2]+"_event_distributions.root", "RECREATE")
    myfile = ROOT.TFile.Open(outTag+"_event_distributions.root", "RECREATE")
    f = ROOT.TFile.Open(inFile,"READ")
    tree = f.Get("t")

    h1 = ROOT.TH1F("h1","mass" ,100 ,0 , 0.400)
    tree.Project("h1", "mass")
    savehist(h1,"mass",myfile)
    
    h2 = ROOT.TH1F("h2","mass" ,100 ,0 , 0.400)
    tree.Project("h2", "mass;pwflag==4","pwflag==4")
    savehist(h2,"mass_photons",myfile)

    h3 = ROOT.TH1F("h3","passesWW" ,5,-1,5)
    tree.Project("h3", "passesWW")
    savehist(h3,"passesWW",myfile)


if __name__ == "__main__":
	if len(sys.argv) < 3:
		print(" Usage: event_distributions.py input_root_file output_tag")
		sys.exit(1)
	event_distributions(sys.argv[1],sys.argv[2])
