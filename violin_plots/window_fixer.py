import matplotlib.pyplot as plt
import pickle
import sys

def window_fixer(name,w,h):
    with open('saved_fig.pickle', 'rb') as f:
        fig = pickle.load(f)
    fig.set_size_inches((w,h))
    plt.savefig('plot_images/squished_'+ name +'.pdf',format="pdf", bbox_inches="tight")
    plt.close()

window_fixer("eeToJJJ_50k_1TeV_v_eeToZZToJJ_50k_1TeV_n90",int(sys.argv[1]),int(sys.argv[2]))
#window_fixer("new2")
