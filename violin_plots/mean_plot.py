import seaborn as sns
from IPython.display import display, HTML
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import uproot
import numpy as np
import pandas as pd
from violin_plots import fix_bins, generator, split_bins, dataframe_fixer


def produce_dataframe(file1,file2,name1,name2,bins,nxx):
    dt = pd.DataFrame([],columns=bins)
    d1 = split_bins(dt,file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy(),name1,bins)
    d2 = split_bins(dt,file2["h_"+"n"+str(nxx)+"_p;1"].to_numpy(),name2,bins)

    d1 = d1.T
    d2 = d2.T

    comb = pd.concat([d1.assign(plot=name1),d2.assign(plot=name2)],axis = 0)

    return dataframe_fixer(comb,file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1])

def mean_plot(file_name1, name1, text1, file_name2, name2,text2, nxx,ylim=10,xlim=5,flag=False,fig=None,ax=None):
    if (flag != True): 
        fig, ax = plt.subplots()
    file1 = uproot.open("../root_files/violin_files/" + file_name1+ "_2_histograms.root")
    file2 = uproot.open("../root_files/violin_files/" + file_name2+ "_2_histograms.root")

    file1h = uproot.open("../root_files/violin_files/" + file_name1+ "_herwig_histograms.root")
    file2h = uproot.open("../root_files/violin_files/" + file_name2+ "_herwig_histograms.root")

    file1v = uproot.open("../root_files/violin_files/" + file_name1+ "_pythia_vincia_histograms.root")
    file2v = uproot.open("../root_files/violin_files/" + file_name2+ "_pythia_vincia_histograms.root")

    print("Mean Plot Started") 
    print("Creating " + name1+ " vs " + name2 + " for " + "n"+str(nxx) + "...") 
    
    bins = fix_bins(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[2])
    pythia_data = produce_dataframe(file1,file2,name1,name2,bins,nxx)
    print("Finished pythia dataframe...")
    print(pythia_data)
    herwig_data = produce_dataframe(file1h,file2h,name1,name2,bins,nxx)
    print("Finished herwig dataframe...")
    print(herwig_data)
    vincia_data = produce_dataframe(file1v,file2v,name1,name2,bins,nxx)
    print("Finished vincia datatframe...")
    print(vincia_data)

    color_blue = (
            round(30/256,3),
            round(144/256,3),
            round(255/256,3)
            )
    color_orange = (    
                    round(255/256,3),
                    round(141/256,3),
                    round(30/256,3)
                    )
    #Herwig starts here
    ax.plot(herwig_data.loc[herwig_data['plot'] == name1].groupby('H').mean(),
             color=color_blue,
             path_effects = [path_effects.SimpleLineShadow(alpha = 0.25),
                             path_effects.SimpleLineShadow(offset=(2,-4),alpha=0.15),
                             path_effects.Normal()],
             linewidth = 3,
             )
    ax.plot(herwig_data.loc[herwig_data['plot'] == name1].groupby('H').mean(),"s",markersize=16,
            linestyle='None',markeredgecolor=color_blue,markerfacecolor=color_blue,
            markeredgewidth=2,label="Herwig")
    ax.plot(herwig_data.loc[herwig_data['plot'] == name2].groupby('H').mean(),
             color=color_orange,
             path_effects = [path_effects.SimpleLineShadow(alpha = 0.25),
                             path_effects.SimpleLineShadow(offset=(2,-4),alpha=0.15),
                             path_effects.Normal()],
             linewidth = 3
             )   
    ax.plot(herwig_data.loc[herwig_data['plot'] == name2].groupby('H').mean(), "s",markersize=16,
            linestyle='None',markeredgecolor=color_orange,markerfacecolor=color_orange,
            markeredgewidth=2)

    #Pythia
    ax.plot(pythia_data.loc[pythia_data['plot'] == name1].groupby('H').mean(),
             color=color_blue,
             path_effects = [path_effects.SimpleLineShadow(alpha = 0.25),
                             path_effects.SimpleLineShadow(offset=(2,-4),alpha=0.15),
                             path_effects.Normal()],
             linewidth = 3,
             )
    ax.plot(pythia_data.loc[pythia_data['plot'] == name1].groupby('H').mean(),"o",markersize=16,
            linestyle='None',markeredgecolor=color_blue,markerfacecolor='white',
            markeredgewidth=2,label="Pythia")
    ax.plot(pythia_data.loc[pythia_data['plot'] == name2].groupby('H').mean(),
             color=color_orange,
             path_effects = [path_effects.SimpleLineShadow(alpha = 0.25),
                             path_effects.SimpleLineShadow(offset=(2,-4),alpha=0.15),
                             path_effects.Normal()],
             linewidth = 3
             )   
    ax.plot(pythia_data.loc[pythia_data['plot'] == name2].groupby('H').mean(), "o",markersize=16,
            linestyle='None',markeredgecolor=color_orange,markerfacecolor='white',
            markeredgewidth=2)

    #Vincia
    ax.plot(vincia_data.loc[vincia_data['plot'] == name1].groupby('H').mean(),
             color=color_blue,
             path_effects = [path_effects.SimpleLineShadow(alpha = 0.25),
                             path_effects.Normal()],
             linewidth = 3,
             )
    ax.plot(vincia_data.loc[vincia_data['plot'] == name1].groupby('H').mean(),"^",markersize=14,
            linestyle='None',markeredgecolor=color_blue,markerfacecolor='white',
            markeredgewidth=2,label="Vincia")
    ax.plot(vincia_data.loc[vincia_data['plot'] == name2].groupby('H').mean(),
             color=color_orange,
             linewidth = 3
            )   
    ax.plot(vincia_data.loc[vincia_data['plot'] == name2].groupby('H').mean(), "^",markersize=14,
            linestyle='None',markeredgecolor=color_orange,markerfacecolor='white',
            markeredgewidth=2)

    ax.text(0.019, 0.9, text1,
             fontdict={'family': 'serif',
                       'color': color_blue, 
                       'weight': 'bold',
                       'size': 22,
                       },
             transform = ax.transAxes
             )
    ax.text(0.019, 0.76, text2, 
             fontdict={'family': 'serif',
                       'color': color_orange, 
                       'weight': 'bold',
                       'size': 22,
                       },
             transform = ax.transAxes
             )
    ax.set(xlabel="Jet p [GeV]",ylabel=r'$ \langle n_{'+str(nxx)+r'} \rangle $',title='')
    xlbl = ax.xaxis.get_label()
    xlbl.set_fontsize(26)
    ylbl = ax.yaxis.get_label()
    ylbl.set_fontsize(28)
    #if (flag != True):
    x_labels = []
    for i in range(0, len(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1]) - 1):
        x_labels.append(str(int(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1][i]))+
                        "-"+str(int(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1][i+1]))) 
    ax.tick_params(axis = 'x',which='both',top=False,labeltop=False)
    ax.set_xticklabels(x_labels, fontsize = 19,rotation=-18)
    ax.tick_params(axis='y', which='major', labelsize=20)
    ax.set_xticks(pythia_data.loc[pythia_data['plot'] == name1].groupby('H').mean().index.tolist())
    ax.legend(loc='lower right',fontsize=18)
    ax.set_ylim(bottom=xlim,top=ylim)
    plt.gcf().set_size_inches(15.5, 8.5)
    #plt.tight_layout()
    #plt.savefig('plot_images/'+ file_name1+"_v_"+file_name2 + '_'+"n"+str(nxx)+'.pdf',format="pdf", bbox_inches="tight")
    #plt.show()
    #plt.close()
    #return fig,ax

#mean_plot("eeToJJJ_50k_1TeV","JJJ","ee \u27F6 3j","eeToZZToJJ_50k_1TeV","ZZ","ee \u27F6 ZZ \u27F6 4j",90,10)
