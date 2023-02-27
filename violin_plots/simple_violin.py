import seaborn as sns
import matplotlib.pyplot as plt
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
        arr.append((bins[i+1]-bins[i])/2+bins[i])
    return arr

def generator(bins, prob,sz=10):
    arr = []
    for i in range(0,len(bins)):
        for j in range(0,int(prob[i])):
            arr.append(bins[i])
    return arr

def split_bins(hist):
    arr = hist[0]
    lists = []
    for i in arr:
        lists.append(generator(fix_bins(hist[2]),i))
    return lists

def simple_plot(file_name,nXX):
    print("Creating "+ nXX +" plot for " + file_name + "...") 
    uproot_file = uproot.open("./violin_files/" + file_name+ "_histograms.root")
    data1 = split_bins(uproot_file["h_"+nXX+"_p;1"].to_numpy())
    sns.violinplot(data=data1)
    
    plt.title(file_name + " " + nXX)
    plt.xlabel("Jet P[GeV]")
    plt.ylabel(nXX)
    plt.savefig('plots/'+ file_name + '_'+nXX+'.png')
    plt.close()
