"""
Test of matplotlib.widgets.

The TextBox works fine, but the only way I could figure out to get the typed
value back to the main program scope was to change a dict entry. Weird.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

x = np.linspace(0,1,10)
y = x**2

plt.close('all')
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot(111)
fig.subplots_adjust(bottom=0.2)
ax.plot(x,y,'*g')
ax.grid(True)
ax.axis('square')
bbox = fig.add_axes([0.5, 0.05, 0.2, 0.075])
b = TextBox(bbox, 'Type\nHere', initial='', color='.95', hovercolor='1', label_pad=0.03)

c = {'typed_thing':'what'}

def submit(thing_you_type):
    if True:
        # Task 1: Update text printed on the plot based on what you type.

        # (i) Print what you type on the plot
        h = ax.text(.05,.9,thing_you_type, transform=ax.transAxes)

        b.set_val('')
        # (ii) This clears the TextBox when you hit return,
        # but it also clears the value stored in the dict.

        h.remove()
        # (iii) For some reason this accomplishes kind of what I was strugging to
        # accomplish. It removes the text on the plot as soon as you start
        # typing in the box AGAIN. I would have thought it would do it right
        # away, but it does not.

    else:
        # Task 2: Add what you type to the dict as soon as you hit return.
        c['typed_thing'] = thing_you_type

b.on_submit(submit)

plt.show()