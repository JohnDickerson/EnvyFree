#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
from matplotlib.font_manager import FontProperties

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

XFONT={'fontsize':24}
YFONT={'fontsize':24}
TITLEFONT={'fontsize':24}
TINYFONT={'fontsize':6}

# Visualizes our correlated utility distribution
u_low, sigma_low = 0.4, 0.2
u_high, sigma_high = 0.6, 0.3
x = np.linspace(0,1,100)

fig = plt.figure()
ax = fig.add_subplot(111)

N=25
for delta in xrange(N):
    u = u_low + (float(delta)/(N-1))*(u_high-u_low)
    sigma = sigma_low + (float(delta)/(N-1))*(sigma_high-sigma_low)
    #ax.plot(x,mlab.normpdf(x, u, sigma))
    ax.fill(x,mlab.normpdf(x, u, sigma), 'r')

plt.savefig("utility_correlated.pdf", format='pdf', bbox_inches='tight')
plt.clf()
    
