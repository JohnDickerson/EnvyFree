#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import matplotlib.patches as patches   # For the proxy twin-axis legend entry
from scipy.optimize import curve_fit

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

XFONT={'fontsize':24}
YFONT={'fontsize':24}
TITLEFONT={'fontsize':24}
TINYFONT={'fontsize':6}

def thm_2_func(x, a, b):
    return a * (x / np.log(x)) + b

def print_thm_2_func(vec):
    return "${0:.2f} * m/\ln(m) - {1:.2f}$".format(vec[0], -vec[1])

n = range(3,11)
# 99%+ percentage of runs were feasible after m=?
unif_m = [8,9,10,12,14,16,18,19]
corr_m = [8,10,11,13,14,16,18,19]

# Fit an   f(m) = O( m / ln(m) )  curve to the 99%+ data
popt_unif, pcov_unif = curve_fit(thm_2_func, n, unif_m)
popt_corr, pcov_corr = curve_fit(thm_2_func, n, corr_m)

print popt_unif
print popt_corr

fig = plt.figure()
ax = fig.add_subplot(111)

unif = ax.plot(n, unif_m, 'ks', label="Uniform", linewidth=2,)
corr = ax.plot(n, corr_m, 'ko', label="Correlated", linewidth=2,)
fit_unif = ax.plot(n, thm_2_func(n, *popt_unif), 'k--', label=print_thm_2_func(popt_unif))
fit_corr = ax.plot(n, thm_2_func(n, *popt_corr), 'k-', label=print_thm_2_func(popt_corr))

ax.set_ylabel("$m$", fontdict=XFONT)
ax.set_xlabel("$n$", fontdict=YFONT)
plt.legend(loc='upper left',)

plt.savefig("with_high_probability.pdf", format='pdf', bbox_inches='tight')
plt.clf()
