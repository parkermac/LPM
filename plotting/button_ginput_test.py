"""
Code to experiment with ginput and homemade buttons or other inputs
"""

import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0,1,10)
y = x**2

plt.close('all')
fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(121)
ax.plot(x,y,'*g')
ax.grid(True)
ax.axis('square')
aa = ax.axis()

plt.show()

inp = 'c'
while inp != 'x':
    inp = input('x=exit, g=ginput, n=name: ')
    if inp == 'g':
        ax.set_title('Make line (return to end)')
        plt.draw()
        a = plt.ginput(n=-1, timeout=0)
        # a is a list of tuples
        x = [b[0] for b in a]
        y = [b[1] for b in a]
        ax.plot(x,y,'*-g')
        ax.axis(aa)
        ax.set_title('Waiting for keyboard input')
        plt.draw()