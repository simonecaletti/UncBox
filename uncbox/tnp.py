#!/usr/bin/env python3

import math
import numpy as np

##############################################
#  Class of polynomial basis

def bernstein(n, nu, x):
    return math.comb(n, nu) * (x ** nu) * ((1 - x) ** (n - nu))

def chebyshev(nu, x):
    return np.polynomial.chebyshev.Chebyshev.basis(nu)(x)

#############################################
# TNP function

def TNP(k, params, x, basis=0):
    """Calculate the TNP function for a given degree k and tnps."""
    """0: Bernstein basis, 1: Chebyshev basis"""
    if k < 0 or k >= len(tnps):
        raise ValueError("k must be in the range [0, len(tnps)-1]")
    if basis==0:
        return sum(bernstein(k, nu, x) * tnps[nu] for nu in range(k + 1))
    elif basis==1:
        return sum(chebyshev(nu, x) * tnps[nu] for nu in range(k + 1))
    else:
        raise ValueError("basis must be 0 or 1")

#############################################
# Uncertainity bar

def compute_envelope(df, fact, degree=2, basis=0):
    up=df.copy()
    down=df.copy()
    unc=df.copy()

    if basis==0:
        unc['val'] = fact*abs(unc['val'])*np.sqrt(sum(bernstein(degree, j, unc['xmid'])**2 for j in range(degree+1)))
    elif basis==1:
        unc['val'] = fact*abs(unc['val'])*np.sqrt(sum(chebyshev(j, unc['xmid'])**2 for j in range(degree+1)))
    else:
        raise ValueError("basis must be 0 or 1")

    up['val'] = up['val'] + unc['val']
    down['val'] = down['val'] - unc['val']

    return up, down
