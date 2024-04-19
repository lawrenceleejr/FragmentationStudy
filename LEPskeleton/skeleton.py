import ROOT
import uproot4
import sys
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
    for k in range(nParticles[i]):
        builder.begin_record()
        builder.field("pt").append(pt_branch[i][k])
        builder.field("eta").append(eta_branch[i][k])
        builder.field("phi").append(phi_branch[i][k])
        builder.field("M").append(M_branch[i][k])
        builder.end_record()
    array1 = builder.snapshot()
    array1 = ak.with_name(array1, "Momentum4D")

    cluster = fastjet.ClusterSequence(array1, jetdef)
    print(len(cluster.inclusive_jets()))
    break

