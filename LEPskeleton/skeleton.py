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

h_n50_p = ROOT.TH2D(f"h_n50_p","; Jet P; n50",25,0,125,100,0,10)
h_n80_p = ROOT.TH2D(f"h_n80_p","; Jet P; n80",25,0,125,100,0,20)
h_n90_p = ROOT.TH2D(f"h_n90_p","; Jet P; n90",25,0,125,100,0,30)
h_n95_p = ROOT.TH2D(f"h_n95_p","; Jet P; n95",25,0,125,100,0,30)
h_n99_p = ROOT.TH2D(f"h_n99_p","; Jet P; n99",25,0,125,100,0,30)



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

num_events = len(nParticles) # get number of events


# https://fastjet.fr/repo/doxygen-3.4.1/classfastjet_1_1JetDefinition.html
jetdef = fastjet.JetDefinition(fastjet.antikt_algorithm, 0.4)
vector.register_awkward()


printStuff = False
print("There are " + str(num_events))
for i in range(num_events):
    if i > 200:
        break
    if (i % 250 == 0):
        print(str(int(i/num_events *100)) + "% done")
    
    ########################################
    #Event Cuts
    ########################################

    #TODO : implement Anthony's cuts


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
    #Analysis Code
    ########################################
    isTrijet = True
    isDijetGamma = False

    if(isTrijet):
         for jet, cont in zip(cluster.inclusive_jets(), cluster.constituents()):
             arr = sorted(cont, key=lambda x: x['E'], reverse=True)

             listOfConstituentMomenta = []
             for tmpconst in range(len(cont)):
            # print("tmpconst: ", tmpconst)
            # print("px_refs[entry][tmpconst]: ", px_refs[entry][tmpconst])
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

             h_n50_p.Fill(jetp4.P(), tmpGraph.Eval(0.5))
             h_n80_p.Fill(jetp4.P(), tmpGraph.Eval(0.8))
             h_n90_p.Fill(jetp4.P(), tmpGraph.Eval(0.9))
             h_n95_p.Fill(jetp4.P(), tmpGraph.Eval(0.95))
             h_n99_p.Fill(jetp4.P(), tmpGraph.Eval(0.99))
     elif(isDijetGamma):
         #TODO
     else
         #TODO

for thing in [h_n50_p, h_n80_p, h_n90_p, h_n95_p, h_n99_p]:
    thing.Smooth()
    thing.SetFillColor(ROOT.kRed)
    thing.SetFillStyle(2)
    thing.Write()
    thing.ProfileX().Write()
    thing.QuantilesX(0.5).Write()
    thing.QuantilesX(0.25).Write()
    thing.QuantilesX(0.75).Write()

savehist(h_n50_p, "h_n50_p")
savehist(h_n80_p, "h_n80_p")
savehist(h_n90_p, "h_n90_p")
savehist(h_n95_p, "h_n95_p")
savehist(h_n99_p, "h_n99_p")

