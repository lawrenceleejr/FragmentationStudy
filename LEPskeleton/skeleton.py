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


try:
    input = raw_input
except:
    pass

if len(sys.argv) < 2:
    print(" Usage: skeleton.py input_root_file")
    sys.exit(1)

myfile = ROOT.TFile.Open("test.root", "RECREATE")

inputFile = sys.argv[1]

f = uproot4.open(inputFile)
tree = f["t"]
branches = tree.arrays()

px_branch = branches["px"]
py_branch = branches["py"]
pz_branch = branches["pz"]
#E_branch = branches["Energy"]
nParticles = branches["nParticle"]
num_events = len(nParticles) # get number of events

pt_branch = branches["pt"]
eta_branch = branches["eta"]
phi_branch = branches["phi"]
M_branch = branches["mass"]

# https://fastjet.fr/repo/doxygen-3.4.1/classfastjet_1_1JetDefinition.html
jetdef = fastjet.JetDefinition(fastjet.antikt_algorithm, 0.4)
vector.register_awkward()

builder = ak.ArrayBuilder() # Builds arrays of particles in an event

h_n50_p = ROOT.TH2D(f"h_n50_p","; Jet P; n50",25,0,125,100,0,10)
h_n80_p = ROOT.TH2D(f"h_n80_p","; Jet P; n80",25,0,125,100,0,20)
h_n90_p = ROOT.TH2D(f"h_n90_p","; Jet P; n90",25,0,125,100,0,30)
h_n95_p = ROOT.TH2D(f"h_n95_p","; Jet P; n95",25,0,125,100,0,30)
h_n99_p = ROOT.TH2D(f"h_n99_p","; Jet P; n99",25,0,125,100,0,30)

printStuff = False
for i in range(num_events):
    if i > 10000:
        break
    temp = []
    for k in range(nParticles[i]):
        temp_part = {}
        temp_part["px"] = px_branch[i][k]
        temp_part["py"] = py_branch[i][k]
        temp_part["pz"] = pz_branch[i][k]
        temp_part["E"] = np.sqrt(M_branch[i][k]**2 + px_branch[i][k]**2 + py_branch[i][k]**2 + pz_branch[i][k]**2)
        #print(temp_part)
        #builder.begin_record()
        #builder.field("pt").append(pt_branch[i][k])
        #builder.field("eta").append(eta_branch[i][k])
        #builder.field("phi").append(phi_branch[i][k])
        #builder.field("M").append(M_branch[i][k])
        #builder.end_record()
        temp.append(temp_part)
    array1 = ak.Array(temp)
    #array1 = builder.snapshot()
    #array1 = ak.with_name(array1, "Momentum4D")
    #array1 = ak.with_behavior(array1, vector.backends.awkward.behavior)

    cluster = fastjet.ClusterSequence(array1, jetdef)
    if printStuff:
        print(f"\nNumber of particles in event: ", nParticles[i])
        print(f"Number of jets in event: ", len(cluster.inclusive_jets())) # How many jets are there?
        print(f"Number of particles according to fastjet: ", cluster.n_particles())
        print(f"Unclustered constituents: ", cluster.unclustered_particles())
        print(f"Number of pseudojets: ", cluster.childless_pseudojets())
        print(f"Jet constituent_index: ", cluster.constituent_index())
        print(f"Jet constituents: ", cluster.constituents())
        print(f"Energy correlator of each exclusive jet: ", cluster.exclusive_jets_energy_correlator())
        print(f"Sum of all the energies in the event: ", cluster.Q())
        print(type(cluster))

    for jet, cont in zip(cluster.inclusive_jets(), cluster.constituents()):
        #print("\n")
        arr = sorted(cont, key=lambda x: x['E'], reverse=True)
        #for sub in arr:
            #print(sub)

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

        if len(listOfConstituentMomenta) == 1:
            continue

        jetp4 = ROOT.TLorentzVector()
        jetp4.SetPxPyPzE(
            jet['px'],
            jet['py'],
            jet['pz'],
            jet['E']
        )

        listOfConstituentMomenta = sorted(listOfConstituentMomenta, key=lambda x: x.E(), reverse=True)
        runningp4sum = ROOT.TLorentzVector()

        tmpGraph = ROOT.TGraph(len(arr))

        for i, tmpconst in enumerate(listOfConstituentMomenta):
            runningp4sum += tmpconst
            try:
                index = math.floor(jet['E'] / 50)
                #h_jetfrag[index*50].Fill(i,runningp4sum.E() / jet['E'] )
            except:
                pass

            tmpGraph.SetPoint(i, runningp4sum.E() / jet['E'], i)

        h_n50_p.Fill(jetp4.P(), tmpGraph.Eval(0.5))
        h_n80_p.Fill(jetp4.P(), tmpGraph.Eval(0.8))
        h_n90_p.Fill(jetp4.P(), tmpGraph.Eval(0.9))
        h_n95_p.Fill(jetp4.P(), tmpGraph.Eval(0.95))
        h_n99_p.Fill(jetp4.P(), tmpGraph.Eval(0.99))

    #break # Only doing one event right now, for testing

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

