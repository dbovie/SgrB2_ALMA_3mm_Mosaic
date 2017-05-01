import os
import copy

import numpy as np
from astropy.io import fits
from astropy import units as u
from astropy import table
from astropy import coordinates
from astropy import wcs
from astropy.convolution import convolve_fft,Gaussian2DKernel
import reproject
import pyregion

import paths

datapath = '/Users/adam/work/sgrb2/alma/continuumdata'

distance = 8.4*u.kpc
cara_higal_fit_scaling = 1e22


files = {"SHARC": {'wavelength': 350*u.um, 'bmarea':9.55e-10*u.sr, 'bunit':u.Jy, 'filename':'SgrB2_350um_gal.fits',},
         "ATLASGAL": {'wavelength': 870*u.um, 'bmarea':4.91e-9*u.sr, 'bunit':u.Jy, 'filename':'AG-Laboca-Planck.1.5.fits',},
         "SCUBA450": {'wavelength': 450*u.um, 'bmarea':7.59e-10*u.sr, 'bunit':u.Jy, 'filename':'gc450_gal_gal_zoom.fits',},
         "SCUBA850": {'wavelength': 850*u.um, 'bmarea':2.71e-9*u.sr, 'bunit':u.Jy, 'filename':'gc850_gal_gal_zoom.fits',},
         #"Herschel70": {'wavelength': 350*u.um, 'bmarea':10*u.arcsec**2, 'bunit':u.Jy, 'filename':'igls_l000_blue_cnr_hh_gal_zoom.fits',},
         #"Herschel160": {'wavelength': 350*u.um, 'bmarea':10*u.arcsec**2, 'bunit':u.Jy, 'filename':'igls_l000_red_cnr_hh_gal_zoom.fits',},
         "Herschel500": {'wavelength': 500*u.um, 'bmarea':1.72e-8*u.sr, 'bunit':u.MJy/u.sr, 'filename':'igls_l000_plw_deglitch_hh_gal_zoom.fits',},
         "Herschel350": {'wavelength': 350*u.um, 'bmarea':8.43e-9*u.sr, 'bunit':u.MJy/u.sr, 'filename':'igls_l000_pmw_deglitch_hh_gal_zoom.fits',},
         "Herschel250": {'wavelength': 250*u.um, 'bmarea':4.30*u.sr, 'bunit':u.MJy/u.sr, 'filename':'igls_l000_psw_deglitch_hh_gal_zoom.fits',},
         "BGPS": {'wavelength': 1100*u.um, 'bmarea':2.90e-8*u.sr, 'bunit':u.Jy, 'filename':'v2.1_ds2_l001_13pca_map20.fits',},
         "HerschelColumn25": {'wavelength': 0*u.um, 'bmarea':2.90e-8*u.sr, 'bunit':cara_higal_fit_scaling*u.cm**-2, 'filename':'gcmosaic_column_conv25.fits',},
         "HerschelColumn36": {'wavelength': 0*u.um, 'bmarea':2.90e-8*u.sr, 'bunit':cara_higal_fit_scaling*u.cm**-2, 'filename':'gcmosaic_column_conv36.fits',},
         "Sharc20Column": {'wavelength': 350*u.um, 'bmarea':2.90e-8*u.sr, 'bunit':u.cm**-2, 'filename':'column_maps/sharc_col_20K.fits',},
         "Sharc50Column": {'wavelength': 350*u.um, 'bmarea':2.90e-8*u.sr, 'bunit':u.cm**-2, 'filename':'column_maps/sharc_col_50K.fits',},
         "Scuba20Column": {'wavelength': 450*u.um, 'bmarea':2.90e-8*u.sr, 'bunit':u.cm**-2, 'filename':'column_maps/scuba_col_20K.fits',},
         "Scuba50Column": {'wavelength': 450*u.um, 'bmarea':2.90e-8*u.sr, 'bunit':u.cm**-2, 'filename':'column_maps/scuba_col_50K.fits',},
        }

"""
Goal:
    For each core in the core photometry catalog, determine the corresponding
    brightness in the above images, then put the core CDF on top of the
    brightness ("column") PDF.
"""

alma_hdr = fits.Header(dict(NAXIS=2,
                            NAXIS1=450,
                            NAXIS2=450,
                            CTYPE1='RA---SIN',
                            CRVAL1=2.668301750000E+02,
                            CDELT1=-0.0002777777777777778,
                            CRPIX1=225.0,
                            CUNIT1='deg     ',
                            CTYPE2='DEC--SIN',
                            CRVAL2=-2.839256111111E+01,
                            CDELT2=0.0002777777777777778,
                            CRPIX2=225.0,
                            CUNIT2='deg     ',)
                      )


tbl = table.Table.read(paths.tpath("continuum_photometry.ipac"), format='ascii.ipac',)

regfile = pyregion.open(paths.rpath('coverage.reg'))

for imname in files:
    print("Loading {0}".format(imname))
    tbl.add_column(table.Column(name=imname, data=np.zeros(len(tbl),
                                                           dtype='float'),
                                unit=files[imname]['bunit']))

    ffile = fits.open(os.path.join(datapath, files[imname]['filename']))
    new_data,_ = reproject.reproject_interp(ffile, alma_hdr)
    new_hdu = fits.PrimaryHDU(data=new_data, header=alma_hdr)

    files[imname]['file'] = new_hdu

    ww = wcs.WCS(files[imname]['file'].header)
    files[imname]['wcs'] = ww

    files[imname]['pixarea'] = (ww.wcs.cdelt[1]*u.deg)**2

    files[imname]['mask'] = regfile.get_mask(hdu=new_hdu)

    assert ww.naxis == 2

# Fix column around Sgr B2
col = files['HerschelColumn36']['file'].data
col_conv = convolve_fft(col, Gaussian2DKernel(5), interpolate_nan=True,
                        normalize_kernel=True)
files['HerschelColumn36']['file'].data[np.isnan(col)] = col_conv[np.isnan(col)]
files['HerschelColumn36']['file'].data *= cara_higal_fit_scaling
files['HerschelColumn36']['bunit'] = u.cm**-2

col = files['HerschelColumn25']['file'].data
col_conv = convolve_fft(col, Gaussian2DKernel(5), interpolate_nan=True,
                        normalize_kernel=True)
files['HerschelColumn25']['file'].data[np.isnan(col)] = col_conv[np.isnan(col)]
files['HerschelColumn25']['file'].data *= cara_higal_fit_scaling
files['HerschelColumn25']['bunit'] = u.cm**-2


for row in tbl:
    
    coord = coordinates.SkyCoord(row['RA'], row['Dec'], frame='fk5', unit=(u.deg, u.deg))

    for imname,fmeta in files.items():
        if 'GLON' in fmeta['wcs'].wcs.ctype[0]:
            xcrd, ycrd = fmeta['wcs'].wcs_world2pix(coord.galactic.l, coord.galactic.b, 0)
        elif fmeta['wcs'].wcs.equinox == 1950:
            xcrd, ycrd = fmeta['wcs'].wcs_world2pix(coord.fk4.ra, coord.fk4.dec, 0)
        else: # should always be this one now...
            xcrd, ycrd = fmeta['wcs'].wcs_world2pix(coord.ra, coord.dec, 0)

        # TODO: convert to K
        row[imname] = (fmeta['file'].data[int(ycrd), int(xcrd)] * fmeta['bunit']).value

tbl.write(paths.tpath("continuum_photometry_plusbackground.ipac"), format='ascii.ipac',
          overwrite=True)


brick_files = copy.deepcopy(files)
brick_hdr = fits.Header(dict(NAXIS=2,
                             NAXIS1=450,
                             NAXIS2=450,
                             CTYPE1='RA---SIN',
                             CRVAL1=266.5335253,
                             CDELT1=-0.0002777777777777778,
                             CRPIX1=225.0,
                             CUNIT1='deg     ',
                             CTYPE2='DEC--SIN',
                             CRVAL2=-28.70780832,
                             CDELT2=0.0002777777777777778,
                             CRPIX2=225.0,
                             CUNIT2='deg     ',)
                       )
brick_files['SHARC']['filename'] = 'SHARC_350_Dowell.fits'
brick_files['SCUBA450']['filename'] = 'gc450.fits.gz'
brick_files['SCUBA850']['filename'] = 'gc850.fits.gz'
brick_files['ATLASGAL']['filename'] = 'AG-Laboca-Planck.0.0.fits'
brick_files["Herschel500"]['filename'] = 'igls_l000_plw_deglitch_hh.fits'
brick_files["Herschel350"]['filename'] = 'igls_l000_pmw_deglitch_hh.fits'
brick_files["Herschel250"]['filename'] = 'igls_l000_psw_deglitch_hh.fits'
brick_files["BGPS"]['filename'] = 'v2.1_ds2_l000_13pca_map20_crop.fits'

for imname in brick_files:

    ffile = fits.open(os.path.join(datapath, brick_files[imname]['filename']))
    new_data,_ = reproject.reproject_interp(ffile, brick_hdr)
    new_hdu = fits.PrimaryHDU(data=new_data, header=brick_hdr)

    brick_files[imname]['file'] = new_hdu

    ww = wcs.WCS(brick_files[imname]['file'].header)
    brick_files[imname]['wcs'] = ww

brick_files['HerschelColumn25']['file'].data *= cara_higal_fit_scaling
brick_files['HerschelColumn25']['bunit'] = u.cm**-2
brick_files['HerschelColumn36']['file'].data *= cara_higal_fit_scaling
brick_files['HerschelColumn36']['bunit'] = u.cm**-2




def plotit():
    import astropy.stats
    import pylab as pl

    pl.figure(1).clf()
    pl.figure(2).clf()
    pl.figure(3).clf()
    pl.figure(4).clf()
    pl.figure(5).clf()
    for ii,imname in enumerate(f for f in files if 'column' in f.lower()):


        print(imname)
        data = files[imname]['file'].data
        mask = files[imname]['mask']
        brickdata = brick_files[imname]['file'].data
        # https://github.com/astropy/astropy/pull/5232 for ignore_nan
        lo = astropy.stats.mad_std(data, ignore_nan=True)
        hi = np.nanmax(data)
        bins = np.logspace(np.log10(lo), np.log10(hi), 100)

        pl.figure(1)
        pl.subplot(2,3,ii+1)
        brickweights = np.ones(np.isfinite(brickdata).sum(),
                               dtype='float')/np.isfinite(brickdata).sum()*np.isfinite(data).sum()
        bH,bL,bP = pl.hist(brickdata[np.isfinite(brickdata)], bins=bins,
                           log=True, alpha=0.5, histtype='step',
                           #weights=brickweights,
                           bottom=1.1,
                           color='b', zorder=-1)
        #weights = np.ones(np.isfinite(data).sum(), dtype='float')/np.isfinite(data).sum()
        H,L,P = pl.hist(data[np.isfinite(data) & mask], bins=bins, log=True,
                        alpha=0.5, color='k',
                        #normed=True,
                        histtype='step')
        # Lada threshold, approximately (116 Msun/pc^2)
        pl.vlines(5e21, 1.1, H.max())
        #pl.hist(tbl[imname], bins=bins, log=True, alpha=0.5)
        pl.xlim(np.min([bL.min(), L.min()]), L.max())
        pl.semilogx()
        pl.yscale('log', nonposy='clip')
        ax2 = pl.gca().twinx()
        ax2.plot(np.sort(tbl[imname]), np.arange(len(tbl),
                                                 dtype='float')/len(tbl),
                 'k-', linewidth=3, alpha=0.5, zorder=10)
        ax2.set_xlim(L.min(), L.max())
        ax2.set_ylim(0,1)
        pl.title(imname)

        pl.figure(2)
        pl.subplot(2,3,ii+1)
        pl.imshow(data, cmap='gray_r')
        pl.contour(data, levels=np.percentile(tbl[imname],[5,10,25,50,75,90,95]))
        pl.contour(mask, levels=[0.5])
        pl.title(imname)

        sorted_col = u.Quantity(np.sort(data[mask & (data>0)]), u.cm**-2)
        cumul = np.cumsum(sorted_col)[::-1]
        pixarea_cm2 = (files[imname]['pixarea']*distance**2)
        cum_mass = (cumul * pixarea_cm2 * 2.8*u.Da).to(u.M_sun, u.dimensionless_angles())
        pl.figure(3)
        pl.vlines(5e21, 0.5, 1e6, color='k', linestyle='--', linewidth=1)
        pl.plot(sorted_col, cum_mass, label=imname)
        pl.legend(loc='best')
        pl.xlim(1e21,2e25)
        pl.loglog()

        pl.figure(4)
        pl.vlines(5e21, 0.5, 1e6, color='k', linestyle='--', linewidth=1)
        pl.plot(sorted_col-5e22*u.cm**-2, cum_mass-(5e22*u.cm**-2*pixarea_cm2*2.8*u.Da).to(u.M_sun, u.dimensionless_angles()), label=imname)
        pl.legend(loc='best')
        pl.xlim(1e21,2e25)
        pl.loglog()

        pl.figure(5)
        pl.vlines(5e21, 0, 1, color='k', linestyle='--', linewidth=1)
        pl.plot(np.sort(tbl[imname]), np.arange(len(tbl),
                                                dtype='float')/len(tbl),
                linestyle='-', linewidth=3, alpha=0.5, zorder=10,
                label=imname,
               )
        pl.xscale('log')
        pl.xlim(1e21,2e25)
        pl.ylim(0,1)

    pl.figure(1)
    pl.tight_layout()
    pl.savefig(paths.fpath("flux_histograms_with_core_location_CDF.png"), bbox_inches='tight')


    pl.figure(3)
    pl.tight_layout()
    pl.savefig(paths.fpath("mass_cdf_histograms.png"), bbox_inches='tight')
    pl.figure(4)
    pl.tight_layout()
    pl.savefig(paths.fpath("mass_cdf_histograms_bgsubd.png"), bbox_inches='tight')

    pl.figure(5)
    pl.legend(loc='best')
    pl.tight_layout()
    pl.xlabel("Column Density $N(\mathrm{H}_2)$ (cm$^{-2}$)", fontsize=16)
    pl.ylabel("Cumulative fraction\nof cores at column $>N$", fontsize=16)
    pl.savefig(paths.fpath("core_background_column_cdf.png"), bbox_inches='tight')

    #pl.figure(3)
    #pl.tight_layout()
    #pl.savefig(paths.fpath("cumulative_mass_histograms.png"), bbox_inches='tight')




    # TODO: plot the same (?) histograms for The Brick
    # DONE!

if __name__ == "__main__":
    import matplotlib
    matplotlib.rcParams['figure.figsize'] = (12,8)
    matplotlib.rcParams['figure.dpi'] = 75.
    matplotlib.rcParams['savefig.dpi'] = 300.
    matplotlib.rcParams['axes.labelsize'] = 9
    matplotlib.rcParams['xtick.labelsize'] = 8
    matplotlib.rcParams['ytick.labelsize'] = 8
    matplotlib.use('Qt5Agg')
    import pylab as pl
    pl.ion()

    plotit()
