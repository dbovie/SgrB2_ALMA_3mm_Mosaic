import numpy as np
from imf import imf
import paths
from astropy.table import Table,Column
from astropy import coordinates
from astropy import units as u
import regions
import latex_info

from astropy import wcs
from astropy.io import fits
# workaround for new regions API
arbitrary_wcs = wcs.WCS(fits.getheader(paths.Fpath('SgrB2_selfcal_TCTE7m_continuum_best.fits')))

core_phot_tbl = Table.read(paths.tpath("continuum_photometry_withSIMBAD.ipac"),
                           format='ascii.ipac')

# measured from core_flux_distributions
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

# we want the mean, not the median, which is not analytic (or at least it's
# easiest to compute numerically)
x = np.linspace(o_mmin,mmax,50000)
y = kroupa(x)
over8mean = (x*y).sum()/y.sum()

nsources = len(core_phot_tbl)

print("Mass fraction M>8 = {0}".format(over8fraction))
print("Mean mass Mbar(M>8) = {0}".format(over8mean))
print("Mass of observed sources, assuming all are 8 msun = {0}".format(nsources*8))
print("Total Mass estimate if all sources are 8 msun = {0}".format(nsources*8/over8fraction))
print("Total Mass estimate if Mbar={1} = {0}".format(nsources*over8mean/over8fraction, over8mean))

# Comparison to Schmiedeke et al, 2016 tbl 2
clusters = regions.read_ds9(paths.rpath('schmiedeke_clusters.reg'))
clusters.append(regions.CircleSkyRegion(clusters[0].center,
                                        radius=1*u.deg,
                                        meta={'text':'Total'})
               )

# add in DePree HII regions based on whether or not their names
# are already in the table, since we didn't count the larger HII regions
hii_regions = regions.read_ds9(paths.rpath('SgrB2_1.3cm_hiiRegions_masked_Done.reg'))
hii_regions = Table.read(paths.tpath("Schmiedeke2016_HIIregions_tableB1.txt"), format='ascii.fixed_width')
schmiedeke_dust_regions = Table.read(paths.tpath("Schmiedeke2016_dustsources_tableB2.txt"), format='ascii.fixed_width')
schmiedeke_summary_table = Table.read(paths.tpath("Schmiedeke2016_HIIregions_table2.txt"), format='ascii.fixed_width')

def obj_in_tbl(objname):
    for name in core_phot_tbl['name']:
        if str(objname).lower() in str(name).lower():
            return True
    return False


for row in hii_regions:
    #if 'text' not in reg.meta:
    #    continue
    #nm = reg.meta['text'].strip("{}")
    nm = row['ID']
    if (hasattr(nm,'mask') and nm.mask):
        print("Skipping row {0} because masked.".format(row))
    elif not obj_in_tbl(nm):
        if row['robs'] > 5:
            print("Skipping row {0} because it's too large".format(row))
            continue
        coord = coordinates.SkyCoord(row['RA'], row['Dec'], frame='fk5', unit=(u.hour, u.deg))
        core_phot_tbl.add_row({'name': nm, 'SIMBAD_OTYPE':'HII',
                               'RA': coord.ra,
                               'Dec': coord.dec,
                               'color': 'green',
                               'Muno_xray_ID': '-',
                               'Caswell_Name': '-',
                               #'Classification': 'HII',
                               #'RA': reg.center.ra[0],
                               #'Dec': reg.center.dec[0]
                              })
    else:
        print('{0} found in table'.format(nm))
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

tbl = Table(names=['Name', '$N(cores)$', '$N(H\\textsc{ii})$', '$M_{count}$',
                   '$M_{inferred}$', '$M_{inferred, H\\textsc{ii}}$',
                   '$M_{inferred, cores}$', '$M_{count}^s$', '$M_{inf}^s$',
                   'SFR'],
            dtype=['S10', int, int, int, int, int, int, int, int, float])

for col in tbl.colnames:
    if 'M' in col:
        tbl[col].unit = u.Msun
tbl['SFR'].unit = u.Msun/u.yr
sgrb2_age_myr = 0.74

cluster_column = np.array(['--']*len(core_phot_tbl))

print("Mass fraction M>20 = {0}".format(over20fraction))
print("Mean mass M>20 = {0}".format(over20mean))
print("Mass fraction 8<M<20 = {0}".format(over8lt20fraction))
print("Mean mass 8<M<20 = {0}".format(over8lt20mean))
for reg in clusters:
    mask = reg.contains(core_coords, arbitrary_wcs)
    nhii = (hii & mask).sum()
    ncores = ((~hii) & mask).sum()

    mass = ncores * over8lt20mean + nhii * over20mean
    # the fractions are fractions-of-total, so we're estimating the total mass
    # from each independent population assuming they're the same age
    hii_only_inferred_mass = nhii * over20mean / over20fraction
    core_inferred_mass = ncores * over8lt20mean / over8lt20fraction
    inferred_mass = (core_inferred_mass +
                     hii_only_inferred_mass) / 2.


    name = reg.meta['text'].strip("{}")
    print("Cluster {0:4s}: N(cores)={1:3d} N(HII)={2:3d} counted mass={3:10.2f}"
          " inferred mass={4:10.2f} HII-only inferred mass: {5:10.2f}"
          " core-inferred mass={6:10.2f}"
          .format(name, ncores, nhii, mass,
                  inferred_mass, hii_only_inferred_mass, core_inferred_mass))

    if name == 'Total':
        sst_mask = [-1]
    else:
        sst_mask = schmiedeke_summary_table['Name'] == 'Sgr B2({0})'.format(name)
        cluster_column[mask] = name

    tbl.add_row([name,
                 ncores,
                 nhii,
                 latex_info.round_to_n(mass,2)*u.M_sun,
                 latex_info.round_to_n(inferred_mass, 2)*u.M_sun,
                 latex_info.round_to_n(hii_only_inferred_mass, 2)*u.M_sun,
                 latex_info.round_to_n(core_inferred_mass, 2)*u.M_sun,
                 schmiedeke_summary_table[sst_mask]['M∗ initial']*u.M_sun,
                 schmiedeke_summary_table[sst_mask]['M∗ all']*1e3*u.M_sun,
                 latex_info.round_to_n(inferred_mass/sgrb2_age_myr/1e6,2)*u.M_sun/u.yr,
                ])



formats = {'SFR': lambda x: latex_info.strip_trailing_zeros(str(x))}

latexdict = latex_info.latexdict.copy()
latexdict['header_start'] = '\label{tab:clustermassestimates}'
latexdict['caption'] = 'Cluster Masses'
latexdict['preamble'] = '\centering'
latexdict['tablefoot'] = ("\par\n"
                          "$M_{{count}}$ is the mass of directly counted protostars, "
                          "assuming each millimeter source is {0:0.1f} \msun, or "
                          "{1:0.1f} \msun "
                          "if it is also an \hii region.  "
                          "$M_{{inferred,cores}}$ and $M_{{inferred,\hii}}$ are the inferred "
                          "total stellar masses assuming the counted objects represent "
                          "fractions of the total mass {2:0.2f} (cores) and "
                          "{3:0.2f} (\hii regions).  $M_{{inferred}}$ is the average "
                          "of these two.  "
                          "$M_{{count}}^s$ and $M_{{inf}}^s$ are the counted and inferred "
                          "masses reported in \citet{{Schmiedeke2016a}}.  "
                          "The star formation rate is computed using $M_{{inferred}}$ and"
                          " an age $t=0.74$ Myr, "
                          "which is the time of the last pericenter passage in the "
                          "\citet{{Kruijssen2015a}} model."
                          "  The \emph{{total}} column represents the total over the whole observed "
                          "region.  "
                          "  The clusters sum to much less "
                          "than the \emph{{total}} because the Deep South region is not included, "
                          "and it dominates the overall core count."
                          .format(over8lt20mean, over20mean, over8lt20fraction,
                                  over20fraction)
                         )
tbl.write(paths.texpath('cluster_mass_estimates.tex'), format='ascii.latex',
          formats=formats,
          latexdict=latexdict, overwrite=True)

core_phot_tbl.add_column(Column(name='Cluster', data=cluster_column))

classification = Column(name='Classification',
                        data=["{0}{1}{2}{3} {4}"
                              .format(('S' if row['color'] == 'green' else 'W'),
                                      ("\_" if row['Muno_xray_ID'] == '-' else "X"),
                                      ("\_" if row['Caswell_Name'] == '-' else "M"),
                                      ("\_" if np.isnan(row['McGrath_V_H2O']) else "W"),
                                      # would be nice... ("\_" if row['HII_name'] == '-' else "H"),
                                      str(row['SIMBAD_OTYPE']))
                              for row in core_phot_tbl])
core_phot_tbl.add_column(classification)

core_phot_tbl.write(paths.tpath("continuum_photometry_withSIMBAD_andclusters.ipac"),
                    format='ascii.ipac', overwrite=True)

# cutoff analysis...

for cutoff in np.linspace(8,70,10):
    x = np.linspace(cutoff,mmax,50000)
    y = kroupa(x)
    over20mean = (x*y).sum()/y.sum()
    over20fraction = (kroupa.m_integrate(cutoff, mmax)[0] /
                      kroupa.m_integrate(kroupa.mmin, mmax)[0])
    print("Mass fraction M>{1} = {0}".format(over20fraction, cutoff))
    print("Mean mass M>{1} = {0}".format(over20mean, cutoff))
    print("Represented mass M>{1} = {0}".format(over20mean/over20fraction, cutoff))



"""
Result as of 3/24/2017:
Cluster M   : N(cores)= 10 N(HII)= 37 counted mass=   1803.50 inferred mass=   6719.27 HII-only inferred mass:   12084.30 core-inferred mass=   1354.25
Cluster N   : N(cores)= 10 N(HII)=  4 counted mass=    301.72 inferred mass=   1330.33 HII-only inferred mass:    1306.41 core-inferred mass=   1354.25
Cluster NE  : N(cores)=  4 N(HII)=  0 counted mass=     47.87 inferred mass=    270.85 HII-only inferred mass:       0.00 core-inferred mass=    541.70
Cluster S   : N(cores)=  3 N(HII)=  1 counted mass=     81.41 inferred mass=    366.44 HII-only inferred mass:     326.60 core-inferred mass=    406.27

Updated 4/24/2017:
Cluster M   : N(cores)= 10 N(HII)= 55 counted mass=   2622.65 inferred mass=   9658.70 HII-only inferred mass:   17963.15 core-inferred mass=   1354.25
Cluster N   : N(cores)= 10 N(HII)=  7 counted mass=    438.24 inferred mass=   1820.23 HII-only inferred mass:    2286.22 core-inferred mass=   1354.25
Cluster NE  : N(cores)=  4 N(HII)=  0 counted mass=     47.87 inferred mass=    270.85 HII-only inferred mass:       0.00 core-inferred mass=    541.70
Cluster S   : N(cores)=  3 N(HII)=  1 counted mass=     81.41 inferred mass=    366.44 HII-only inferred mass:     326.60 core-inferred mass=    406.27


still missing 2 in NE, 5, in M, 1 in S, and have one too many in N
"""
