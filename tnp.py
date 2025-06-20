import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

Nc=3

def compute_ratio(df1, df2):
    """Compute the ratio of two dataframes with error propagation."""
    ratio = df1.copy()
    ratio['val'] = df1['val'] / df2['val']
    ratio['err'] = ratio['val'] * np.sqrt((df1['err']/df1['val'])**2 + (df2['err']/df2['val'])**2)
    return ratio

def bernstein(n, nu, x):
    return math.comb(n, nu) * (x ** nu) * ((1 - x) ** (n - nu))


def chebyshev(nu, x):
    return np.polynomial.chebyshev.Chebyshev.basis(nu)(x)

def tnp_func1(k, tnps, x):
    """Calculate the TNP function for a given degree k and tnps."""
    if k < 0 or k >= len(tnps):
        raise ValueError("k must be in the range [0, len(tnps)-1]")
    return sum(bernstein(k, nu, x) * tnps[nu] for nu in range(k + 1))

def compute_envelope(df,k=2):
    up=df.copy()
    down=df.copy()
    unc=df.copy()

    # unc['val'] = 1.0/Nc**2*abs(unc['val'])*np.sqrt(sum(bernstein(k, j, unc['xmid'])**2 for j in range(k+1)))
    unc['val'] = 1.0/Nc**2*abs(unc['val'])*np.sqrt(sum(chebyshev(j, unc['xmid'])**2 for j in range(k+1)))

    up['val'] = up['val'] + unc['val']
    down['val'] = down['val'] - unc['val']

    return up, down



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
NORM = "LC"
    
with PdfPages("plots/epem3jet.pdf") as pdf:
    for ob in obs:
        fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(10,8),gridspec_kw={'height_ratios': [1, 1]})
        for ax in axes:
            ax.grid(alpha=0.2, linestyle=":", color="black")
        # axes[0].set_xlim([0.9,10.1])
        # axes[1].set_xscale('log')
        axes[0].set_yscale('log')
        axes[1].set_ylim([0.8,1.2])

        axes[0].set_title(ob)

        bins = data["NNLO"][ob]['FC']["xmid"].values

        for col in ["LC","FC"]:
            axes[0].plot(bins, data["NNLO"][ob][col]["val"].values, label=col,color=cols[col],linestyle='None',marker='x')
            axes[0].errorbar(bins, data["NNLO"][ob][col]["val"].values, data["NNLO"][ob][col]["err"].values, ls="none", capsize=3,color=cols[col], linewidth=1)

            rat = compute_ratio(data["NNLO"][ob][col], data["NNLO"][ob][NORM])
            axes[1].plot(bins, rat["val"].values, label=col,color=cols[col],linestyle='None',marker='x')
            axes[1].errorbar(bins, rat["val"].values, rat["err"].values, ls="none", capsize=3,color=cols[col], linewidth=1)

        up, down = compute_envelope(data["NNLO"][ob]['LC'])
        axes[0].plot(bins, up["val"].values,color="green",linestyle='None',marker='x')
        axes[0].plot(bins, down["val"].values,color="green",linestyle='None',marker='x')

        ratup = compute_ratio(up, data["NNLO"][ob][NORM])
        ratdown = compute_ratio(down, data["NNLO"][ob][NORM])
        axes[1].plot(bins, ratup["val"].values,color="green",linestyle='None',marker='x')
        axes[1].plot(bins, ratdown["val"].values,color="green",linestyle='None',marker='x')

        axes[0].legend(ncol=2)
        # axes[1].legend()
        axes[0].minorticks_on()

        pdf.savefig(bbox_inches='tight')
        plt.close()










