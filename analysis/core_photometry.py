import numpy as np

import regions
import radio_beam
from astropy import units as u
from astropy import log
from astropy import wcs
from astropy.stats import mad_std
from astropy.io import fits
from astropy.table import Table,Column

import paths
import masscalc

def photometry(data, mywcs, regs, beam):
    results = {}
    for ii,reg in enumerate(regs):
        if 'text' not in reg.meta:
            name = str(ii)
        else:
            name = reg.meta['text'].strip("{}")

        # all regions are points: convert them to 0.5" circles
        phot_reg = regions.CircleSkyRegion(center=reg.center, radius=0.5*u.arcsec)
        pixreg = phot_reg.to_pixel(mywcs)

        bgreg = regions.CircleSkyRegion(center=reg.center, radius=1.5*u.arcsec).to_pixel(mywcs)

        log.info(name)

        mask = pixreg.to_mask()
        cutout = mask.cutout(data) * mask.data

        # how do I make an annulus?
        bgmask = bgreg.to_mask()
        
        # manualannulus
        diff = bgmask.shape[0]-mask.shape[0]
        bgm = bgmask.data.astype('bool')
        bgm[int(diff/2):-int(diff/2), int(diff/2):-int(diff/2)] ^= mask.data.astype('bool')
        assert bgm.sum() == bgmask.data.sum() - mask.data.sum()

        bgcutout = bgmask.cutout(data) * bgm

        results[name] = {'peak': cutout.max(),
                         'sum': cutout.sum(),
                         'bgrms': bgcutout.std(),
                         'bgmad': mad_std(bgcutout),
                         'npix': mask.data.sum(),
                         'beam_area': beam.sr,
                         'RA': reg.center.ra[0],
                         'Dec': reg.center.dec[0],
                        }

    return results


if __name__ == "__main__":
    regs = regions.read_ds9(paths.rpath('sgrb2_cores_TE.reg'))

    contfnpath = paths.tmpath('te/SgrB2_selfcal_full_TE_selfcal4_ampphase.image.pbcor.fits')
    contfile = fits.open(contfnpath)
    data = contfile[0].data
    beam = radio_beam.Beam.from_fits_header(contfnpath)
    mywcs = wcs.WCS(contfile[0].header)

    units = {'peak':u.Jy/u.beam,
             'sum':u.Jy/u.beam,
             'npix':u.dimensionless_unscaled,
             'beam_area':u.sr,
             'peak_mass_20K':u.M_sun,
             'peak_col_20K':u.cm**-2,
             'RA': u.deg,
             'Dec': u.deg,
            }

    results = photometry(data, mywcs, regs, beam)

    fn_90GHz = paths.tmpath('SgrB2_nocal_TE_continuum_90GHz.image.pbcor.fits')
    results_90GHz = photometry(fits.getdata(fn_90GHz),
                               wcs.WCS(fits.getheader(fn_90GHz)), regs,
                               radio_beam.Beam.from_fits_header(fits.getheader(fn_90GHz)))
    fn_100GHz = paths.tmpath('SgrB2_nocal_TE_continuum_100GHz.image.pbcor.fits')
    results_100GHz = photometry(fits.getdata(fn_100GHz),
                               wcs.WCS(fits.getheader(fn_100GHz)), regs,
                               radio_beam.Beam.from_fits_header(fits.getheader(fn_100GHz)))

    for name in results:
        results[name]['peak_mass_20K'] = masscalc.mass_conversion_factor()*results[name]['peak']
        results[name]['peak_col_20K'] = masscalc.col_conversion_factor(results[name]['peak']*u.Jy, beam.sr)
        results[name]['peak_90GHz'] = results_90GHz[name]['peak']
        results[name]['peak_100GHz'] = results_100GHz[name]['peak']
        results[name]['sum_90GHz'] = results_90GHz[name]['sum']
        results[name]['sum_100GHz'] = results_100GHz[name]['sum']

    # invert the table to make it parseable by astropy...
    # (this shouldn't be necessary....)
    results_inv = {'name':{}}
    columns = {'name':[]}
    for k,v in results.items():
        results_inv['name'][k] = k
        columns['name'].append(k)
        for kk,vv in v.items():
            if kk in results_inv:
                results_inv[kk][k] = vv
                columns[kk].append(vv)
            else:
                results_inv[kk] = {k:vv}
                columns[kk] = [vv]

    for c in columns:
        if c in units:
            columns[c] = u.Quantity(columns[c], units[c])

    tbl = Table([Column(data=columns[k],
                        name=k)
                 for k in ['name', 'RA', 'Dec', 'peak', 'sum', 'npix', 'beam_area',
                           'peak_mass_20K', 'peak_col_20K']])

    peak_brightness = (tbl['peak']*u.beam).to(u.K,
                                              u.brightness_temperature(tbl['beam_area'],
                                                                       masscalc.centerfreq))
    tbl.add_column(Column(data=peak_brightness, name='peak_K', unit=u.K))

    tbl.sort('peak_mass_20K')
    tbl.write(paths.tpath("continuum_photometry.ipac"), format='ascii.ipac',
              overwrite=True)
