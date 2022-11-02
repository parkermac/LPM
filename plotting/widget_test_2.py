"""
More experimentation with widgets and ginput.

I think this is a failed experiment. There is too much conflict
between ginput and the widgets to be useful.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button

x = np.linspace(0,1,10)
y = x**2

plt.close('all')
fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(121)
ax.plot(x,y,'*g')
ax.grid(True)
ax.axis('square')

ax1 = fig.add_subplot(422)
ax2 = fig.add_subplot(424)
ax3 = fig.add_subplot(426)

b1 = TextBox(ax1, 'Type\nHere', initial='',
    color='.95', hovercolor='1', label_pad=0.03)
def f1(inp):
    print('TextBox = ' + inp)
b1.on_submit(f1)

b2 = Button(ax2, 'b2', color='.95', hovercolor='1')
def f2(c):
    print('Clicked b2')
b2.on_clicked(f2)

d = dict()
d['dd'] = True

b3 = Button(ax3, 'Stop Ginput', color='.95', hovercolor='1')
def f3(c):
    d['dd'] = False
b3.on_clicked(f3)

plt.show()

dd = True
while dd == True:
    a = plt.ginput(n=5, timeout=0)
    # a is a list of tuples
    x = []
    y = []
    for b in a:
        x.append(b[0])
        y.append(b[1])
    aa = ax1.axis()
    ax.plot(np.array(x), np.array(y),'*-g')
    ax.axis(aa)
    plt.draw()
    dd = d['dd']
    
