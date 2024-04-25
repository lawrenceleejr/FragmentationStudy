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

    h3 = ROOT.TH1F("h3","passesWW" ,2,0,1)
    tree.Project("h3", "passesWW")
    savehist(h3,"passesWW",myfile)

    h31 = ROOT.TH1F("h31","passesISR" ,2,0,1)
    tree.Project("h31", "passesISR")
    savehist(h31,"passesISR",myfile)

    h4 = ROOT.TH1F("h4","STheta" ,50,-6.3,6.3)
    tree.Project("h4", "STheta")
    savehist(h4,"STheta",myfile)

    h5 = ROOT.TH1F("h5","cos(STheta)" ,50,-1,1)
    tree.Project("h5", "cos(STheta)")
    savehist(h5,"cosSTheta",myfile)

    h41 = ROOT.TH1F("h41","STheta_linearized" ,50,-6.3,6.3)
    tree.Project("h41", "STheta_linearized")
    savehist(h41,"STheta_linearized",myfile)

    h51 = ROOT.TH1F("h51","cos(STheta_linearized)" ,50,-1,1)
    tree.Project("h51", "cos(STheta_linearized)")
    savehist(h51,"cosSTheta_linearized",myfile)

    h6 = ROOT.TH1F("h6", "missP" ,100,-50,50)
    tree.Project("h6", "missP")
    savehist(h6,"missP",myfile)

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print(" Usage: event_distributions.py input_root_file output_tag")
		sys.exit(1)
	event_distributions(sys.argv[1],sys.argv[2])
