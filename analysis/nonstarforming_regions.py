import os
import copy
import warnings

import numpy as np
from astropy.io import fits
from astropy import units as u
from astropy import table
from astropy import coordinates
from astropy import wcs
from astropy.convolution import convolve_fft,Gaussian2DKernel
from astropy.utils.console import ProgressBar
import reproject
import pyregion
import radio_beam

warnings.filterwarnings('ignore', category=wcs.FITSFixedWarning, append=True)

import elmegreen2018
from constants import distance

import paths

datapath = '/Users/adam/work/sgrb2/alma/FITS/continuumdata'
colfilename = datapath+'/column_maps/scuba_col_herscheltem.fits'

colfile = fits.open(colfilename)[0]

sgrb2contfile = fits.open(paths.Fpath('merge/continuum/SgrB2_selfcal_full_TCTE7m_selfcal5_ampphase_taylorterms_multiscale_deeper_mask2.5mJy.image.tt0.pbcor.fits'))

tbl = table.Table.read(paths.tpath("continuum_photometry.ipac"), format='ascii.ipac',)

# Set the beam to be approximately the measured beam size
beam = radio_beam.Beam(11*u.arcsec)
beam_rad = beam.major.to(u.deg).value

observed_region,_ = reproject.reproject_interp(sgrb2contfile, colfile.header)

# make the WCS grid
yy,xx = np.indices(colfile.data.shape)
inds = np.transpose((xx.ravel(), yy.ravel()))
ra,dec = wcs.WCS(colfile.header).celestial.wcs_pix2world(inds, 0).T
ra = ra.reshape(xx.shape)
dec = dec.reshape(yy.shape)

nonstarforming_mask = np.isfinite(observed_region)

for row in ProgressBar(tbl):
    source_dist = ((ra-row['RA'])**2 + (dec-row['Dec'])**2)**0.5
    nonstarforming_mask[source_dist < beam_rad] = False

lo = 5e22
hi = 3e25
bins = np.logspace(np.log10(lo)-0.5, np.log10(hi), 100)

import pylab as pl
observed_mask = np.isfinite(observed_region)
pl.figure(1).clf()
H,L,P = pl.hist(colfile.data[observed_mask], bins=bins, log=True,
                alpha=0.5, color='k',
                linewidth=2,
                #normed=True,
                histtype='step')

H2,L2,P2 = pl.hist(colfile.data[nonstarforming_mask], bins=bins, log=True,
                   alpha=0.5, color='b', linewidth=2,
                   zorder=10,
                   #normed=True,
                   histtype='step')

H3,L3,P3 = pl.hist(colfile.data[observed_mask & ~nonstarforming_mask], bins=bins, log=True,
                   alpha=0.5, color='r',
                   zorder=-5,
                   linewidth=3,
                   linestyle='-',
                   #normed=True,
                   histtype='step')
pl.xscale('log')

pl.xlim(np.min([L.min(), L.min()]), L.max())
pl.xlim(lo,hi)
pl.ylim(0.5,np.max([H.max(), H.max()])*1.1)
pl.semilogx()
pl.yscale('log', nonposy='clip')
pl.xlabel("Column Density N(H$_2$) [cm$^{-2}$]")
pl.ylabel("Number of pixels")

ax1 = pl.gca()
ax2 = ax1.twiny()
print("ax1 xlims: {0}".format(ax1.get_xlim()))
pl.draw()
ax2.set_xlim(np.array(ax1.get_xlim())*(2.8*u.Da).to(u.g).value)
print("ax2 xlims: {0}".format(ax2.get_xlim()))
ax2.set_xscale('log')
ax2.set_xlabel("Column Density [g cm$^{-2}$]")
pl.draw()

pl.savefig(paths.fpath("column_density_distribution_with_and_without_SF.png"),
           bbox_inches='tight')
pl.savefig(paths.fpath("column_density_distribution_with_and_without_SF.pdf"),
           bbox_inches='tight')

ax3 = ax1.twinx()
midpts = (L[:-1] + L[1:])/2.
ax3.plot(midpts, H3/H, linestyle='-', color='k', linewidth=0.5, zorder=-21,)
ax1.set_xlim(lo,hi)
ax3.set_ylabel("Fraction of pixels with stars")

pl.savefig(paths.fpath("column_density_distribution_with_and_without_SF_withfraction.pdf"),
           bbox_inches='tight')

pl.figure(2).clf()
ax = pl.gca()
# this assumes a constant 1 pc thick slab (not a great assumption)
assumed_density = (midpts*u.cm**-2 / u.pc).to(u.cm**-3)

m0 = 1e6*u.M_sun
# this is the relation between Sigma and Rho for a rho~r^-2 collapse
assumed_density = ((midpts*2.8*u.Da*u.cm**-2)**1.5/(m0/(4*np.pi))**0.5/u.Da).to(u.cm**-3)

ax.semilogx(assumed_density, H3/H, linestyle='-', color='k', linewidth=0.5, zorder=-21,)
for Tstar in (5e4, 2e5, 4e5)*u.yr:
    r0 = 10*u.pc

    # using Diederik's fiducial #'s from Kruijssen+ 2014
    m0 = (200*u.M_sun/u.pc**2 * np.pi * r0**2)

    probs = [elmegreen2018.Pstar(rho, Tstar, m0, r0) for rho in assumed_density*2.8*u.Da]
    L, = pl.semilogx(u.Quantity(assumed_density), probs, linestyle='-',
                     label='$T_*={0:0.2f}$ Myr'.format(Tstar.to(u.Myr).value,))
    r0 = 5*u.pc
    assumed_density = ((midpts*2.8*u.Da*u.cm**-2)**1.5/(m0/(4*np.pi))**0.5/u.Da).to(u.cm**-3)
    probs = [elmegreen2018.Pstar(rho, Tstar, m0, r0) for rho in assumed_density*2.8*u.Da]
    pl.semilogx(u.Quantity(assumed_density), probs, linestyle='--',
                color=L.get_color())

    #m0 = 2e6*u.M_sun
    #probs = [elmegreen2018.Pstar(rho, Tstar, m0, r0) for rho in assumed_density*2.8*u.Da]
    #pl.semilogx(u.Quantity(assumed_density), probs, linestyle=':',
    #            color=L.get_color())

ax.set_ylabel("Fraction of pixels with stars")
ax.set_xlabel("(Crude estimate of) Density of H$_2$ [cm$^{-3}$]")
#ax.set_title("Pressureless Collapse of a 10 pc, 10$^6$ M$_\odot$ cloud")
pl.legend(loc='best', fontsize=14)
pl.savefig(paths.fpath("stellarfraction_with_elmegreen_overlays.pdf"),
           bbox_inches='tight')
