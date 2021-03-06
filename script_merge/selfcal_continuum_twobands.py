"""
*THIS IS JUST AN IMAGING SCRIPT*
Assumes selfcal_continuum has been run
"""

phasecenter='J2000 17:47:19.242 -28.23.33.22'
imsize=[4096,4096]

spw90 = "0,1,4,5,8,9,12,13,16,17,20,21,24,25,28,29,32,33,36,37,40,41"
spw100 = '2,3,6,7,10,11,14,15,18,19,22,23,26,27,30,31,34,35,38,39,42,43'

contvis = cont_merge_ms = combvis = 'SgrB2_ACA_TE_TC_contmerge.ms'

outname = 'SgrB2_nocal_TETC7m_continuum_90GHz'
os.system('rm -rf ' + outname + "*")
myimagebase = outname
tclean(vis=contvis,
       imagename=myimagebase,
       field='SgrB2',
       gridder='mosaic',
       spw=spw90,
       phasecenter=phasecenter,
       specmode="mfs",
       niter=100000,
       threshold="5.0mJy",
       deconvolver="clark",
       interactive=False,
       imsize=imsize,
       cell="0.125arcsec",
       outframe='LSRK',
       weighting="briggs",
       robust=0.5)
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.pb', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits', dropdeg=True, overwrite=True) # export the corrected image
exportfits(imagename=myimagebase+'.pb', fitsimage=myimagebase+'.pb.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.model', fitsimage=myimagebase+'.model.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.residual', fitsimage=myimagebase+'.residual.fits', dropdeg=True, overwrite=True) # export the PB image


outname = 'SgrB2_nocal_TETC7m_continuum_100GHz'
os.system('rm -rf ' + outname + "*")
myimagebase = outname
tclean(vis=contvis,
       imagename=myimagebase,
       field='SgrB2',
       gridder='mosaic',
       spw=spw100,
       phasecenter=phasecenter,
       specmode="mfs",
       niter=100000,
       threshold="5.0mJy",
       deconvolver="clark",
       interactive=False,
       imsize=imsize,
       cell="0.125arcsec",
       outframe='LSRK',
       weighting="briggs",
       robust=0.5)
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.pb', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits', dropdeg=True, overwrite=True) # export the corrected image
exportfits(imagename=myimagebase+'.pb', fitsimage=myimagebase+'.pb.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.model', fitsimage=myimagebase+'.model.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.residual', fitsimage=myimagebase+'.residual.fits', dropdeg=True, overwrite=True) # export the PB image





selfcal5vis = 'selfcal_SgrB2_TCTE7m_full_selfcal_iter5_ampphase.ms'

outname = 'SgrB2_selfcal_full_TETC7m_selfcal5_ampphase_continuum_90GHz'
os.system('rm -rf ' + outname + "*")
myimagebase = outname
tclean(vis=selfcal5vis,
       imagename=myimagebase,
       field='SgrB2',
       gridder='mosaic',
       spw=spw90,
       phasecenter=phasecenter,
       specmode="mfs",
       niter=100000,
       threshold="5.0mJy",
       deconvolver="clark",
       interactive=False,
       imsize=imsize,
       cell="0.125arcsec",
       outframe='LSRK',
       weighting="briggs",
       robust=0.5,
       savemodel='none')
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.pb', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits', dropdeg=True, overwrite=True) # export the corrected image
exportfits(imagename=myimagebase+'.pb', fitsimage=myimagebase+'.pb.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.model', fitsimage=myimagebase+'.model.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.residual', fitsimage=myimagebase+'.residual.fits', dropdeg=True, overwrite=True) # export the PB image


outname = 'SgrB2_selfcal_full_TETC7m_selfcal5_ampphase_continuum_100GHz'
os.system('rm -rf ' + outname + "*")
myimagebase = outname
tclean(vis=selfcal5vis,
       imagename=myimagebase,
       field='SgrB2',
       gridder='mosaic',
       spw=spw100,
       phasecenter=phasecenter,
       specmode="mfs",
       niter=100000,
       threshold="5.0mJy",
       deconvolver="clark",
       interactive=False,
       imsize=imsize,
       cell="0.125arcsec",
       outframe='LSRK',
       weighting="briggs",
       robust=0.5,
       savemodel='none')
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.pb', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits', dropdeg=True, overwrite=True) # export the corrected image
exportfits(imagename=myimagebase+'.pb', fitsimage=myimagebase+'.pb.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.model', fitsimage=myimagebase+'.model.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.residual', fitsimage=myimagebase+'.residual.fits', dropdeg=True, overwrite=True) # export the PB image







selfcal5vis = 'selfcal_SgrB2_TCTE7m_full_selfcal_iter5_ampphase.ms'

outname = 'SgrB2_selfcal_full_TETC7m_selfcal5_ampphase_continuum_90GHz_multiscale'
os.system('rm -rf ' + outname + "*")
myimagebase = outname
tclean(vis=selfcal5vis,
       imagename=myimagebase,
       field='SgrB2',
       gridder='mosaic',
       spw=spw90,
       phasecenter=phasecenter,
       specmode="mfs",
       niter=100000,
       threshold="5.0mJy",
       deconvolver="multiscale",
       scales=[0,4,12,36],
       interactive=False,
       imsize=imsize,
       cell="0.125arcsec",
       outframe='LSRK',
       weighting="briggs",
       robust=0.5,
       savemodel='none')
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.pb', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits', dropdeg=True, overwrite=True) # export the corrected image
exportfits(imagename=myimagebase+'.pb', fitsimage=myimagebase+'.pb.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.model', fitsimage=myimagebase+'.model.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.residual', fitsimage=myimagebase+'.residual.fits', dropdeg=True, overwrite=True) # export the PB image


outname = 'SgrB2_selfcal_full_TETC7m_selfcal5_ampphase_continuum_100GHz_multiscale'
os.system('rm -rf ' + outname + "*")
myimagebase = outname
tclean(vis=selfcal5vis,
       imagename=myimagebase,
       field='SgrB2',
       gridder='mosaic',
       spw=spw100,
       phasecenter=phasecenter,
       specmode="mfs",
       niter=100000,
       threshold="5.0mJy",
       deconvolver="multiscale",
       scales=[0,4,12,36],
       interactive=False,
       imsize=imsize,
       cell="0.125arcsec",
       outframe='LSRK',
       weighting="briggs",
       robust=0.5,
       savemodel='none')
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.pb', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits', dropdeg=True, overwrite=True) # export the corrected image
exportfits(imagename=myimagebase+'.pb', fitsimage=myimagebase+'.pb.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.model', fitsimage=myimagebase+'.model.fits', dropdeg=True, overwrite=True) # export the PB image
exportfits(imagename=myimagebase+'.residual', fitsimage=myimagebase+'.residual.fits', dropdeg=True, overwrite=True) # export the PB image
