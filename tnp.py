import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

orders = ["LO","NLO","NLO_only","NNLO","NNLO_only"]

obs = ["1mT","C","y23","HJM","WJB","TJB"]

all_cols = ["N2","N0","Nm2","NFN","NFNm1","NF2","stupid"]

LC_cols = ["N2","NFN","NF2"]

datadir = "data/epem3jet/"

data={}

for order in orders:
    data[order] = {}
    for ob in obs:
        data[order][ob]={}
        
        data[order][ob]['FC'] = pd.DataFrame()
        data[order][ob]['LC'] = pd.DataFrame()

        first = True
        firstLC = True

        for col in all_cols:
            data[order][ob][col] = pd.read_csv(datadir + order + "_NEW_" + col + "." + ob + ".dat", sep=r'\s+', comment='#', header=None, names=['xlow','xmid', 'xhigh','val','err'],dtype=float)
            if first:
                for n in ['xlow','xmid', 'xhigh','val','err']:
                    data[order][ob]['FC'][n] = data[order][ob][col][n]
                    first=False
            else:
                data[order][ob]['FC']["val"]=data[order][ob]['FC']["val"]+data[order][ob][col]["val"]
                data[order][ob]['FC']["err"]=np.sqrt(data[order][ob]['FC']["err"]**2+data[order][ob][col]["err"]**2)

            if col in LC_cols:
                if firstLC:
                    for n in ['xlow','xmid', 'xhigh','val','err']:
                        data[order][ob]['LC'][n] = data[order][ob][col][n]
                        firstLC=False
                else:
                    data[order][ob]['LC']["val"]=data[order][ob]['LC']["val"]+data[order][ob][col]["val"]
                    data[order][ob]['LC']["err"]=np.sqrt(data[order][ob]['LC']["err"]**2+data[order][ob][col]["err"]**2)

cols={"FC":"red","LC":"blue"}
    
with PdfPages("plots/epem3jet.pdf") as pdf:
    for ob in obs:
        fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(10,8),gridspec_kw={'height_ratios': [3, 1]})
        for ax in axes:
            ax.grid(alpha=0.2, linestyle=":", color="black")
        # axes[0].set_xlim([0.9,10.1])
        # axes[1].set_xscale('log')
        axes[1].set_yscale('log')

        axes[0].set_title(ob)

        bins = data["NNLO"][ob]['FC']["xmid"].values

        for col in ["LC","FC"]:
            axes[0].plot(bins, data["NNLO"][ob][col]["val"].values, label=col,color=cols[col],linestyle='None',marker='x')
            axes[0].errorbar(bins, data["NNLO"][ob][col]["val"].values, data["NNLO"][ob][col]["err"].values, ls="none", capsize=3,color=cols[col], linewidth=1)

        axes[0].legend(ncol=2)
        # axes[1].legend()
        axes[0].minorticks_on()

        pdf.savefig(bbox_inches='tight')
        plt.close()










