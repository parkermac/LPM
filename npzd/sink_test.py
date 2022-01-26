"""
Code to develop and test the sinking algorithm.
"""
import numpy as np
import matplotlib.pyplot as plt

# z-coordinates (bottom to top, positive up)
H = 50 # max depth [m]
N = 25 # number of vertical grid cells
C = np.exp(-np.linspace(-2,2,N)**2)
Wsink = 80 # m per day
dt = .1 # time step in days

Dz = H/N
z_w = np.arange(-H,Dz,Dz)
z_rho = z_w[:-1] + Dz/2

def sink(z_w, z_rho, Dz, N, C, Wsink, dt):

    Next = 10
    NN = N + Next

    Cext = np.concatenate((C, np.zeros(Next)))
    Zwext = np.concatenate((z_w, np.arange(Dz,Next*Dz + Dz,Dz)))
    Zext = Zwext[:-1] + Dz/2
    for ii in range(NN):
        zbot = Zwext[ii]
        ztop = Zwext[ii+1]
        NB = 100
        dz = Dz/NB
        zb = np.arange(zbot,ztop,dz) + dz/2
        cb = np.ones(NB) * Cext[ii]
        if ii == 0:
            Zb = zb
            Cb = cb
        else:
            Zb = np.concatenate((Zb,zb))
            Cb = np.concatenate((Cb,cb))
        
    Zb_new = Zb - Wsink*dt

    ind = np.digitize(Zb_new, z_w, right=True)
    Cnew = np.zeros(N)
    for ii in range(N+1):
        mask = ind==ii
        Cnew[ii-1] = Cb[mask].mean()
        
    Cnet_old = Dz * np.sum(C)
    Cnet_new = Dz * np.sum(Cnew)
    Cnet_lost = Cnet_old - Cnet_new
        
    return Cnew, Cnet_old, Cnet_new, Cnet_lost, Cext, Zext, Cb, Zb, Zb_new
    
Cnew, Cnet_old, Cnet_new, Cnet_lost, Cext, Zext, Cb, Zb, Zb_new = sink(z_w, z_rho, Dz, N, C, Wsink, dt)
print('Cnet_old = %0.3f' % (Cnet_old))
print('Cnet_new = %0.3f' % (Cnet_new))
print('Cnet_lost = %0.3f' % (Cnet_lost))

plt.close('all')
fig = plt.figure(figsize=(12,12))
ax = fig.add_subplot(111)
ax.plot(Cext,Zext,'-og')
ax.plot(Cb,Zb,'-b')
ax.plot(Cb,Zb_new,'--b')
ax.plot(Cnew,z_rho,'-or')
plt.show()
