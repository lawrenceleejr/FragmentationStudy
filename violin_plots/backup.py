import seaborn as sns
from IPython.display import display, HTML
import matplotlib.pyplot as plt
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
            for j in range(0,int(row[i])):
                temp = {"plot":row["plot"],"H":float(p_bins[int(data_col[i])]),"value":float(index) }
                temp_df = pd.DataFrame(temp,index=[num])
                num = num + 1
                dt = pd.concat([dt,temp_df])
    return dt

def split_violin(file_name1, name1, text1, file_name2, name2,text2, nxx,ylim):
    file1 = uproot.open("../root_files/violin_files/" + file_name1+ "_histograms.root")
    file2 = uproot.open("../root_files/violin_files/" + file_name2+ "_histograms.root")

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

    print(final)

    fig, ax = plt.subplots()
    ax2 = ax.twiny()
    ax3 = ax.twiny()
    sns.violinplot(data=final,x='H',y='value',hue="plot",inner=None,split=True,ax=ax,
                   cut = 30,legend=False,
                   palette= {
                                name1:(
                                        round(30/256,3),
                                        round(144/256,3),
                                        round(255/256,3)
                                        ), 
                                name2:(    
                                        round(235/256,3),
                                        round(150/256,3),
                                        round(5/256,3)
                                        )
                                }
                   )
    sns.regplot(data=final.loc[final['plot'] == name1],x='H',y='value',scatter=False,ax=ax2,
                line_kws={"path_effects": [path_effects.SimpleLineShadow(),path_effects.Normal()]},
                ci=None,
                color=( 
                        round(30/256,3),
                        round(144/256,3),
                        round(255/256,3)
                       )
                )
    sns.regplot(data=final.loc[final['plot'] == name2],x='H',y='value',scatter=False,ax=ax3,
                line_kws={"path_effects": [path_effects.SimpleLineShadow(), path_effects.Normal()]},
                ci=None,
                color=( 
                        round(235/256,3), 
                        round(150/256,3), 
                        round(5/256,3)
                       )
                )
    ax2.grid(False)
    ax2.set(xlabel=None,ylabel=None)
    ax2.tick_params(axis = 'x',which='both',bottom=False,top=False,labelbottom=False,labeltop=False)
    ax3.grid(False)
    ax3.set(xlabel=None,ylabel=None)
    ax3.tick_params(axis = 'x',which='both',bottom=False,top=False,labelbottom=False,labeltop=False)
    ax.set(xlabel="Jet P [GeV]",ylabel=r'$n_{'+str(nxx)+'}$',title=name1 +" vs "+ name2+", " + r'$n_{'+str(nxx)+'}$')
    plt.text(6.5, 13, text1,
             rotation=90., 
             fontdict={'family': 'serif',
                       'color': ( 
                                 round(30/256,3),
                                 round(144/256,3),
                                 round(255/256,3)
                                 ),
                       'weight': 'normal',
                       'size': 16,
                       }
             )
    plt.text(15, 13, text2, 
             rotation=90.,
             fontdict={'family': 'serif',
                       'color': (
                           round(235/256,3),
                           round(150/256,3),
                           round(5/256,3)
                           ),
                       'weight': 'normal',
                       'size': 16,
                       })
    ax.legend([],[], frameon=False)
    x_labels = []
    for i in range(0, len(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1]) - 1):
        x_labels.append(str(int(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1][i]))+
                        "-"+str(int(file1["h_"+"n"+str(nxx)+"_p;1"].to_numpy()[1][i+1]))) 
    ax.tick_params(axis = 'x',which='both',top=False,labeltop=False)
    ax.set_xticklabels(x_labels)
    plt.gca().set_ylim(bottom=0,top=ylim)
    plt.tick_params(axis = 'x',which='both',bottom=False,top=False,labelbottom=False,labeltop=False)
    plt.gcf().set_size_inches(15.5, 8.5)
    plt.savefig('plot_images/'+ file_name1+"_v_"+file_name2 + '_'+"n"+str(nxx)+'.png')
    plt.close()

