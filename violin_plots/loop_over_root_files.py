from simple_violin import simple_plot

files = ['eeToJJJ_50k_1TeV','eeToJJJ_50k_4TeV','eeToZZToJJ_50k_1TeV','eeToZZToJJ_50k_500GeV','eeToZgamma_50k_1TeV','eeToZgamma_50k_4TeV']
nXX = ['n50','n80','n90','n95','n99']

for f in files:
    for n in nXX:
        simple_plot(f,n)

