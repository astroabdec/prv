import numpy as np
from scipy import interpolate
from scipy.optimize import curve_fit
from numpy.polynomial.polynomial import polyval
import importlib as impl
import copy
import math
import glob, os
from astropy.io import fits
from specutils.spectra.spectrum1d import Spectrum1D
from specutils.fitting.continuum import fit_continuum
import astropy.units as u
import fnmatch
from astropy.modeling.polynomial import Chebyshev1D,Polynomial1D
from astropy.table import Table
import ccf530 as c5

"""
Making a stellar template for TOI-530 by shifting to stellar rest frame and take median (ignoring the tellurics).

Written by Sharon Xuesong Wang
2021.11.28
"""

# speed of whom?
c = 2.99792458e8


def shift_interp(obs, bc, twave):
    # Shift the observed spectral order according to BC and drizzle onto template wavelength scale

    owave = twave*(1.0 - bc/c)  # to observed wavelengths, note the sign of BC!
    tflux = np.empty(len(twave))
    mask = np.ones(len(twave))  # numerical mask, default to bad, 0 = False, good data, 1 = True, bad data
    tflux[:] = np.NaN  # default to NaN
    
    # what's the overlapping wavelength range that this can be done?
    minwave = np.max([np.nanmin(obs['wave']), np.nanmin(owave)])
    maxwave = np.min([np.nanmax(obs['wave']), np.nanmax(owave)])
    padding = 1  # chop off edge 
    wuse = np.where((owave < (maxwave - padding)) & (owave >= (minwave + padding)))[0]

    obs_interp = interpolate.interp1d(obs['wave'], obs['flux'], kind='cubic')
    tflux[wuse] = obs_interp(owave[wuse])

    maskn = obs['ivar'] < 0.1  # bad pixels have 0 ivars, recall ivar = photon counts
    mask_interp = interpolate.interp1d(obs['wave'], maskn*1.0, kind='linear')  # 1 is bad; use linear!
    mask[wuse] = mask_interp(owave[wuse]) > 0.5  # anything larger than 0.5 is bad

    return tflux, mask


def make_tfarr(obsmat, bcarr, iord, twave):
    # for a particular order, iord, make a stack of tflux array
    # the input obsmat is a list of obs list, i.e. a "matrix"

    tfarr = np.empty((len(obsmat), len(twave)))
    maarr = np.zeros((len(obsmat), len(twave)), dtype=bool)  # mask array, True = bad data
    
    for iobs in range(len(obsmat)):
        tflux, mask = shift_interp(obsmat[iobs][iord], bcarr[iobs], twave)
        tfarr[iobs,:] = tflux
        maarr[iobs,:] = mask

    return tfarr, maarr


def kick_nan(obs,iord,nanind):
    # kick out the NaNs from one order in an obs list
    thiswave = np.delete(obs[iord]['wave'], nanind)
    thisflux = np.delete(obs[iord]['flux'], nanind)
    thisivar = np.delete(obs[iord]['ivar'], nanind)
    thisobs = np.zeros(len(thiswave),dtype={'names': ('wave', 'flux', 'ivar'), 'formats': ('f8', 'f8', 'f8')})
    thisobs['wave'] = thiswave
    thisobs['flux'] = thisflux
    thisobs['ivar'] = thisivar

    return thisobs


def make_tpl(ofiles, ordarr, twarr, kicknan=False, cleannan=False):
    # master loop

    obsmat = []
    bcarr = []
    for ifile in range(len(ofiles)):
        obs,berv,bjd = c5.load_obs(ofiles[ifile], ordarr, telmask=np.zeros(1), cleannan=cleannan)
        for iord in range(len(obs)):
            nanind = np.where(np.isnan(obs[iord]['flux']))[0]
            if len(nanind) > 0:
                # first kick out the edges
                edgeind = np.concatenate((np.arange(500),-1*(np.arange(700)+1)))  # 500 on the left, 700 on the right
                obs[iord] = kick_nan(obs,iord,edgeind)
                nanind = np.where(np.isnan(obs[iord]['flux']))[0]
                if kicknan:  # Preserve a mask for the NaN values, but for now, just patch them up with 1; ivar < 1 => bad pixel NaN
                    obs[iord]['flux'][nanind] = 1.0
                    obs[iord]['ivar'][nanind] = 0.0
                else:  # patch up the NaNs with flux at continuum level with some added photon noise 
                    medflux = np.nanmedian(obs[iord]['ivar'])
                    randflux = np.random.poisson(medflux,size=len(nanind))/medflux
                    obs[iord]['flux'][nanind] = randflux
        # append all obs of this night
        obsmat.append(obs)
        bcarr.append(berv*1e3)

    tplarr = np.empty((len(ordarr),len(twarr[0])))
    maskarr = np.zeros((len(ordarr),len(twarr[0])), dtype=bool)  # all False by default. False is good.
    tplmat = []

    # looping through each order
    for i in range(len(twarr)):
        tfarr,maarr = make_tfarr(obsmat, bcarr, i, twarr[i])
        tplarr[i,:] = np.nanmedian(tfarr, axis=0)  # take a simple median!
        maskarr[i,:] = np.all(maarr, axis=0)  # Only True if all pixels are True, i.e. all NaNs and no flux info
        tplmat.append(tfarr)

    # into the same format that ccf530.py uses, with matching number of orders with ordarr
    tpl = []
    mod = np.zeros(len(twarr[0]),dtype={'names': ('wave', 'flux', 'mask'), 'formats': ('f8', 'f8', '?')})
    for i in range(49):  # 49 orders in total for SPIRou
        tpl.append(mod)
        for iord,ordid in enumerate(ordarr):
            if i == ordid:
                mod = np.zeros(len(twarr[iord]),dtype={'names': ('wave', 'flux', 'mask'), 'formats': ('f8', 'f8', '?')})
                mod['wave'] = twarr[iord]
                mod['flux'] = tplarr[iord,:]
                mod['mask'] = maskarr[iord,:]
                junk = tpl.pop(-1)
                tpl.append(mod)

    return tpl,twarr,tplarr,maskarr,tplmat



def make_tpl_telmask(ofiles, ordarr, twarr):
    # master loop
    # now masking the tellurics in the observation before combining into mask

    teltable = Table.read('telluric_mask_carm_short.dat', format='ascii')
    telwave=teltable['col1'][0:-2]/10.0  # in nm!

    obsmat = []
    bcarr = []
    for ifile in range(len(ofiles)):
        obs,berv,bjd = c5.load_obs(ofiles[ifile], ordarr, telmask=telwave, cleannan=False)
        obsmat.append(obs)
        bcarr.append(berv*1e3)

    tplarr = np.empty((len(ordarr),len(twarr[0])))
    tplmat = []
    
    for i in range(len(twarr)):
        tfarr = make_tfarr(obsmat, bcarr, i, twarr[i])
        tplarr[i,:] = np.nanmedian(tfarr, axis=0)  # take a simple median!
        tplmat.append(tfarr)

    # into the same format that ccf530.py uses
    tpl = []
    mod = np.zeros(len(twarr[0]),dtype={'names': ('wave', 'flux'), 'formats': ('f8', 'f8')})
    for i in range(49):  # 49 orders in total for SPIRou
        tpl.append(mod)
        for iord,ordid in enumerate(ordarr):
            if i == ordid:
                mod = np.zeros(len(twarr[iord]),dtype={'names': ('wave', 'flux'), 'formats': ('f8', 'f8')})
                mod['wave'] = twarr[iord]
                mod['flux'] = tplarr[iord,:]
                junk = tpl.pop(-1)
                tpl.append(mod)

    return tpl,twarr,tplarr,tplmat



if __name__ == "__main__":
    
    ordarr = np.array([28,29,30,31,32,33,34,35,36])

    # observational data
    odir = './SPIRou-data/zitao-processed/'
    ofiles = fnmatch.filter(os.listdir(odir),"*t.fits")
    ofiles = [odir+thisfile for thisfile in ofiles]

    # Use the same wavelength scale as SERVAL
    tfile = 'toi530.tpl.fits'
    stpl = c5.load_tpl(tfile,ordarr,telmask=np.zeros(1))
    twarrin = [stpl[i]['wave'] for i in range(len(stpl))]

    tpl,twarr,tplarr,tplmat = make_tpl_telmask(ofiles, ordarr, twarrin)

    np.savez('toi530-homemade-tpl-telmask.npz',tpl=tpl,twarr=twarr,tplarr=tplarr,tplmat=tplmat)
