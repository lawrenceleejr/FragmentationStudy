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
    print(" Usage: skeleton.py input_root_file")
    sys.exit(1)

inputFile = sys.argv[1]

f = uproot4.open(inputFile)
tree = f["t"]
branches = tree.arrays()

#px_branch = branches["px"]
#py_branch = branches["py"]
#pz_branch = branches["pz"]
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
for i in range(num_events):
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
    print(f"Number of particles in event: ", nParticles[i])
    print(f"Number of jets in event: ", len(cluster.inclusive_jets())) # How many jets are there?
    print(f"Number of particles according to fastjet: ", cluster.n_particles())
    print(f"Unclustered constituents: ", cluster.unclustered_particles())
    print(f"Jet constituent_index: ", cluster.constituent_index())
    print(f"Jet constituents: ", cluster.constituents())
    print(f"Sum of all the energies in the event: ", cluster.Q())
    print(type(cluster))
    break # Only doing one event right now, for testing

