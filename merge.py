#!/usr/bin/env python

import sys
import ROOT
import math
import numpy as np
# import uproot


def closeAtDestruct(hist):
   myFile = ROOT.TFile.Open("file.root", "RECREATE")
   myFile.WriteObject(hist, "MyHist")
   # At the end of the function, there are no more references to `file`.
   # The `TFile` object gets deleted, which in turn saves and closes
   # the ROOT file.


try:
    input = raw_input
except:
    pass

if len(sys.argv) < 3:
    print(" Usage: merge.py eeToZgamma_file eeToZgluon_file")
    sys.exit(1)

print("Beginning...")
ROOT.gSystem.Load("libDelphes")

try:
    ROOT.gInterpreter.Declare('#include "classes/DelphesClasses.h"')
    ROOT.gInterpreter.Declare('#include "external/ExRootAnalysis/ExRootTreeReader.h"')
except:
    pass

inputFile = sys.argv[1]

# Open .root file to use histograms
# Path starts in Delphes directory
eeToZgamma_file = ROOT.TFile.Open("../FragmentationStudy/root_files/"+sys.argv[1]+"_histograms.root", "READ")
eeToZgluon_file = ROOT.TFile.Open("../FragmentationStudy/root_files/"+sys.argv[2]+"_histograms.root", "READ")

# Herwig test
herwig_file = ROOT.TFile.Open("../FragmentationStudy/root_files/herwig_test_histograms.root", "READ")
herwig_profx = herwig_file.PartVsPprofx
herwig_profx.SetName("Herwig")
# herwig_profx.SetStats(0)
herwig_profx.SetLineColor(ROOT.kGreen)

eeToZgamma_profx = eeToZgamma_file.PartVsPprofx
eeToZgluon_profx = eeToZgluon_file.PartVsPprofx

eeToZgamma_profx.SetName("ee->Z+gamma")
eeToZgluon_profx.SetName("ee->Z+gluon")

# Places both plots onto one canvas
c0 = ROOT.TCanvas()
c0.Update()
st0 = eeToZgamma_profx.GetListOfFunctions().FindObject("stats")
st0.SetY1NDC(0.50)
st0.SetY2NDC(0.30)
st0.SetLineColor(ROOT.kBlue)
ROOT.gPad.Update()
st1 = eeToZgluon_profx.GetListOfFunctions().FindObject("stats")
st1.SetY1NDC(0.30)
st1.SetY2NDC(0.10)
st1.SetLineColor(ROOT.kRed)
ROOT.gPad.Update()

eeToZgamma_profx.Draw()
eeToZgluon_profx.SetLineColor(ROOT.kRed)
eeToZgluon_profx.Draw("sames")
herwig_profx.Draw("sames")
c0.Print("../merge.png")
c0.Clear()

# Uproot stuff
# eeToZgamma_file = uproot.open("../FragmentationStudy/root_files/"+sys.argv[1]+"_histograms.root")
# eeToZgluon_file = uproot.open("../FragmentationStudy/root_files/"+sys.argv[2]+"_histograms.root")

print("Done!")
