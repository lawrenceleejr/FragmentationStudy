import seaborn as sns
from IPython.display import display, HTML
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib import gridspec
import uproot
import numpy as np
import pandas as pd
from violin_plots import fix_bins, generator, split_bins, dataframe_fixer, split_violin
from mean_plot import mean_plot

def shared_plot(file_name1, name1, text1, file_name2, name2,text2, nxx,ylim1,ylim2,xlim):
    print("Starting Shared Plot...")
    file1 = uproot.open("../root_files/violin_files/" + file_name1+ "_2_histograms.root")
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=False)
    split_violin(file_name1 + "_2", name1, text1, file_name2+"_2", name2,text2, nxx,ylim1,flag=True,fig=fig,ax=ax1)
    mean_plot(file_name1, name1, text1, file_name2, name2,text2, nxx,ylim2,xlim,flag=True,fig=fig,ax=ax2)
    #ax1.get_shared_x_axes().join(ax1, ax2)
    ax1.set_xticklabels([])
    ax1.set(xlabel=None)
    fig.subplots_adjust(wspace=0, hspace=0)
    fig.subplots_adjust(bottom=0.15,left=0.10, right=0.97, top=0.97)
    #gs = gridspec.GridSpec(2, 1, width_ratios=[1],
    #    wspace=0.0, hspace=0.0, top=0.95, bottom=0.05, left=0.17, right=0.845)
    plt.show()
    #plt.savefig('plot_images/squished_'+ file_name1+"_v_"+file_name2 + '_'+"n"+str(nxx)+'.pdf',format="pdf", bbox_inches="tight")
    plt.close()

shared_plot("eeToJJJ_50k_1TeV","JJJ","ee \u27F6 3j","eeToZZToJJ_50k_1TeV","ZZ","ee \u27F6 ZZ \u27F6 4j",90,16,10,3.5)
