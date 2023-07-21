// main41.cc is a part of the PYTHIA event generator.
// Copyright (C) 2022 Torbjorn Sjostrand.
// PYTHIA is licenced under the GNU GPL v2 or later, see COPYING for details.
// Please respect the MCnet Guidelines, see GUIDELINES for details.

// Authors: Mikhail Kirsanov <Mikhail.Kirsanov@cern.ch>.

// Keywords: basic usage; hepmc;

// This program illustrates how HepMC can be interfaced to Pythia8.
// It studies the charged multiplicity distribution at the LHC.
// HepMC events are output to the hepmcout41.dat file.

// WARNING: typically one needs 25 MB/100 events at the LHC.
// Therefore large event samples may be impractical.

#include "Pythia8/Pythia.h"
#ifndef HEPMC2
#include "Pythia8Plugins/HepMC3.h"
#else
#include "Pythia8Plugins/HepMC2.h"
#endif

using namespace Pythia8;

bool endsWith(string s, string sub) { return s.rfind(sub) == (s.length() - sub.length()) ? 1 : 0; }
string remove(string s, string sub) { if (s.find(sub) != std::string::npos) s.erase(s.find(sub), sub.length()); return s;}


// Helper class to parse command line options.
class InputParser {

public:

  InputParser (int &argc, char **argv) {
    for (int i = 1; i < argc; ++i) arglist.push_back(string(argv[i]));
  }

  const string& getOption(const string &opt) const {
    vector<string>::const_iterator itr = find(arglist.begin(),
      arglist.end(), opt);
    if (itr != arglist.end() && ++itr != arglist.end()) return *itr;
    return "";
  }

  bool hasOption(const string &opt) const {
    return find(arglist.begin(), arglist.end(), opt) != arglist.end();
  }

private:
  vector<string> arglist;
};

int main(int argc, char* argv[]) {

  InputParser ip(argc, argv);

  if(ip.hasOption("-h") || ip.hasOption("--help")) {
    cout << "Usage: ./main00 -f eeToZgamma_50k_unweighted_events.lhe.gz.\n" << endl;
    return 0;
  }
  // Print version number and exit.
  if(ip.hasOption("-v") || ip.hasOption("--version")) {
    cout << "PYTHIA version: " << PYTHIA_VERSION << endl;
    return 0;
  }
  string lhefile = "eeToZgamma_50k_unweighted_events.lhe.gz";
  if(ip.hasOption("-f")) lhefile = ip.getOption("-f");

  int nEvents = -1;
  if(ip.hasOption("-e")) nEvents = stoi(ip.getOption("-e"));

  int shower_model = 1; //https://pythia.org/latest-manual/PartonShowers.html
  if(ip.hasOption("-s")) shower_model = stoi(ip.getOption("-s"));

  string outfile = remove(remove(lhefile,".gz"),".lhe");
  outfile += "_pythia";
  if (shower_model==2) outfile += "_vincia";

  // Interface for conversion from Pythia8::Event to HepMC
  // event. Specify file where HepMC events will be stored.
  Pythia8::Pythia8ToHepMC topHepMC(outfile+".hepmc");

  // Generator. Process selection. LHC initialization. Histogram.
  Pythia pythia;
  pythia.readString("Beams:frameType = 4");
  pythia.readString("Beams:LHEF = "+lhefile);
  pythia.readString("Init:showAllParticleData = off");
  pythia.readString("Next:numberCount = 1000");
  pythia.readString("PhaseSpace:pTHatMin = 20.");
  pythia.readString("Next:numberShowInfo = 0");
  pythia.readString("Next:numberShowProcess = 1");
  pythia.readString("Next:numberShowEvent = 1");
  pythia.readString("PartonLevel:MPI = on");  //default = on
  pythia.readString("PartonLevel:ISR = off"); //default = on
  pythia.readString("PartonLevel:FSR = off"); //default = on
  pythia.readString("HadronLevel:all = on");  //default = on
  if (shower_model==2){
  // VINCIA settings: https://vincia.hepforge.org/current/share/Vincia/htmldoc/VinciaShower.html
    pythia.readString("PartonShowers:model   = 2");
    pythia.readString("Vincia:verbose        = 1");
  }

  //pythia.init();
  if(!pythia.init()) { return EXIT_FAILURE; }

  Hist nJets("Number of jets", 20, -0.5, 19.5);Hist* nJetsPtr    = &nJets;
  SlowJet slowJet( -1, 0.7, 20., 4., 2, 1);

  // Begin event loop. Generate event until none left in input file.
  for (int iEvent = 0; ; ++iEvent) {
    if (nEvents>0 && iEvent >= nEvents) break;
    if (pythia.info.atEndOfFile()) break; // If failure because reached end of file then exit event loop.
    if (!pythia.next()) continue; //Skip if error

    // Construct new empty HepMC event, fill it and write it out.
    topHepMC.writeNextEvent( pythia );

    double weight = pythia.info.weight();
    slowJet. analyze( pythia.event );
    nJetsPtr->fill( slowJet.sizeJet() , weight);


  // End of event loop.
  }
  pythia.stat();

  // Output histograms
  cout << nJets;

  // Done.
  return 0;
}