import seaborn as sns
import matplotlib.pyplot as plt
import uproot
import numpy as np

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
    print(len(arr))
    return arr

def split_bins(hist):
    arr = hist[0]
    lists = []
    for i in arr:
        lists.append(generator(fix_bins(hist[2]),i))
    return np.array(lists)

file = uproot.open("~/YETI_2/RootFiles/yeti2.root")

sns.violinplot(data=split_bins(file["hist"].to_numpy()), split=True)

plt.show()
