"""
Initial test of the pyvista module.

Currently to run this you need to first do:

conda activate lodev

"""

import pyvista as pv
import numpy as np

import xarray as xr
from lo_tools import Lfun, zrfun, zfun
Ldir = Lfun.Lstart()
fn = Ldir['roms_out'] / 'cas6_v00_uu0mb' / 'f2021.07.04' / 'ocean_his_0025.nc'
ds = xr.open_dataset(fn)
G, S, T = zrfun.get_basic_info(fn)

# place for possible output
out_dir = Ldir['parent'] / 'LPM_output' / 'ploting'
Lfun.make_dir(out_dir)

# extract fields
lon = G['lon_rho']
lat = G['lat_rho']
Lon = lon[0,:]
Lat = lat[:,0]
z = -G['h']

# trim region
ix0 = zfun.find_nearest_ind(Lon,-127)
ix1 = zfun.find_nearest_ind(Lon,-122.2)
iy0 = zfun.find_nearest_ind(Lat,47)
iy1 = zfun.find_nearest_ind(Lat,50)
lon = lon[iy0:iy1, ix0:ix1]
lat = lat[iy0:iy1, ix0:ix1]
Lon = lon[0,:]
Lat = lat[:,0]
z = z[iy0:iy1, ix0:ix1]
m = G['mask_rho'][iy0:iy1, ix0:ix1]

# convert to km
x, y = zfun.ll2xy(lon, lat, Lon.mean(), Lat.mean())
xx = x/1000
yy = y/1000
zz = z/1000

NY, NX = xx.shape

# create mesh, scaling z
z_scale = 50
mesh = pv.StructuredGrid(xx, yy, z_scale*zz)


# more fields
vn = 'salt'; clim = (20,34)
vn = 'NO3'; clim = (0,45)
vn = 'oxygen'; clim = (0,350)

vv = ds[vn][0,-1,iy0:iy1,ix0:ix1].values
vv[m==0] = np.nan

vv_south = ds[vn][0,:,iy0,ix0:ix1].values
zr, zw = zrfun.get_z(-z, 0*z, S)
zz_south = zr[:,0,:]/1000
xx_south = xx[0,:] * np.ones((S['N']+2,1))
yy_south = yy[0,0] * np.ones(xx_south.shape)

vv_south = np.concatenate((vv_south[0,:].reshape(1,NX),
                            vv_south,
                            vv_south[-1,:].reshape(1,NX)),
                            axis=0)

zz_south = np.concatenate((zz[0,:].reshape(1,NX),
                            zz_south,
                            np.zeros((1,NX))),
                            axis=0)

mesh0 = pv.StructuredGrid(xx, yy, 0*zz)
mesh_south = pv.StructuredGrid(xx_south, yy_south, z_scale*zz_south)

# x = np.linspace(-10,10,100)
# y = x.copy()
# xx, yy = np.meshgrid(x, y)
# rr = np.sqrt(xx**2 + yy**2)
# zz = np.sin(rr)

mesh.point_data['bathy'] = zz.flatten(order='F')
mesh0.point_data[vn] = vv.flatten(order='F')
mesh_south.point_data['south'] = vv_south.flatten(order='F')

#
pl = pv.Plotter()
pl.add_mesh(mesh, scalars='bathy', show_scalar_bar=False,
    cmap='cividis', clim=(-2,1))
opacity = 1
pl.add_mesh(mesh0, scalars=vn, show_scalar_bar=True,
    cmap='jet', clim=clim, opacity=opacity, edge_color='w')
pl.add_mesh(mesh_south, scalars='south', show_scalar_bar=False,
    cmap='jet', clim=clim, opacity=opacity, edge_color='w')
    
pl.set_position([100,-600,600])

pl.export_html(out_dir / 'pyvista_test.html')

cpos = [(-392.30296709989165, -882.0513995416103, 579.9729707235836),
 (-32.98573967703153, 18.426810850776647, -39.115092906496244),
 (0.028556084552702893, 0.5585411242944357, 0.8289851401001869)]
# use return_cpos=True to return camper position
# other choices are like cpos='xy' (flat map view)
pl.show(window_size=(1500,1500))#, cpos=cpos)




