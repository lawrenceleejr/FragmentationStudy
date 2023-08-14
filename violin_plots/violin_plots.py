import seaborn as sns
from IPython.display import display, HTML
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.patheffects as path_effects
import uproot
import numpy as np
import pandas as pd

def fix_bins(bins):
    arr = []
    #uproot delivers the bins in an array that 
    # has one more element than the total number of bins
    #This sets each value in the middle of the bin
    #so the length of the array matches the number of bins
    for i in range(0, len(bins)-1):
        arr.append(str(round((bins[i+1]-bins[i])/2+bins[i],2)))
    return arr

def generator(bins, prob,sz=10):
    arr = []
    for i in range(0,len(bins)):
        for j in range(0,int(prob[i])):
            arr.append(bins[i])
    return arr

def split_bins(dataframe,hist,plot_name,bins):
    arr = hist[0]
    count = 0
    for i in arr:
        #temp = {bins[j] : (i.tolist()+ [plot_name]+[str(round((hist[1][count]-hist[1][count+1])/2+hist[1][count],2))])[j] for j in range(len(bins))}
        temp = {bins[j] : i.tolist()[j] for j in range(len(bins))}
        temp_df = pd.DataFrame(temp,index=[count])
        dataframe = pd.concat([dataframe,temp_df])
        count = count + 1
    return dataframe

def dataframe_fixer(data,p_val):
    col = ["plot","H","value"]
    dt = pd.DataFrame([],columns=col)
    data_col = list(data.columns)
    num = 0
    p_bins = {j : fix_bins(p_val)[j] for j in range(0,len(fix_bins(p_val)))}
    for index, row in data.iterrows():
        for i in range(0,len(data_col)-1):
            for j in range(0,int(round(float(row[i])))):
                temp = {"plot":row["plot"],"H":float(p_bins[int(data_col[i])]),"value":float(index) }
                temp_df = pd.DataFrame(temp,index=[num])
                num = num + 1
                dt = pd.concat([dt,temp_df])
    return dt

def split_violin(file_name1, name1, text1, file_name2, name2,text2, nxx,ylim,flag=False,fig=None,ax=None):
    if(flag != True):
        fig, ax = plt.subplots()
    file1 = uproot.open("../root_files/violin_files/" + file_name1+ "_histograms.root")
    file2 = uproot.open("../root_files/violin_files/" + file_name2+ "_histograms.root")

    print("Violin Plot Started")
    print("Creating " + name1+ " vs " + name2 + " for " + "n"+str(nxx) + "...") 
    bins = fix_bins(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[2])

    dt = pd.DataFrame([],columns=bins)
    d1 = split_bins(dt,file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy(),name1,bins)
    d2 = split_bins(dt,file2["h_"+"n"+str(nxx)+"_p;1"].to_numpy(),name2,bins) 

    d1 = d1.T
    d2 = d2.T


    comb = pd.concat([d1.assign(plot=name1),d2.assign(plot=name2)],axis = 0)
    #I'm assuming that the binning for both plots is exactly the same
    final = dataframe_fixer(comb,file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1])
    averages = final.loc[final['plot'] == name1].groupby('H').mean()
    #print(final)
    #print(averages)
    ax2 = ax.twiny()
    ax3 = ax.twiny()
    color_blue =    (
                    round(30/256,3),
                    round(144/256,3),
                    round(255/256,3)
                    )
    color_orange =  (    
                    round(255/256,3),
                    round(141/256,3),
                    round(30/256,3)
                    )
    sns.violinplot(data=final,x='H',y='value',hue="plot",inner=None,split=True,ax=ax,
                   cut = 30,legend=False,
                   palette= {
                       name1:color_blue, 
                       name2:color_orange    
                       }
                   )
    ax2.plot(final.loc[final['plot'] == name1].groupby('H').mean(),
             color=color_blue,
             path_effects = [path_effects.SimpleLineShadow(alpha = 0.25),
                             path_effects.SimpleLineShadow(offset=(2,-4),alpha=0.15),
                             path_effects.Normal()],
             linewidth = 3.5,
             )
    ax2.plot(final.loc[final['plot'] == name1].groupby('H').mean(),"o",markersize=13,
             linestyle='None',markeredgecolor=color_blue,markerfacecolor='white',
             markeredgewidth=2)
    ax3.plot(final.loc[final['plot'] == name2].groupby('H').mean(),
             color=color_orange,
             path_effects = [path_effects.SimpleLineShadow(alpha = 0.25),
                             path_effects.SimpleLineShadow(offset=(2,-4),alpha=0.15),
                             path_effects.Normal()],
             linewidth = 3.5

             )   
    ax3.plot(final.loc[final['plot'] == name2].groupby('H').mean(), "o",markersize=13,
             linestyle='None',markeredgecolor=color_orange,markerfacecolor='white',
             markeredgewidth=2)
    if (flag != True):
        plt.text(0.019, 0.62, text1,
                rotation=90., 
                fontdict={'family': 'serif',
                            'color': color_blue, 
                            'weight': 'bold',
                            'size': 24,
                        },
                transform = ax.transAxes
                )
        plt.text(0.059, 0.62, text2, 
                rotation=90.,
                fontdict={'family': 'serif',
                            'color': color_orange, 
                            'weight': 'bold',
                            'size': 24,
                        },
                transform = ax.transAxes
                )
    ax.legend([],[], frameon=False)
    ax.set(ylabel=r'$ n_{'+str(nxx)+r'} $',title=None)
    xlbl = ax.xaxis.get_label()
    xlbl.set_fontsize(26)
    ylbl = ax.yaxis.get_label()
    ylbl.set_fontsize(28)
    ax2.grid(False)
    ax2.set(xlabel=None,ylabel=None)
    ax2.tick_params(axis = 'x',which='both',bottom=False,top=False,labelbottom=False,labeltop=False)
    ax3.grid(False)
    ax3.set(xlabel=None,ylabel=None)
    ax3.tick_params(axis = 'x',which='both',bottom=False,top=False,labelbottom=False,labeltop=False)
    if(flag != True):
        ax.set(xlabel="Jet P [GeV]")
        x_labels = []
        for i in range(0, len(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1]) - 1):
            x_labels.append(str(int(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1][i]))+
                            "-"+str(int(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1][i+1]))) 
        ax.tick_params(axis = 'x',which='both',top=False,labeltop=False)
        ax.set_xticklabels(x_labels, fontsize = 19, rotation=-18)
    ax.tick_params(axis='y', which='major', labelsize=20)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().set_ylim(bottom=0,top=ylim)
    plt.gcf().set_size_inches(15.5, 8.5)
    #plt.tight_layout()
    #plt.show()
    #plt.savefig('plot_images/'+ file_name1+"_v_"+file_name2 + '_'+"n"+str(nxx)+'.pdf', format="pdf", bbox_inches="tight")
    #return fig,ax

