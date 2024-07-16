import matplotlib.pyplot as plt
import csv
import numpy as np
from scipy.integrate import simps

from scipy.interpolate import interp1d
from numpy import interp

from matplotlib import colormaps


def plot_roc_curve(fpr1, tpr1, fpr2, tpr2, title='ROC Curve', output_filename='roc_curve.pdf'):
    """
    Plots an ROC curve given the false positive rate and true positive rate.
    
    Parameters:
    - fpr: List or array of false positive rates
    - tpr: List or array of true positive rates
    - title: Title of the plot
    """
    
    # Interpolate to create a smooth curve
    # interp_func = interp1d(fpr, tpr, kind='cubic')
    # fpr_smooth = np.linspace(0, 1, 100)
    # tpr_smooth = interp_func(fpr_smooth)

    euclideandistance = 0
    for x1, y1, x2, y2 in zip(fpr1,tpr1,fpr2,tpr2):
        euclideandistance += np.hypot((x2-x1),(y2-y1))

    AUC1 = np.trapz(tpr1,fpr1)
    AUC2 = np.trapz(tpr2,fpr2)

    plt.figure()


    plasma_cmap = colormaps.get_cmap('brg')

    N = len(fpr1)-1
    # Discretize the colormap into N segments

    goodDataStart = np.argmax(fpr1 > 0.0001)
    goodDataEnd = np.argmax(fpr1 > 0.999)

    N = goodDataEnd - goodDataStart

    print(goodDataStart,goodDataEnd)

    colors = [(1,1,1,0) for i in range(goodDataStart)]
    colors += [plasma_cmap( i/N ) for i in range(0,N-8)[::-1]]
    colors += [(1,1,1,0) for i in range(len(fpr1))]
    print(colors)


    for i in range(len(fpr1)-1):
        plt.fill(
            [fpr1[i],fpr2[i],fpr2[i+1],fpr1[i+1] ],
            [tpr1[i],tpr2[i],tpr2[i+1],tpr1[i+1] ],
            color=colors[i],lw=0)
        print(colors[i])


    plt.plot(fpr1, tpr1, "-", color='black', lw=2, label=r'$ee\rightarrow ZZ\rightarrow 4j$')
    plt.plot(fpr2, tpr2, "--", color='black', lw=2, label=r'$ee\rightarrow 3j$')

    highlightPoint = 8

    plt.annotate(r'$\epsilon_q=$'+f"{tpr1[highlightPoint]:0.2f}  ", xy=(fpr1[highlightPoint],tpr1[highlightPoint]), 
        xytext=(fpr1[highlightPoint]+0.15,tpr1[highlightPoint]),
                 arrowprops=dict(facecolor='black', arrowstyle='-',ls=":"),
                 fontsize=14, color='k',horizontalalignment='left',verticalalignment='center')

    plt.annotate(r'$\epsilon_q=$'+f"{tpr2[highlightPoint]:0.2f}  ", xy=(fpr2[highlightPoint],tpr2[highlightPoint]), 
        xytext=(fpr2[highlightPoint]+0.15,tpr2[highlightPoint]),
                 arrowprops=dict(facecolor='black', arrowstyle='-',ls=":"),
                 fontsize=14, color='k',horizontalalignment='left',verticalalignment='center')


    plt.plot([fpr1[highlightPoint],fpr2[highlightPoint]], [tpr1[highlightPoint],tpr2[highlightPoint]], "-o", color='k', lw=2,mew=2,mec="k",mfc="w",ms=7,zorder=100)
    # plt.plot([0, 1], [0, 1], color='black', lw=1, linestyle='-')

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])

    # plt.xscale('log')  # Set x-axis to log scale
    # plt.xlim(0.001, 1)  # Adjust x-axis limits accordingly

    plt.xlabel('Gluon Efficiency')
    plt.ylabel('Quark Efficiency')
    # plt.title(title)
    plt.legend(loc="lower right", fancybox=False, frameon=False, framealpha=0, shadow=True, borderpad=1,fontsize=14)

    plt.text(0.5, 0.4, f'Pythia 8.306\n'+r"$n_{90}$-based $q/g$ Tagger"+f'\n{ptrange} GeV Jets\n∆AUC: {AUC1-AUC2:0.2f}\nPointwise Distance: {euclideandistance:0.2f}', fontsize=14, color='black')
    # Save the plot as a PDF

    plt.tight_layout()  
    plt.savefig(output_filename, format='pdf')
    # plt.show()

if __name__ == "__main__":
    # Example data points (replace with your actual data)

    for ptrange in ["50-100","100-150","150-200","200-250"]:
        ZZdata = np.loadtxt(f'../output_csv/eeToZZtoJJ_{ptrange}-slice_run1.csv', delimiter=',')
        JJJdata = np.loadtxt(f'../output_csv/eeToJJJ_{ptrange}-slice_run1.csv', delimiter=',')

        fpr1 = ZZdata[0]
        tpr1 = JJJdata[1]
        fpr2 = JJJdata[0]
        tpr2 = JJJdata[1]

        # this is currently set up as a gluon tagger... (i.e. selecting jets with n90>cut). 

        fpr1 = 1-fpr1
        tpr1 = 1-tpr1
        fpr2 = 1-fpr2
        tpr2 = 1-tpr2

        print(fpr1,tpr1,fpr2,tpr2)

        plot_roc_curve(tpr1, fpr1, tpr2, fpr2, output_filename=f'roc_curve_{ptrange}.pdf')


