#!/usr/bin/env python3

import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import uncbox.tnp as tnp

######################################
# Parameters

Nc=3
#basis = 0 #0: Bernstein, 1: Chebyshev
degree = 2 # Degree of the polynomial

#####################################
# Utility functions

def compute_ratio(df1, df2):
    """Compute the ratio of two dataframes with error propagation."""
    ratio = df1.copy()
    ratio['val'] = df1['val'] / df2['val']
    ratio['err'] = ratio['val'] * np.sqrt((df1['err']/df1['val'])**2 + (df2['err']/df2['val'])**2)
    return ratio

####################################
# Analysis specific variables

orders = ["LO","NLO","NLO_only","NNLO","NNLO_only"]
obs = ["1mT","C","y23","TJB"]
all_cols = ["N2","N0","Nm2","NFN","NFNm1","NF2","stupid"]
LC_cols = ["N2","NFN","NF2"]

datadir = "data/epem3jet/"
outputfile = "plots/epem3jet.pdf"

####################################
# Upload data as dataframe

data = {}
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


#######################################
# Print them as plots

cols={"FC":"red","LC":"blue"}
NORM = "LC"
fact = 1.0/Nc**2

#x_min = [0.05, 0.0, 0.0, 0.05]
#x_max = [0.40, 1.0, 0.4, 0.4]

with PdfPages(outputfile) as pdf:
    for ob in obs:
        fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(10,8),gridspec_kw={'height_ratios': [1, 1]})
        for ax in axes:
            ax.grid(alpha=0.2, linestyle=":", color="black")
        axes[0].set_ylim([0.7,1.3])
        #axes[0].set_xlim([ixmin, ixmax])
        axes[1].set_xlabel(ob)
        #axes[1].set_xscale('log')
        #axes[0].set_yscale('log')
        axes[1].set_ylim([0.7,1.3])
        axes[0].set_ylabel("Ratio to LC")
        axes[1].set_ylabel("Ratio to LC")
        axes[0].set_title(r'$e^+e- \rightarrow 3 \text{jets}$')

        bins = data["NNLO"][ob]['FC']["xmid"].values

        for col in ["LC","FC"]:
            #axes[0].plot(bins, data["NNLO"][ob][col]["val"].values, label=col,color=cols[col],linestyle='None',marker='x')
            #axes[0].errorbar(bins, data["NNLO"][ob][col]["val"].values, data["NNLO"][ob][col]["err"].values, ls="none", capsize=3,color=cols[col], linewidth=1)

            rat = compute_ratio(data["NNLO"][ob][col], data["NNLO"][ob][NORM])
            axes[0].plot(bins, rat["val"].values, label=col,color=cols[col],linestyle='None',marker='x')
            axes[0].errorbar(bins, rat["val"].values, rat["err"].values, ls="none", capsize=3,color=cols[col], linewidth=1)

            rat = compute_ratio(data["NNLO"][ob][col], data["NNLO"][ob][NORM])
            axes[1].plot(bins, rat["val"].values, label=col,color=cols[col],linestyle='None',marker='x')
            axes[1].errorbar(bins, rat["val"].values, rat["err"].values, ls="none", capsize=3,color=cols[col], linewidth=1)

        up0, down0 = tnp.compute_envelope(data["NNLO"][ob]['LC'], fact, degree=degree, basis=0)

        ratup = compute_ratio(up0, data["NNLO"][ob][NORM])
        ratdown = compute_ratio(down0, data["NNLO"][ob][NORM])
        axes[0].plot(bins, ratup["val"].values,color="green",linestyle='solid',marker='None', alpha=0.3)
        axes[0].plot(bins, ratdown["val"].values,color="green",linestyle='solid',marker='None', alpha=0.3)
        axes[0].fill_between(bins, ratdown["val"].values, ratup["val"].values, color="green", alpha=0.1)

        up1, down1 = tnp.compute_envelope(data["NNLO"][ob]['LC'], fact, degree=degree, basis=1)

        ratup = compute_ratio(up1, data["NNLO"][ob][NORM])
        ratdown = compute_ratio(down1, data["NNLO"][ob][NORM])
        axes[1].plot(bins, ratup["val"].values,color="purple",linestyle='solid',marker='None', alpha=0.3)
        axes[1].plot(bins, ratdown["val"].values,color="purple",linestyle='solid',marker='None', alpha=0.3)
        axes[1].fill_between(bins, ratdown["val"].values, ratup["val"].values, color="purple", alpha=0.1)

        axes[0].legend(ncol=2)

        axes[0].text(0.02, 0.05, "Bernstein (k=2)", transform=axes[0].transAxes, fontsize=12)
        axes[1].text(0.02, 0.05, "Chebyshev (k=2)", transform=axes[1].transAxes, fontsize=12)

        # axes[1].legend()
        axes[0].minorticks_on()

        pdf.savefig(bbox_inches='tight')
        plt.close()
