import numpy as np
from imf import imf
import paths
from astropy.table import Table
from astropy import coordinates
from astropy import units as u
import pyregion
import regions

core_phot_tbl = Table.read(paths.tpath("continuum_photometry_withSIMBAD.ipac"),
                           format='ascii.ipac')

core_powerlaw_index = 1.94

kroupa = imf.Kroupa()

o_mmin = 8
hii_cutoff = 20
mmax = 200
over8fraction = (kroupa.m_integrate(o_mmin, mmax)[0] /
                 kroupa.m_integrate(kroupa.mmin, mmax)[0])
# from wikipedia, median of power-law is well-defined for more slopes than the
# mean, but we're interested in the mean so I just compute that numerically
# below
over8median = 2**(1/(1.94-1)) * o_mmin

x = np.linspace(o_mmin,mmax,50000)
y = kroupa(x)
over8mean = (x*y).sum()/y.sum()

nsources = len(core_phot_tbl)

print("Mass fraction M>8 = {0}".format(over8fraction))
print("Mass of observed sources, assuming all are 8 msun = {0}".format(nsources*8))
print("Total Mass estimate if all sources are 8 msun = {0}".format(nsources*8/over8fraction))
print("Total Mass estimate if Mbar={1} = {0}".format(nsources*over8mean/over8fraction, over8mean))

# Comparison to Schmiedeke et al, 2016 tbl 2
clusters = regions.read_ds9(paths.rpath('schmiedeke_clusters.reg'))

# TODO: add in DePree HII regions based on whether or not their names
# are already in the table, since we didn't count the larger HII regions
hii_regions = regions.read_ds9(paths.rpath('SgrB2_1.3cm_hiiRegions_masked_Done.reg'))
for reg in hii_regions:
    if 'text' not in reg.meta:
        continue
    nm = reg.meta['text'].strip("{}")
    if nm not in core_phot_tbl['name']:
        core_phot_tbl.add_row({'name': nm, 'SIMBAD_OTYPE':'HII',
                               'RA': reg.center.ra[0],
                               'Dec': reg.center.dec[0]})
hii = core_phot_tbl['SIMBAD_OTYPE'] == 'HII'
core_coords = coordinates.SkyCoord(core_phot_tbl['RA'], core_phot_tbl['Dec'],
                                   frame='fk5')

# Mean of "cores"
x = np.linspace(o_mmin,hii_cutoff,50000)
y = kroupa(x)
over8lt20mean = (x*y).sum()/y.sum()
over8lt20fraction = (kroupa.m_integrate(o_mmin, hii_cutoff)[0] /
                     kroupa.m_integrate(kroupa.mmin, mmax)[0])
# Mean of "HII regions"
x = np.linspace(hii_cutoff,mmax,50000)
y = kroupa(x)
over20mean = (x*y).sum()/y.sum()
over20fraction = (kroupa.m_integrate(hii_cutoff, mmax)[0] /
                  kroupa.m_integrate(kroupa.mmin, mmax)[0])

for reg in clusters:
    mask = reg.contains(core_coords)
    nhii = (hii & mask).sum()
    ncores = ((~hii) & mask).sum()

    mass = ncores * over8lt20mean + nhii * over20mean
    inferred_mass = (ncores * over8lt20mean / over8lt20fraction +
                     nhii * over20mean / over20fraction)


    print("Cluster {0:4s}: N(cores)={1:3d} N(HII)={2:3d} counted mass={3:10.2f}"
          " inferred mass={4:10.2f}"
          .format(reg.meta['text'].strip("{}"), ncores, nhii, mass, inferred_mass))
