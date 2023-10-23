"""
Code to generate the convex hull around a set of points (like all the gridpoints in a TEF segment)
and then figure out if a point is inside this polygon.

I suspect that we don't need to use methods from both scipy and matplotlib to do this.
"""

import matplotlib.pyplot as plt
import matplotlib.path as mpth
from scipy.spatial import ConvexHull
import numpy as np

# generate the points for the hull (Npoints,2)
rng = np.random.default_rng()
points = rng.random((30, 2))   # Npoints random points, zero to 1, in 2-D

# create the convex hull object
hull = ConvexHull(points)
# the hull.vertices are indices (Npoints) into points, which is copied as hull.points
chx = hull.points[hull.vertices,0]
chy = hull.points[hull.vertices,1]

# create path object from the convex hull from the hull array
path = mpth.Path(hull.points[hull.vertices,:])

# generate test points (npoints,2)
tp = np.array([[.25,.25],[.5,.5],[.5,1.5]])

# make Boolean array (npoints) of which are inside
isin = path.contains_points(tp)

# plotting
plt.close('all')

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(points[:,0],points[:,1],'.g')
ax.plot(chx,chy,'-g')
ax.plot([chx[0],chx[-1]],[chy[0],chy[-1]],'-g') # closing the hull, visually
ax.plot(tp[isin,0],tp[isin,1],'*r') # points inside the hull
ax.plot(tp[~isin,0],tp[~isin,1],'*b') # outside the hull

plt.show()