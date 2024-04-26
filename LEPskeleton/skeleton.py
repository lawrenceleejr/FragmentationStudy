import ROOT
import uproot4
import sys
import awkward as ak
import fastjet
import vector
import numpy as np


def savehist(hist, histname):
    """At the end of the function, there are no more references to `file`.
    The `TFile` object gets deleted, which in turn saves and closes
    the ROOT file."""
    myfile.WriteObject(hist, histname)

def nXX_graph(jet_constituent_momenta,jet_energy):
     jet_constituent_momenta = sorted(jet_constituent_momenta, key=lambda x: x.E(), reverse=True)
     runningp4sum = ROOT.TLorentzVector()

     tmpGraph = ROOT.TGraph(len(jet_constituent_momenta))

     for i, tmpconst in enumerate(jet_constituent_momenta):
            runningp4sum += tmpconst
            try:
                index = math.floor(jet_energy / 50)
            except:
                pass

            tmpGraph.SetPoint(i, runningp4sum.E() / jet_energy, i)
     return tmpGraph

########################################
#File Input
########################################
try:
    input = raw_input
except:
    pass

if len(sys.argv) < 3:
    print(" Usage: skeleton.py input_root_file output_tag")
    sys.exit(1)


for item in sys.argv[1].split("/"):
    if item.find(".root") != -1:
        output = item.split(".")[0]

myfile = ROOT.TFile.Open("/wumbodrive/data/LEP/LEP2/output/"+output+"_"+sys.argv[2]+"_histograms.root", "RECREATE")

inputFile = sys.argv[1]

f = uproot4.open(inputFile)
tree = f["t"]
branches = tree.arrays()

px_branch = branches["px"]
py_branch = branches["py"]
pz_branch = branches["pz"]
E_branch = branches["Energy"]
nParticles = branches["nParticle"]
pt_branch = branches["pt"]
eta_branch = branches["eta"]
phi_branch = branches["phi"]
M_branch = branches["mass"]
pwflag = branches["pwflag"]
STheta = branches["STheta"]
passesWW = branches["passesWW"]
passesISR = branches["passesISR"]
passesMissP = branches["passesMissP"]


num_events = len(nParticles) # get number of events

########################################
#Declaring Histograms
########################################
tri_h_n50_p = ROOT.TH2D(f"th_n50_p","; Leading Trijet P; n50",50,0,175,10,0,10)
tri_h_n80_p = ROOT.TH2D(f"th_n80_p","; Leading Trijet P; n80",50,0,175,20,0,20)
tri_h_n90_p = ROOT.TH2D(f"th_n90_p","; Leading Trijet P; n90",50,0,175,30,0,30)
tri_h_n95_p = ROOT.TH2D(f"th_n95_p","; Leading Trijet P; n95",50,0,175,30,0,30)
tri_h_n99_p = ROOT.TH2D(f"th_n99_p","; Leading Trijet P; n99",50,0,175,30,0,30)
di_h_n50_p = ROOT.TH2D(f"dh_n50_p","; Jet P; n50",50,0,175,10,0,10)
di_h_n80_p = ROOT.TH2D(f"dh_n80_p","; Jet P; n80",50,0,175,20,0,20)
di_h_n90_p = ROOT.TH2D(f"dh_n90_p","; Jet P; n90",50,0,175,30,0,30)
di_h_n95_p = ROOT.TH2D(f"dh_n95_p","; Jet P; n95",50,0,175,30,0,30)
di_h_n99_p = ROOT.TH2D(f"dh_n99_p","; Jet P; n99",50,0,175,30,0,30)

isolatedPhotons = ROOT.TH1F("isolatedPhotons","Number of Isolated Photons",30,0,30)
isolatedPhotonEnergyhist = ROOT.TH1F("isolatedPhotonEnergyhist", "Total Energy of Isolated Photons", 100, 0, 200)
numClusters = ROOT.TH1F("numClusters", "Total Number of Clusters",50,0,50)

tevent_selection = ROOT.TH1F("trijet_event_selection","Trijet Cut Flow Histogram", 7,0,7)
devent_selection = ROOT.TH1F("dijet_event_selection","Dijet Cut Flow Histogram", 8,0,8)

tE = ROOT.TH1F("trijet_energy","Leading Trijet Energy",100,0,200)
dE = ROOT.TH1F("dijet_energy","Dijet Energy",100,0,200)
tPions = ROOT.TH1F("trijet_pions","Number of Pions in Leading Trijet",30,0,30)
dPions = ROOT.TH1F("dijet_pions","Number of Pions in dijet",30,0,30)
tInvMass = ROOT.TH1F("tInvMass","Invariant Mass of leading three jets",100,0,200)
dInvMass = ROOT.TH1F("dInvMass","Invariant Mass of dijet system",100,0,200)


########################################
#Fastjet Setup
########################################
# https://fastjet.fr/repo/doxygen-3.4.1/classfastjet_1_1JetDefinition.html
jetdef = fastjet.JetDefinition(fastjet.antikt_algorithm, 0.4)
vector.register_awkward()


print("There are " + str(num_events) + " events")
for i in range(num_events):
    if (i % 250 == 0):
        print(str(int(i/num_events *100)) + "% done")

    tevent_selection.Fill(0)
    devent_selection.Fill(0)
    ########################################
    #Pre-clustering Event Cuts
    ########################################

    if (abs(np.cos(STheta[i])) > 0.82):
        continue
    tevent_selection.Fill(1)
    devent_selection.Fill(1)

    if (not passesWW[i]):
        continue
    tevent_selection.Fill(2)
    devent_selection.Fill(2)
    
    if (not passesMissP[i]):
        continue
    tevent_selection.Fill(3)
    devent_selection.Fill(3)

    
    ########################################
    #Jet Clustering
    ########################################

    #Looping over all particles in the event and putting them in an array in the format:
    #[{"px" : __, "py" : __, "pz" : __, "E" : __}, {...}, ... ]
    #This is the format that FastJet wants them in 
    temp = []
    for k in range(nParticles[i]):
        temp_part = {}
        temp_part["px"] = px_branch[i][k]
        temp_part["py"] = py_branch[i][k]
        temp_part["pz"] = pz_branch[i][k]
        temp_part["E"] = np.sqrt(M_branch[i][k]**2 + px_branch[i][k]**2 + py_branch[i][k]**2 + pz_branch[i][k]**2)
        temp.append(temp_part)
    array1 = ak.Array(temp)
    cluster = fastjet.ClusterSequence(array1, jetdef)


    ########################################
    #Pre-clustering Event Cuts
    ########################################
    
    #Have to pass certain criteria to find these events
    isTrijet = False
    isDijetGamma = False
    
    isolatedPhotonEnergy = 0
    isoP = 0
    numNonPhotonJets = 0

    jets = cluster.inclusive_jets()
    constituents = cluster.constituents()
    constituent_index = cluster.constituent_index()
    numClusters.Fill(len(jets))

    if(len(jets) < 2):
        continue
    tevent_selection.Fill(4)
    devent_selection.Fill(4)

    for cl,index in zip(constituents,cluster.constituent_index()):
        if (len(cl) == 1 and pwflag[i][index[0]] == 4):
            isolatedPhotonEnergy += np.sqrt(px_branch[i][index[0]]**2 + py_branch[i][index[0]]**2 + pz_branch[i][index[0]]**2) 
            isoP += 1
        else:
            numNonPhotonJets += 1
    isolatedPhotonEnergyhist.Fill(isolatedPhotonEnergy)
    isolatedPhotons.Fill(isoP)

    
    if (isolatedPhotonEnergy < 5):
        tevent_selection.Fill(5)
        if (numNonPhotonJets >=3):
            tevent_selection.Fill(6)
            isTrijet = True
            energy_indexing = np.argsort(jets[:]["E"])
        
            tj1 = energy_indexing[-1]
            tj2 = energy_indexing[-2]
            tj3 = energy_indexing[-2]
            tmp_j1 = ROOT.TLorentzVector(
                    jets[tj1]["px"],
                    jets[tj1]["pz"],
                    jets[tj1]["py"],
                    jets[tj1]["E"],
            )
            tmp_j2 = ROOT.TLorentzVector(
                    jets[tj2]["px"],
                    jets[tj2]["pz"],
                    jets[tj2]["py"],
                    jets[tj2]["E"],
            )
            tmp_j3 = ROOT.TLorentzVector(
                    jets[tj3]["px"],
                    jets[tj3]["pz"],
                    jets[tj3]["py"],
                    jets[tj3]["E"],
            )
            tInvMass.Fill((tmp_j1 + tmp_j2 + tmp_j3).M())
    else:
        #I'm using the fact that python doesn't give
        #if/else blocks their own scope to reuse these variables
        #later in the dijet code without refinding these things.
        #Gross.
        energy_indexing = np.argsort(jets[:]["E"])
        
        dj1 = energy_indexing[-1]
        dj2 = energy_indexing[-2]
        tmp_j1 = ROOT.TLorentzVector(
                    jets[dj1]["px"],
                    jets[dj1]["pz"],
                    jets[dj1]["py"],
                    jets[dj1]["E"],
            )
        tmp_j2 = ROOT.TLorentzVector(
                    jets[dj2]["px"],
                    jets[dj2]["pz"],
                    jets[dj2]["py"],
                    jets[dj2]["E"],
            )
        inv_mass = (tmp_j1 + tmp_j2).M()
        dInvMass.Fill(inv_mass)
        if (inv_mass > 86.188):
            devent_selection.Fill(5)
            if (inv_mass < 96.188):
                devent_selection.Fill(6)
                if (isolatedPhotonEnergy >= 5):
                    devent_selection.Fill(7)
                    isDijetGamma = True

    ########################################
    #Analysis Code
    ########################################

    if(isTrijet):
        
        highest_energy_index = np.argmax(cluster.inclusive_jets()[:]["E"])
        
        #for jet, cont, index in zip(cluster.inclusive_jets(), cluster.constituents(),cluster.constituent_index()):
        jet = jets[highest_energy_index]
        cont = constituents[highest_energy_index]
        index = constituent_index[highest_energy_index]
        arr = sorted(cont, key=lambda x: x['E'], reverse=True)

        listOfConstituentMomenta = []
        for tmpconst in range(len(cont)):
            tmp_p4 = ROOT.TLorentzVector(
                cont[tmpconst]["px"],
                cont[tmpconst]["py"],
                cont[tmpconst]["pz"],
                cont[tmpconst]["E"],
            )
            listOfConstituentMomenta.append(tmp_p4)


        jetp4 = ROOT.TLorentzVector()
        jetp4.SetPxPyPzE(
             jet['px'],
             jet['py'],
             jet['pz'],
             jet['E']
         )

        tmpGraph = nXX_graph(listOfConstituentMomenta,jet["E"])

        tri_h_n50_p.Fill(jetp4.P(), tmpGraph.Eval(0.5))
        tri_h_n80_p.Fill(jetp4.P(), tmpGraph.Eval(0.8))
        tri_h_n90_p.Fill(jetp4.P(), tmpGraph.Eval(0.9))
        tri_h_n95_p.Fill(jetp4.P(), tmpGraph.Eval(0.95))
        tri_h_n99_p.Fill(jetp4.P(), tmpGraph.Eval(0.99))
        
        tE.Fill(jet["E"])

        nPi = 0
        for ind in index:
            if (M_branch[i][ind] > 0.134 and M_branch[i][ind] < 0.144):
                nPi += 1
        tPions.Fill(nPi)

    elif(isDijetGamma):
        jet = jets[dj1]
        cont = constituents[dj1]
        index = constituent_index[dj1]
        listOfConstituentMomenta = []
        for tmpconst in range(len(cont)):
            tmp_p4 = ROOT.TLorentzVector(
                cont[tmpconst]["px"],
                cont[tmpconst]["py"],
                cont[tmpconst]["pz"],
                cont[tmpconst]["E"],
            )
            listOfConstituentMomenta.append(tmp_p4)


        jetp4 = ROOT.TLorentzVector()
        jetp4.SetPxPyPzE(
             jet['px'],
             jet['py'],
             jet['pz'],
             jet['E']
         )

        tmpGraph = nXX_graph(listOfConstituentMomenta,jet["E"])
        di_h_n50_p.Fill(jetp4.P(), tmpGraph.Eval(0.5))
        di_h_n80_p.Fill(jetp4.P(), tmpGraph.Eval(0.8))
        di_h_n90_p.Fill(jetp4.P(), tmpGraph.Eval(0.9))
        di_h_n95_p.Fill(jetp4.P(), tmpGraph.Eval(0.95))
        di_h_n99_p.Fill(jetp4.P(), tmpGraph.Eval(0.99))

        dE.Fill(jet["E"])

        nPi = 0
        for ind in index:
            if (M_branch[i][ind] > 0.134 and M_branch[i][ind] < 0.144):
                nPi += 1
        dPions.Fill(nPi)

        jet = jets[dj2]
        cont = constituents[dj2]
        index = constituent_index[dj2]
        listOfConstituentMomenta = []
        for tmpconst in range(len(cont)):
            tmp_p4 = ROOT.TLorentzVector(
                cont[tmpconst]["px"],
                cont[tmpconst]["py"],
                cont[tmpconst]["pz"],
                cont[tmpconst]["E"],
            )
            listOfConstituentMomenta.append(tmp_p4)


        jetp4 = ROOT.TLorentzVector()
        jetp4.SetPxPyPzE(
             jet['px'],
             jet['py'],
             jet['pz'],
             jet['E']
         )

        tmpGraph = nXX_graph(listOfConstituentMomenta,jet["E"])
        di_h_n50_p.Fill(jetp4.P(), tmpGraph.Eval(0.5))
        di_h_n80_p.Fill(jetp4.P(), tmpGraph.Eval(0.8))
        di_h_n90_p.Fill(jetp4.P(), tmpGraph.Eval(0.9))
        di_h_n95_p.Fill(jetp4.P(), tmpGraph.Eval(0.95))
        di_h_n99_p.Fill(jetp4.P(), tmpGraph.Eval(0.99))

        dE.Fill(jet["E"])

        nPi = 0
        for ind in index:
            if (M_branch[i][ind] > 0.134 and M_branch[i][ind] < 0.144):
                nPi += 1
        dPions.Fill(nPi)

    else:
        a = 0


print("Finished analysis. Saving histograms...")

for thing in [tri_h_n50_p, tri_h_n80_p, tri_h_n90_p, tri_h_n95_p, tri_h_n99_p,di_h_n50_p, di_h_n80_p, di_h_n90_p, di_h_n95_p, di_h_n99_p]:
    #thing.Smooth()
    thing.SetFillColor(ROOT.kRed)
    thing.SetFillStyle(2)
    thing.Write()
    thing.ProfileX().Write()
    thing.QuantilesX(0.5).Write()
    thing.QuantilesX(0.25).Write()
    thing.QuantilesX(0.75).Write()

savehist(tri_h_n50_p, "tri_h_n50_p")
savehist(tri_h_n80_p, "tri_h_n80_p")
savehist(tri_h_n90_p, "tri_h_n90_p")
savehist(tri_h_n95_p, "tri_h_n95_p")
savehist(tri_h_n99_p, "tri_h_n99_p")
savehist(di_h_n50_p, "di_h_n50_p")
savehist(di_h_n80_p, "di_h_n80_p")
savehist(di_h_n90_p, "di_h_n90_p")
savehist(di_h_n95_p, "di_h_n95_p")
savehist(di_h_n99_p, "di_h_n99_p")


savehist(isolatedPhotons,"isolated_photons")
savehist(isolatedPhotonEnergyhist,"isolatedPhotonEnergy")
savehist(numClusters,"numClusters")

savehist(tevent_selection,"trijet_event_selection")
savehist(devent_selection,"dijet_event_selection")

savehist(tE,"trijet_energy")
savehist(dE,"dijet_energy")
savehist(tPions,"trijet_pions")
savehist(dPions,"dijet_pions")
savehist(tInvMass,"tInvMass")
savehist(dInvMass,"dInvMass")
