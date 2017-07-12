import numpy as np
from astropy import units as u
from astropy.table import Table, Column
from astropy import coordinates
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
Vizier.ROW_LIMIT = 10000

import paths

def stringy(x):
    if hasattr(x, 'astype'):
        return x.astype('str')
    else:
        return str(x)

cont_tbl = Table.read(paths.tpath('continuum_photometry.ipac'), format='ascii.ipac')

sgrb2_coords = coordinates.SkyCoord(cont_tbl['RA'], cont_tbl['Dec'],
                                    unit=(u.deg, u.deg), frame='fk5',)


simbad = Simbad()
simbad.add_votable_fields('otype')
simbad_results = simbad.query_region(sgrb2_coords.fk5, radius=0.5*u.arcsec)
simbad_coords = coordinates.SkyCoord(simbad_results['RA'],
                                     simbad_results['DEC'], frame='fk5',
                                     unit=(u.hour, u.deg))
matches = coordinates.match_coordinates_sky(sgrb2_coords, simbad_coords)

simbad_col_data = []
simbad_otype = []
for match,distance,_ in zip(*matches):
    if distance < 0.5*u.arcsec:
        simbad_col_data.append(simbad_results[match]['MAIN_ID'])
        simbad_otype.append(simbad_results[match]['OTYPE'])
    else:
        simbad_col_data.append("-")
        simbad_otype.append('-')

cont_tbl.add_column(Column(data=simbad_col_data, name='SIMBAD_ID'))
cont_tbl.add_column(Column(data=simbad_otype, name='SIMBAD_OTYPE'))

# HACK for broken SIMBAD
cont_tbl[np.where(cont_tbl['name'] == 'core_172_K2')[0][0]]['SIMBAD_ID'] = "NAME Sgr B2 HII K2"
cont_tbl[np.where(cont_tbl['name'] == 'core_172_K2')[0][0]]['SIMBAD_OTYPE'] = "HII"
cont_tbl[np.where(cont_tbl['name'] == 'core_176_f1')[0][0]]['SIMBAD_ID'] = "NAME Sgr B2 HII F1"
cont_tbl[np.where(cont_tbl['name'] == 'core_176_f1')[0][0]]['SIMBAD_OTYPE'] = "HII"
cont_tbl[np.where(cont_tbl['name'] == 'core_265_H')[0][0]]['SIMBAD_ID'] = "NAME Sgr B2 HII H"
cont_tbl[np.where(cont_tbl['name'] == 'core_265_H')[0][0]]['SIMBAD_OTYPE'] = "HII"
cont_tbl[np.where(cont_tbl['name'] == 'core_245_A2')[0][0]]['SIMBAD_ID'] = "NAME Sgr B2 HII A2"
cont_tbl[np.where(cont_tbl['name'] == 'core_245_A2')[0][0]]['SIMBAD_OTYPE'] = "HII"
cont_tbl[np.where(cont_tbl['name'] == 'core_182_Y')[0][0]]['SIMBAD_ID'] = "NAME Sgr B2 HII Y"
cont_tbl[np.where(cont_tbl['name'] == 'core_182_Y')[0][0]]['SIMBAD_OTYPE'] = "HII"
cont_tbl[np.where(cont_tbl['name'] == 'core_241_f10.30')[0][0]]['SIMBAD_ID'] = "[GCD95] F10.30"
cont_tbl[np.where(cont_tbl['name'] == 'core_241_f10.30')[0][0]]['SIMBAD_OTYPE'] = "HII"
cont_tbl[np.where(cont_tbl['name'] == 'core_242_f10.318')[0][0]]['SIMBAD_ID'] = "[GCD95] F10.318"
cont_tbl[np.where(cont_tbl['name'] == 'core_242_f10.318')[0][0]]['SIMBAD_OTYPE'] = "HII"

assert cont_tbl[cont_tbl['name'] == 'core_176_f1']['SIMBAD_OTYPE'] == "HII"

# query Methanol Multibeam Catalog (Caswell 2010: 2010MNRAS.404.1029C) for each source
caswell_maser_results = Vizier.query_region(sgrb2_coords.fk5, radius=2*u.arcsec, catalog='VIII/96/catalog')['VIII/96/catalog']
caswell_coords = coordinates.SkyCoord(stringy(caswell_maser_results['RAJ2000']),
                                      stringy(caswell_maser_results['DEJ2000']),
                                      frame='fk5', unit=(u.hour, u.deg))
caswell_matches = coordinates.match_coordinates_sky(sgrb2_coords, caswell_coords)

caswell_names = []
caswell_velos = []
caswell_matchdist = []
for match,distance,_ in zip(*caswell_matches):
    if distance < 1*u.arcsec:
        caswell_names.append(caswell_maser_results[match]['Name'])
        caswell_velos.append(caswell_maser_results[match]['VpkSC'])
        caswell_matchdist.append(distance.to(u.arcsec))
    else:
        caswell_names.append("-")
        caswell_velos.append(np.nan)
        caswell_matchdist.append(np.nan*u.arcsec)

cont_tbl.add_column(Column(data=caswell_names, name='Caswell_Name'))
cont_tbl.add_column(Column(data=caswell_velos, name='Caswell_V_CH3OH', unit=u.km/u.s))
cont_tbl.add_column(Column(data=u.Quantity(caswell_matchdist, u.arcsec), name='Caswell_matchdistance', unit=u.arcsec))



# query Methanol Multibeam Catalog (McGrath 2010: 2010MNRAS.404.1029C) for each source
McGrath_maser_results = Vizier.query_region(sgrb2_coords.fk5, radius=2*u.arcsec, catalog='J/ApJS/155/577/tables')['J/ApJS/155/577/tables']
McGrath_coords = coordinates.SkyCoord(stringy(McGrath_maser_results['_RA.icrs']),
                                      stringy(McGrath_maser_results['_DE.icrs']),
                                      frame='fk5', unit=(u.hour, u.deg))
McGrath_matches = coordinates.match_coordinates_sky(sgrb2_coords, McGrath_coords)

#McGrath_names = []
McGrath_velos = []
McGrath_matchdist = []
for match,distance,_ in zip(*McGrath_matches):
    if distance < 1*u.arcsec:
        #McGrath_names.append(McGrath_maser_results[match]['Name'])
        McGrath_velos.append(McGrath_maser_results[match]['VLSR'])
        McGrath_matchdist.append(distance.to(u.arcsec))
    else:
        #McGrath_names.append("-")
        McGrath_velos.append(np.nan)
        McGrath_matchdist.append(np.nan*u.arcsec)

#cont_tbl.add_column(Column(data=McGrath_names, name='McGrath_Name'))
cont_tbl.add_column(Column(data=McGrath_velos, name='McGrath_V_H2O', unit=u.km/u.s))
cont_tbl.add_column(Column(data=u.Quantity(McGrath_matchdist, u.arcsec), name='McGrath_matchdistance', unit=u.arcsec))






muno_xray_results = Vizier.query_region(sgrb2_coords.fk5, radius=2*u.arcsec,
                                        catalog='J/ApJS/165/173')['J/ApJS/165/173/table2']
muno_xray_coords = coordinates.SkyCoord(muno_xray_results['RAJ2000'],
                                        muno_xray_results['DEJ2000'],
                                        frame='fk5', unit=(u.deg, u.deg))
muno_xray_matches = coordinates.match_coordinates_sky(sgrb2_coords, muno_xray_coords)

muno_xray_names = []
muno_xray_countrates = []
muno_xray_matchdist = []
for match,distance,_ in zip(*muno_xray_matches):
    if distance < 1*u.arcsec:
        muno_xray_names.append(muno_xray_results[match]['CXOGC'])
        muno_xray_countrates.append(muno_xray_results[match]['Flux'])
        muno_xray_matchdist.append(distance.to(u.arcsec))
    else:
        muno_xray_names.append("-")
        muno_xray_countrates.append(np.nan)
        muno_xray_matchdist.append(np.nan*u.arcsec)

cont_tbl.add_column(Column(data=muno_xray_names, name='Muno_xray_ID'))
cont_tbl.add_column(Column(data=muno_xray_countrates, name='Muno_xray_Counts', unit=u.cm**-2*u.s**-1))
cont_tbl.add_column(Column(data=u.Quantity(muno_xray_matchdist, u.arcsec), name='Muno_xray_matchdistance', unit=u.arcsec))

# calculate local surface density per Gutermuth+ 2011 approach
nn11 = coordinates.match_coordinates_sky(sgrb2_coords, sgrb2_coords, nthneighbor=11)
cont_tbl.add_column(Column(data=nn11[1], name='nn11', description='11th nearest neighbor distance'))

cont_tbl.write(paths.tpath("continuum_photometry_withSIMBAD.ipac"), format='ascii.ipac',
               overwrite=True)
core_phot_tbl = cont_tbl






# match other catalogs to ours

caswell_in_field = Vizier.query_region(coordinates.SkyCoord('17:47:19.305', '-28:23:33.589', frame='fk5', unit=(u.hour, u.deg)),
                                       width=7.5*u.arcmin, height=7.5*u.arcmin, catalog='VIII/96/catalog')['VIII/96/catalog']
caswell_in_field_coords = coordinates.SkyCoord(stringy(caswell_in_field['RAJ2000']),
                                               stringy(caswell_in_field['DEJ2000']),
                                               frame='fk5', unit=(u.hour, u.deg))
caswell_in_field_matches = coordinates.match_coordinates_sky(caswell_in_field_coords, sgrb2_coords)
sgrb2_ids = []
sgrb2_dists = []
for match,distance,_ in zip(*caswell_in_field_matches):
    if distance < 2*u.arcsec:
        sgrb2_ids.append(cont_tbl[match]['name'])
        sgrb2_dists.append(distance.to(u.arcsec))
    else:
        sgrb2_ids.append("-")
        sgrb2_dists.append(np.nan*u.arcsec)
caswell_in_field.add_column(Column(data=sgrb2_ids, name='ALMA_ID'))
caswell_in_field.add_column(Column(data=u.Quantity(sgrb2_dists,u.arcsec), name='ALMA_dist', unit=u.arcsec))

with open(paths.rpath("caswell_masers_matches.reg"),'w') as fh:
    fh.write('fk5\n')
    for row in caswell_in_field:
        fh.write("point({0},{1}) # point=cross color=red text={{{2}}}\n"
                 .format(stringy(row['RAJ2000']).replace(" ",":"),
                         stringy(row['DEJ2000']).replace(" ",":"), row['ALMA_ID']))



muno_in_field = Vizier.query_region(coordinates.SkyCoord('17:47:19.305', '-28:23:33.589',
                                                         frame='fk5', unit=(u.hour, u.deg)),
                                    width=7.5*u.arcmin, height=7.5*u.arcmin,
                                    catalog='J/ApJS/165/173/table2')['J/ApJS/165/173/table2']
muno_in_field_coords = coordinates.SkyCoord(muno_in_field['RAJ2000'], muno_in_field['DEJ2000'], frame='fk5', unit=(u.deg, u.deg))
muno_in_field_matches = coordinates.match_coordinates_sky(muno_in_field_coords, sgrb2_coords)
sgrb2_ids = []
sgrb2_dists = []
for match,distance,_ in zip(*muno_in_field_matches):
    if distance < 2*u.arcsec:
        sgrb2_ids.append(cont_tbl[match]['name'])
        sgrb2_dists.append(distance.to(u.arcsec))
    else:
        sgrb2_ids.append("-")
        sgrb2_dists.append(np.nan*u.arcsec)
muno_in_field.add_column(Column(data=sgrb2_ids, name='ALMA_ID'))
muno_in_field.add_column(Column(data=u.Quantity(sgrb2_dists,u.arcsec), name='ALMA_dist', unit=u.arcsec))

with open(paths.rpath("muno_xrays_matches.reg"),'w') as fh:
    fh.write('fk5\n')
    for row in muno_in_field:
        fh.write("point({0},{1}) # point=cross color=red text={{{2}}}\n"
                 .format(stringy(row['RAJ2000']).replace(" ",":"),
                         stringy(row['DEJ2000']).replace(" ",":"), row['ALMA_ID']))
