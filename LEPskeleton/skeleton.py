import ROOT
import uproot4
import sys, os
import awkward as ak
import fastjet
import vector


try:
    input = raw_input
except:
    pass

if len(sys.argv) < 2:
    print(" Usage: loop.py input_root_file")
    sys.exit(1)

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


jetdef = fastjet.JetDefinition(fastjet.antikt_algorithm, 0.4)
vector.register_awkward()

builder = ak.ArrayBuilder()
for i in range(len(nParticles)):
    #print(px_branch[i])
    for k in range(nParticles[i]):
        #print(E_branch[i])
        #array = {"px": px_branch[i][k], "py": py_branch[i][k], "pz": pz_branch[i][k], "E": E_branch[i]}
        #print(array)
        #array1.append(array)
        builder.begin_record()
        #builder.field("px").append(px_branch[i][k])
        #builder.field("py").append(py_branch[i][k])
        #builder.field("pz").append(pz_branch[i][k])
        #builder.field("E").append(E_branch[i])
        builder.field("pt").append(pt_branch[i][k])
        builder.field("eta").append(eta_branch[i][k])
        builder.field("phi").append(phi_branch[i][k])
        builder.field("M").append(M_branch[i][k])
        builder.end_record()
    array1 = builder.snapshot()
    #print(array1.type.show())
    array1 = ak.with_name(array1, "Momentum4D")
    #print(array1.type.show())

    cluster = fastjet.ClusterSequence(array1, jetdef)
    print(len(cluster.inclusive_jets()))
    #print(array1)



    #k = branch["nParticle"]
    #print(k)
    #for i in range(0, k):
        #print(i)
        #print(branch["px"][i])


    #for particle in branch["px"]:
        #print(particle)
    #if branch["RunNo"] == 42684:
        #print(branch)
        #i += 1
    break
#print(i)