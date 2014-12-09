from astropy import units as u
import ds9
from spectral_cube import SpectralCube

files = [
    "SgrB2_a_03_7M.CH3CN_5-4_3.image.pbcor.fits",
    "SgrB2_a_03_7M.H2CO615-616.image.pbcor.fits",
    "SgrB2_a_03_7M.H2CS303-202.image.pbcor.fits",
    "SgrB2_a_03_7M.H2CS321-220.image.pbcor.fits",
    "SgrB2_a_03_7M.H41a.image.pbcor.fits",
    "SgrB2_a_03_7M.HC3N.image.pbcor.fits",
    "SgrB2_a_03_7M.HCN.image.pbcor.fits",
    "SgrB2_a_03_7M.HCOp.image.pbcor.fits",
    "SgrB2_a_03_7M.HNC.image.pbcor.fits",
]

dd = ds9.ds9()

vrange = [-95, 135]*u.km/u.s

for fn in files:
    species = fn.split(".")[1]
    if 'CH3CN' in species:
        rest_value = 91987.094*u.MHz
    else:
        rest_value = None
    cube = SpectralCube.read(fn).with_spectral_unit(u.km/u.s, rest_value=rest_value,
                                                    velocity_convention='radio').spectral_slab(vrange[0],
                                                                                               vrange[1])
    cube.to_ds9(dd.id, newframe=True)
    dd.set('wcs append', "OBJECT  = '{0}'".format(species))
    print cube

dd.set('tile yes')
dd.set('frame frameno 1')
dd.set('frame delete')
dd.set('scale limits -0.5 2')
dd.set('wcs fk5')
dd.set('lock frame wcs')
dd.set('lock slice image')
dd.set('lock scale yes')
dd.set('lock color yes')


#SgrB2_a_03_7M.lowres.spw0.image.pbcor.fits
#SgrB2_a_03_7M.lowres.spw1.image.pbcor.fits
#SgrB2_a_03_7M.lowres.spw2.image.pbcor.fits
#SgrB2_a_03_7M.lowres.spw3.image.pbcor.fits
