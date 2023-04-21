import seaborn as sns
from IPython.display import display, HTML
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import uproot
import numpy as np
import pandas as pd
from violin_plots import fix_bins, generator, split_bins, dataframe_fixer

def mean_plot(file_name1, name1, text1, file_name2, name2,text2, nxx,ylim):
    file1 = uproot.open("../root_files/violin_files/" + file_name1+ "_2_histograms.root")
    file2 = uproot.open("../root_files/violin_files/" + file_name2+ "_2_histograms.root")

    file1h = uproot.open("../root_files/violin_files/" + file_name1+ "_herwig_histograms.root")
    file2h = uproot.open("../root_files/violin_files/" + file_name2+ "_herwig_histograms.root")
    print("Creating " + name1+ " vs " + name2 + " for " + "n"+str(nxx) + "...") 
    bins = fix_bins(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[2])

    dt = pd.DataFrame([],columns=bins)
    d1 = split_bins(dt,file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy(),name1,bins)
    d2 = split_bins(dt,file2["h_"+"n"+str(nxx)+"_p;1"].to_numpy(),name2,bins) 

    d1 = d1.T
    d2 = d2.T

    comb = pd.concat([d1.assign(plot=name1),d2.assign(plot=name2)],axis = 0)

    #The Herwig stuff is just the same as the first data put with an h appended

    final = dataframe_fixer(comb,file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1])

    dth = pd.DataFrame([],columns=bins)
    d1h = split_bins(dth,file1h["h_"+"n"+str(nxx)+"_p;1"].to_numpy(),name1,bins)
    d2h = split_bins(dth,file2h["h_"+"n"+str(nxx)+"_p;1"].to_numpy(),name2,bins) 

    d1h = d1h.T
    d2h = d2h.T

    combh = pd.concat([d1h.assign(plot=name1),d2h.assign(plot=name2)],axis = 0)

    finalh = dataframe_fixer(combh,file1h["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1])

    fig, ax = plt.subplots()
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
    ax.plot(final.loc[final['plot'] == name1].groupby('H').mean(),
             color=color_blue,
             path_effects = [path_effects.SimpleLineShadow(alpha = 0.25),
                             path_effects.SimpleLineShadow(offset=(2,-4),alpha=0.15),
                             path_effects.Normal()],
             linewidth = 3.5,
             )
    ax.plot(final.loc[final['plot'] == name1].groupby('H').mean(),"o-",markersize=10,
             linestyle='None',markeredgecolor=color_blue,markerfacecolor='white')
    ax.plot(final.loc[final['plot'] == name2].groupby('H').mean(),
             color=color_orange,
             path_effects = [path_effects.SimpleLineShadow(alpha = 0.25),
                             path_effects.SimpleLineShadow(offset=(2,-4),alpha=0.15),
                             path_effects.Normal()],
             linewidth = 3.5

             )   
    ax.plot(final.loc[final['plot'] == name2].groupby('H').mean(), "o-",markersize=10,
             linestyle='None',markeredgecolor=color_orange,markerfacecolor='white')


    #Herwig starts here
    ax.plot(finalh.loc[finalh['plot'] == name1].groupby('H').mean(),
             color=color_blue,
             path_effects = [path_effects.SimpleLineShadow(alpha = 0.25),
                             path_effects.SimpleLineShadow(offset=(2,-4),alpha=0.15),
                             path_effects.Normal()],
             linewidth = 3.5,
             )
    ax.plot(finalh.loc[finalh['plot'] == name1].groupby('H').mean(),"o-",markersize=10,
             linestyle='None',markeredgecolor=color_blue,markerfacecolor='black')
    ax.plot(finalh.loc[finalh['plot'] == name2].groupby('H').mean(),
             color=color_orange,
             path_effects = [path_effects.SimpleLineShadow(alpha = 0.25),
                             path_effects.SimpleLineShadow(offset=(2,-4),alpha=0.15),
                             path_effects.Normal()],
             linewidth = 3.5

             )   
    ax.plot(finalh.loc[finalh['plot'] == name2].groupby('H').mean(), "o-",markersize=10,
             linestyle='None',markeredgecolor=color_orange,markerfacecolor='black')
    plt.text(0.019, 0.8, text1,
             fontdict={'family': 'serif',
                       'color': color_blue, 
                       'weight': 'normal',
                       'size': 24,
                       },
             transform = ax.transAxes
             )
    plt.text(0.019, 0.7, text2, 
             fontdict={'family': 'serif',
                       'color': color_orange, 
                       'weight': 'normal',
                       'size': 24,
                       },
             transform = ax.transAxes
             )
    ax.legend([],[], frameon=False)
    ax.set(xlabel="Jet P [GeV]",ylabel=r'$n_{'+str(nxx)+'}$',title='')
    xlbl = ax.xaxis.get_label()
    xlbl.set_fontsize(24)
    ylbl = ax.yaxis.get_label()
    ylbl.set_fontsize(24)
    x_labels = []
    for i in range(0, len(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1]) - 1):
        x_labels.append(str(int(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1][i]))+
                        "-"+str(int(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1][i+1]))) 
    ax.tick_params(axis = 'x',which='both',top=False,labeltop=False)
    ax.set_xticklabels(x_labels, fontsize = 15)
    ax.tick_params(axis='y', which='major', labelsize=17)
    plt.gca().set_ylim(bottom=0,top=ylim)
    plt.gcf().set_size_inches(15.5, 8.5)
    plt.tight_layout()
    #plt.savefig('plot_images/'+ file_name1+"_v_"+file_name2 + '_'+"n"+str(nxx)+'.png')
    plt.show()
    plt.close()

mean_plot("eeToJJJ_50k_4TeV","JJJ","ee \u27F6 jjj","eeToZgamma_50k_4TeV","Z\u03B3","ee \u27F6 Z\u03B3",90,10)
