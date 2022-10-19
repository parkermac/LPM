"""
Test of matplotlib.widgets
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

plt.close('all')
fig = plt.figure(figsize=(8,8))

x = np.linspace(0,1,10)
y = x**2

ax = fig.add_subplot(111)

fig.subplots_adjust(bottom=0.2)

ax.plot(x,y,'*g')
ax.grid(True)
ax.axis('square')

bbox = fig.add_axes([0.5, 0.05, 0.2, 0.075])

b = TextBox(bbox, 'Type\nHere', initial='', color='.95', hovercolor='1', label_pad=0.03)

c = {'a':'what'}

def submit(sname):
    h = ax.text(.05,.9,sname, transform=ax.transAxes)
    b.set_val('')
    c['a'] = 'why'
    plt.draw()

b.on_submit(submit)

plt.show()