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


def nXX_graph(jet_constituent_momenta, jet_energy):
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
# File Input
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

myfile = ROOT.TFile.Open(
    "/wumbodrive/data/LEP/LEP2/output/" + output + "_" + sys.argv[2] + "_histograms.root", "RECREATE")

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

num_events = len(nParticles)  # get number of events

########################################
# Declaring Histograms
########################################
tri_h_n50_p = ROOT.TH2D(f"th_n50_p", "; Leading Trijet P; n50", 50, 0, 175, 10, 0, 10)
tri_h_n80_p = ROOT.TH2D(f"th_n80_p", "; Leading Trijet P; n80", 50, 0, 175, 20, 0, 20)
tri_h_n90_p = ROOT.TH2D(f"th_n90_p", "; Leading Trijet P; n90", 50, 0, 175, 30, 0, 30)
tri_h_n95_p = ROOT.TH2D(f"th_n95_p", "; Leading Trijet P; n95", 50, 0, 175, 30, 0, 30)
tri_h_n99_p = ROOT.TH2D(f"th_n99_p", "; Leading Trijet P; n99", 50, 0, 175, 30, 0, 30)
di_h_n50_p = ROOT.TH2D(f"dh_n50_p", "; Jet P; n50", 50, 0, 175, 10, 0, 10)
di_h_n80_p = ROOT.TH2D(f"dh_n80_p", "; Jet P; n80", 50, 0, 175, 20, 0, 20)
di_h_n90_p = ROOT.TH2D(f"dh_n90_p", "; Jet P; n90", 50, 0, 175, 30, 0, 30)
di_h_n95_p = ROOT.TH2D(f"dh_n95_p", "; Jet P; n95", 50, 0, 175, 30, 0, 30)
di_h_n99_p = ROOT.TH2D(f"dh_n99_p", "; Jet P; n99", 50, 0, 175, 30, 0, 30)

tj1_v_E = ROOT.TH2D("tj1_v_E", "Trijet 1 v E", 50, 0, 175, 115, 85, 250)
tj2_v_E = ROOT.TH2D("tj2_v_E", "Trijet 2 v E", 50, 0, 175, 115, 85, 250)
tj3_v_E = ROOT.TH2D("tj3_v_E", "Trijet 3 v E", 50, 0, 175, 115, 85, 250)

highELeptonClusters = ROOT.TH1F("numHighELeptonClusters", "Number of clusters with a lepton E > 50% total E", 10, 0, 10)

isolatedPhotons = ROOT.TH1F("isolatedPhotons", "Number of Isolated Photons", 30, 0, 30)
isolatedPhotonEnergyhist = ROOT.TH1F("isolatedPhotonEnergyhist", "Total Energy of Isolated Photons", 100, 0, 200)
numClusters = ROOT.TH1F("numClusters", "Total Number of Clusters", 50, 0, 50)
numUnClustered = ROOT.TH1F("numUnClustered", "Total Number of unclustered particles", 50, 0, 100)
dijet_p_event_energy = ROOT.TH1F("dijet_p_event_energy", "Energy in the qqgamma Events", 50, 0, 225)

tevent_selection = ROOT.TH1F("trijet_event_selection", "Trijet Cut Flow Histogram", 7, 0, 7)
devent_selection = ROOT.TH1F("dijet_event_selection", "Dijet Cut Flow Histogram", 8, 0, 8)

tE = ROOT.TH1F("trijet_energy", "Leading Trijet Energy", 100, 0, 200)
dE = ROOT.TH1F("dijet_energy", "Dijet Energy", 100, 0, 200)
tPions = ROOT.TH1F("trijet_pions", "Number of Pions in Leading Trijet", 30, 0, 30)
dPions = ROOT.TH1F("dijet_pions", "Number of Pions in dijet", 30, 0, 30)
tInvMass = ROOT.TH1F("tInvMass", "Invariant Mass of leading three jets", 100, 0, 200)
dInvMass = ROOT.TH1F("dInvMass", "Invariant Mass of dijet system", 100, 0, 200)
lInvMass = ROOT.TH1F("lInvMass", "Invariant Mass of dijet in every event system", 100, 0, 200)
tlInvMass = ROOT.TH1F("tlInvMass", "Invariant Mass of trijet in every event system", 100, 0, 200)

E_hist = ROOT.TH1D("E_hist", "Energy histogram", 100, 50, 225)
E_vs_scalar_sum = ROOT.TH2D(
    "E_vs_scalar_sum", "Energy listed vs Scalar Sum of Particle Energies", 75, 0, 230, 75, 0, 230)

########################################
# Fastjet Setup
########################################
# https://fastjet.fr/repo/doxygen-3.4.1/classfastjet_1_1JetDefinition.html
jetdef = fastjet.JetDefinition(fastjet.antikt_algorithm, 0.4)
vector.register_awkward()

print("There are " + str(num_events) + " events")
for i in range(num_events):
    if E_branch[i] >= 200:
        continue
    if E_branch[i] <= 96:
        continue
    if i % 250 == 0:
        print(str(int(i / num_events * 100)) + "% done")

    tevent_selection.Fill(0)
    devent_selection.Fill(0)
    ########################################
    # Pre-clustering Event Cuts
    ########################################

    if abs(np.cos(STheta[i])) > 0.82:
        continue
    tevent_selection.Fill(1)
    devent_selection.Fill(1)

    if not passesWW[i]:
        continue
    tevent_selection.Fill(2)
    devent_selection.Fill(2)

    if not passesMissP[i]:
        continue
    tevent_selection.Fill(3)
    devent_selection.Fill(3)

    ########################################
    # Jet Clustering
    ########################################

    # Looping over all particles in the event and putting them in an array in the format:
    # [{"px" : __, "py" : __, "pz" : __, "E" : __}, {...}, ... ]
    # This is the format that FastJet wants them in
    tmp_energy = 0
    temp = []
    for k in range(nParticles[i]):
        temp_part = {}
        temp_part["px"] = px_branch[i][k]
        temp_part["py"] = py_branch[i][k]
        temp_part["pz"] = pz_branch[i][k]
        temp_part["E"] = np.sqrt(
            M_branch[i][k] ** 2 + px_branch[i][k] ** 2 + py_branch[i][k] ** 2 + pz_branch[i][k] ** 2)
        # tmp_energy += np.sqrt(M_branch[i][k]**2 + px_branch[i][k]**2 + py_branch[i][k]**2 + pz_branch[i][k]**2)
        tmp_energy += temp_part["E"]
        temp.append(temp_part)

    array1 = ak.Array(temp)
    E_hist.Fill(tmp_energy)
    E_vs_scalar_sum.Fill(E_branch[i], tmp_energy)

    cluster = fastjet.ClusterSequence(array1, jetdef)
    ########################################
    # Pre-clustering Event Cuts
    ########################################

    # Have to pass certain criteria to find these events

    isolatedPhotonEnergy = 0
    isoP = 0
    numNonPhotonJets = 0

    numHighELeptonClusters = 0

    jets = cluster.inclusive_jets()
    constituents = cluster.constituents()
    constituent_index = cluster.constituent_index()
    numClusters.Fill(len(jets))

    # print(" ")
    # print(cluster.inclusive_jets()[:]["E"])
    # print(constituents[:]["E"])

    if len(jets) < 2:
        continue
    tevent_selection.Fill(4)
    devent_selection.Fill(4)

    # find the jets that are above 10 GeV
    # and don't have a photon as their highest member
    good_jets_index = []

    # This code iterates through and finds the clusters that
    # have a photon as their highest energy.
    # photon flag = 4, leptons = 1,2
    for tmp_jet_thing, cl, index in zip(jets, constituents, cluster.constituent_index()):
        allPhotons = False
        highest_contE_index = np.argmax(cl[:]["E"])
        if pwflag[i][index[highest_contE_index]] == 4:
            allPhotons = True

        # Searches for clusters with a lepton that makes up more than 50% of total cluster energy
        for cont_index in index:
            if pwflag[i][cont_index] == 1 or pwflag[i][cont_index] == 2:
                for E in cl[:]["E"]:
                    if E > (0.5 * tmp_jet_thing["E"]):
                        numHighELeptonClusters += 1

        if allPhotons:
            for cont_index in index:
                isolatedPhotonEnergy += np.sqrt(
                    px_branch[i][cont_index] ** 2 + py_branch[i][cont_index] ** 2 + pz_branch[i][cont_index] ** 2)
            isoP += 1
            good_jets_index.append(0)
        elif tmp_jet_thing["E"] > 10:
            good_jets_index.append(1)
            numNonPhotonJets += 1
        else:
            good_jets_index.append(0)
    isolatedPhotonEnergyhist.Fill(isolatedPhotonEnergy)
    isolatedPhotons.Fill(isoP)
    numUnClustered.Fill(len(cluster.unclustered_particles()))
    highELeptonClusters.Fill(numHighELeptonClusters)

    # I got freaked out about the whole python scope thing
    # and now my code is becoming unreadable...
    good_jets = []
    for tmp_iter2, tmp_jet_iter in enumerate(jets):
        if good_jets_index[tmp_iter2] == 1:
            good_jets.append(tmp_jet_iter.to_list())

    # sort the good jets based on their energy
    good_jets = sorted(good_jets, key=lambda d: d['E'])

    if len(good_jets) >= 2:
        lj1 = good_jets[-1]
        lj2 = good_jets[-2]
        tmp_j1 = ROOT.TLorentzVector(
            lj1["px"],
            lj1["pz"],
            lj1["py"],
            lj1["E"],
        )
        tmp_j2 = ROOT.TLorentzVector(
            lj2["px"],
            lj2["pz"],
            lj2["py"],
            lj2["E"],
        )
        inv_mass = (tmp_j1 + tmp_j2).M()
        lInvMass.Fill(inv_mass)

    if len(good_jets) >= 3:
        tlj1 = good_jets[-1]
        tlj2 = good_jets[-2]
        tlj3 = good_jets[-3]
        tmp_tj1 = ROOT.TLorentzVector(
            tlj1["px"],
            tlj1["pz"],
            tlj1["py"],
            tlj1["E"],
        )
        tmp_tj2 = ROOT.TLorentzVector(
            tlj2["px"],
            tlj2["pz"],
            tlj2["py"],
            tlj2["E"],
        )
        tmp_tj3 = ROOT.TLorentzVector(
            tlj3["px"],
            tlj3["pz"],
            tlj3["py"],
            tlj3["E"],
        )
        inv_mass = (tmp_tj1 + tmp_tj2 + tmp_tj3).M()
        tlInvMass.Fill(inv_mass)

    isTrijet = False
    isDijetGamma = False
    if isolatedPhotonEnergy < 5:
        tevent_selection.Fill(5)
        if numNonPhotonJets >= 3:
            tevent_selection.Fill(6)
            isTrijet = True

            tj1 = good_jets[-1]
            tj2 = good_jets[-2]
            tj3 = good_jets[-3]
            tmp_j1 = ROOT.TLorentzVector(
                tj1["px"],
                tj1["pz"],
                tj1["py"],
                tj1["E"],
            )
            tmp_j2 = ROOT.TLorentzVector(
                tj2["px"],
                tj2["pz"],
                tj2["py"],
                tj2["E"],
            )
            tmp_j3 = ROOT.TLorentzVector(
                tj3["px"],
                tj3["pz"],
                tj3["py"],
                tj3["E"],
            )
            tInvMass.Fill((tmp_j1 + tmp_j2 + tmp_j3).M())
            tj1_v_E.Fill(tmp_j1.P(), E_branch[i])
            tj2_v_E.Fill(tmp_j2.P(), E_branch[i])
            tj3_v_E.Fill(tmp_j3.P(), E_branch[i])
    elif len(good_jets) >= 2:
        # I'm using the fact that python doesn't give
        # if/else blocks their own scope to reuse these variables
        # later in the dijet code without refinding these things.
        # Gross.

        dj1 = good_jets[-1]
        dj2 = good_jets[-2]
        tmp_j1 = ROOT.TLorentzVector(
            dj1["px"],
            dj1["pz"],
            dj1["py"],
            dj1["E"],
        )
        tmp_j2 = ROOT.TLorentzVector(
            dj2["px"],
            dj2["pz"],
            dj2["py"],
            dj2["E"],
        )
        inv_mass = (tmp_j1 + tmp_j2).M()
        dInvMass.Fill(inv_mass)
        devent_selection.Fill(5)
        if inv_mass > 36.188:
            devent_selection.Fill(6)
            if inv_mass < 96.188:
                devent_selection.Fill(7)
                dijet_p_event_energy.Fill(E_branch[i])
                isDijetGamma = True

    ########################################
    # Analysis Code
    ########################################

    # need to do this part
    # using only the good jets
    # so we need to link the good jets
    # to the constituents
    if isTrijet:

        jet_sorted_index = np.argsort(np.max(cluster.inclusive_jets()[:]["E"], axis=0))
        highest_energy_index = jet_sorted_index[-1]

        for jsi in reversed(jet_sorted_index):
            if good_jets_index[jsi] == 1:
                highest_energy_index = jsi
                break

        # for jet, cont, index in zip(cluster.inclusive_jets(), cluster.constituents(),cluster.constituent_index()):
        #     print(jet)
        #     for con, indy in zip(cont,index):
        #         tmp_p4 = ROOT.TLorentzVector(
        #             con["px"],
        #             con["py"],
        #             con["pz"],
        #             con["E"],
        #         )
        #         print(con)
        #         print(tmp_p4.Pt(),tmp_p4.Eta(),tmp_p4.Phi(),tmp_p4.M())
        #         print(pwflag[i][indy])
        #     print()

        jet = jets[highest_energy_index]
        cont = constituents[highest_energy_index]
        index = constituent_index[highest_energy_index]
        arr = sorted(cont, key=lambda x: x['E'], reverse=True)

        jetp4 = ROOT.TLorentzVector()
        jetp4.SetPxPyPzE(
            jet['px'],
            jet['py'],
            jet['pz'],
            jet['E']
        )

        listOfConstituentMomenta = []
        for tmpconst in range(len(arr)):
            tmp_p4 = ROOT.TLorentzVector(
                arr[tmpconst]["px"],
                arr[tmpconst]["py"],
                arr[tmpconst]["pz"],
                arr[tmpconst]["E"],
            )
            listOfConstituentMomenta.append(tmp_p4)

        tmpGraph = nXX_graph(listOfConstituentMomenta, jet["E"])

        tri_h_n50_p.Fill(jetp4.P(), tmpGraph.Eval(0.5))
        tri_h_n80_p.Fill(jetp4.P(), tmpGraph.Eval(0.8))
        tri_h_n90_p.Fill(jetp4.P(), tmpGraph.Eval(0.9))
        tri_h_n95_p.Fill(jetp4.P(), tmpGraph.Eval(0.95))
        tri_h_n99_p.Fill(jetp4.P(), tmpGraph.Eval(0.99))

        tE.Fill(jet["E"])

        nPi = 0
        for ind in index:
            if 0.134 < M_branch[i][ind] < 0.144:
                nPi += 1
        tPions.Fill(nPi)

    elif isDijetGamma:

        # Let's find  the two highest energy jets that also
        # match our earlier criteria for good jets
        jet_sorted_index = np.argsort(cluster.inclusive_jets()[:]["E"])
        dijet_index_1 = jet_sorted_index[-1]
        dijet_index_2 = jet_sorted_index[-2]
        for jsi in reversed(jet_sorted_index):
            if good_jets_index[jsi] == 1:
                dijet_index_1 = jsi
                break

        for jsi in reversed(jet_sorted_index):
            if (good_jets_index[jsi] == 1) and (jsi is not dijet_index_1):
                dijet_index_2 = jsi
                break

        jet = jets[dijet_index_1]
        cont = constituents[dijet_index_1]
        index = constituent_index[dijet_index_1]
        arr = sorted(cont, key=lambda x: x['E'], reverse=True)

        listOfConstituentMomenta = []
        for tmpconst in range(len(arr)):
            tmp_p4 = ROOT.TLorentzVector(
                arr[tmpconst]["px"],
                arr[tmpconst]["py"],
                arr[tmpconst]["pz"],
                arr[tmpconst]["E"],
            )
            listOfConstituentMomenta.append(tmp_p4)

        jetp4 = ROOT.TLorentzVector()
        jetp4.SetPxPyPzE(
            jet['px'],
            jet['py'],
            jet['pz'],
            jet['E']
        )

        tmpGraph = nXX_graph(listOfConstituentMomenta, jet["E"])
        di_h_n50_p.Fill(jetp4.P(), tmpGraph.Eval(0.5))
        di_h_n80_p.Fill(jetp4.P(), tmpGraph.Eval(0.8))
        di_h_n90_p.Fill(jetp4.P(), tmpGraph.Eval(0.9))
        di_h_n95_p.Fill(jetp4.P(), tmpGraph.Eval(0.95))
        di_h_n99_p.Fill(jetp4.P(), tmpGraph.Eval(0.99))

        dE.Fill(jet["E"])

        nPi = 0
        for ind in index:
            if 0.134 < M_branch[i][ind] < 0.144:
                nPi += 1
        dPions.Fill(nPi)

        jet = jets[dijet_index_2]
        cont = constituents[dijet_index_2]
        index = constituent_index[dijet_index_2]

        arr = sorted(cont, key=lambda x: x['E'], reverse=True)

        listOfConstituentMomenta = []
        for tmpconst in range(len(arr)):
            tmp_p4 = ROOT.TLorentzVector(
                arr[tmpconst]["px"],
                arr[tmpconst]["py"],
                arr[tmpconst]["pz"],
                arr[tmpconst]["E"],
            )
            listOfConstituentMomenta.append(tmp_p4)

        jetp4 = ROOT.TLorentzVector()
        jetp4.SetPxPyPzE(
            jet['px'],
            jet['py'],
            jet['pz'],
            jet['E']
        )

        tmpGraph = nXX_graph(listOfConstituentMomenta, jet["E"])
        di_h_n50_p.Fill(jetp4.P(), tmpGraph.Eval(0.5))
        di_h_n80_p.Fill(jetp4.P(), tmpGraph.Eval(0.8))
        di_h_n90_p.Fill(jetp4.P(), tmpGraph.Eval(0.9))
        di_h_n95_p.Fill(jetp4.P(), tmpGraph.Eval(0.95))
        di_h_n99_p.Fill(jetp4.P(), tmpGraph.Eval(0.99))

        dE.Fill(jet["E"])

        nPi = 0
        for ind in index:
            if 0.134 < M_branch[i][ind] < 0.144:
                nPi += 1
        dPions.Fill(nPi)

    else:
        a = 0

print("Finished analysis. Saving histograms...")

for thing in [tri_h_n50_p, tri_h_n80_p, tri_h_n90_p, tri_h_n95_p, tri_h_n99_p, di_h_n50_p, di_h_n80_p, di_h_n90_p,
              di_h_n95_p, di_h_n99_p]:
    # thing.Smooth()
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

# new histograms
savehist(isolatedPhotons, "isolated_photons")
savehist(isolatedPhotonEnergyhist, "isolatedPhotonEnergy")
savehist(numClusters, "numClusters")

savehist(highELeptonClusters, "highELeptonClusters")

savehist(tevent_selection, "trijet_event_selection")
savehist(devent_selection, "dijet_event_selection")

savehist(tE, "trijet_energy")
savehist(dE, "dijet_energy")
savehist(tPions, "trijet_pions")
savehist(dPions, "dijet_pions")
savehist(tInvMass, "tInvMass")
savehist(dInvMass, "dInvMass")
savehist(lInvMass, "lInvMass")
savehist(tlInvMass, "tlInvMass")

savehist(numUnClustered, "numUnClustered")
savehist(dijet_p_event_energy, "dijet_p_event_energy")

savehist(tE, "tE")
savehist(dE, "dE")
savehist(E_hist, "E_hist")
savehist(E_vs_scalar_sum, "E_vs_scalar_sum")

savehist(tj1_v_E, "tj1_v_E")
savehist(tj2_v_E, "tj2_v_E")
savehist(tj3_v_E, "tj3_v_E")
