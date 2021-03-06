# ALMA Data Reduction Script

# Calibration

thesteps = []
step_title = {0: 'Import of the ASDM',
              1: 'Fix of SYSCAL table times',
              2: 'listobs',
              3: 'A priori flagging',
              4: 'Generation and time averaging of the WVR cal table',
              5: 'Generation of the Tsys cal table',
              6: 'Generation of the antenna position cal table',
              7: 'Application of the WVR, Tsys and antpos cal tables',
              8: 'Split out science SPWs and time average',
              9: 'Listobs, clear pointing table, and save original flags',
              10: 'Initial flagging',
              11: 'Putting a model for the flux calibrator(s)',
              12: 'Save flags before bandpass cal',
              13: 'Bandpass calibration',
              14: 'Save flags before gain cal',
              15: 'Gain calibration',
              16: 'Save flags before applycal',
              17: 'Application of the bandpass and gain cal tables',
              18: 'Split out corrected column',
              19: 'Save flags after applycal'}

if 'applyonly' not in globals(): applyonly = False
try:
  print 'List of steps to be executed ...', mysteps
  thesteps = mysteps
except:
  print 'global variable mysteps not set.'
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print 'Executing all steps: ', thesteps

# The Python variable 'mysteps' will control which steps
# are executed when you start the script using
#   execfile('scriptForCalibration.py')
# e.g. setting
#   mysteps = [2,3,4]# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.

import re

import os

if applyonly != True: es = aU.stuffForScienceDataReduction() 


#if re.search('^4.3.1', casadef.casa_version) == None:
# sys.exit('ERROR: PLEASE USE THE SAME VERSION OF CASA THAT YOU USED FOR GENERATING THE SCRIPT: 4.3.1')


# CALIBRATE_AMPLI: J1733-130
# CALIBRATE_ATMOSPHERE: J1733-130,J1733-1304,SgrB2
# CALIBRATE_BANDPASS: J1733-1304
# CALIBRATE_FLUX: J1733-130
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J1752-2956
# CALIBRATE_POINTING: J1733-1304
# OBSERVE_TARGET: SgrB2

# Using reference antenna = DA64

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_X9cffbd_Xefe.ms') == False:
    importasdm('uid___A002_X9cffbd_Xefe', asis='Antenna Station Receiver Source CalAtmosphere CalWVR', bdfflags=True, lazy=False)
  if applyonly != True: es.fixForCSV2555('uid___A002_X9cffbd_Xefe.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_X9cffbd_Xefe.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.listobs')
  listobs(vis = 'uid___A002_X9cffbd_Xefe.ms',
    listfile = 'uid___A002_X9cffbd_Xefe.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_X9cffbd_Xefe.ms',
    mode = 'manual',
    spw = '1~24',
    autocorr = T,
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_X9cffbd_Xefe.ms',
    mode = 'manual',
    intent = '*POINTING*,*SIDEBAND_RATIO*,*ATMOSPHERE*',
    flagbackup = F)
  
  flagcmd(vis = 'uid___A002_X9cffbd_Xefe.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_X9cffbd_Xefe.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_X9cffbd_Xefe.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.wvr') 
  
  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X9cffbd_Xefe.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_X9cffbd_Xefe.ms',
    caltable = 'uid___A002_X9cffbd_Xefe.ms.wvr',
    spw = [17, 19, 21, 23],
    smooth = '6.048s',
    toffset = 0,
    tie = ['SgrB2,J1752-2956'],
    statsource = 'SgrB2')
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_X9cffbd_Xefe.ms.wvr', spw='17', antenna='DA64',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_X9cffbd_Xefe.ms.wvr.plots/uid___A002_X9cffbd_Xefe.ms.wvr') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.tsys') 
  gencal(vis = 'uid___A002_X9cffbd_Xefe.ms',
    caltable = 'uid___A002_X9cffbd_Xefe.ms.tsys',
    caltype = 'tsys')
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_X9cffbd_Xefe.ms.tsys',
    mode = 'manual',
    spw = '9:0~3;124~127,11:0~3;124~127,13:0~3;124~127,15:0~3;124~127',
    flagbackup = F)
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_X9cffbd_Xefe.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='92.1875%',showfdm=True, showBasebandNumber=True, 
    field='', figfile='uid___A002_X9cffbd_Xefe.ms.tsys.plots.overlayTime/uid___A002_X9cffbd_Xefe.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_X9cffbd_Xefe.ms.tsys', msName='uid___A002_X9cffbd_Xefe.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Position for antenna DV12 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DV19 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DA64 is derived from baseline run made on 2015-01-13 02:43:15.
  
  # Note: the correction for antenna DA49 is larger than 2mm.
  
  # Position for antenna DA49 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DA48 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DA61 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DA60 is derived from baseline run made on 2015-01-13 02:43:15.
  
  # Position for antenna DA45 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DA44 is derived from baseline run made on 2014-07-16 01:18:10.
  
  # Position for antenna DA47 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DA46 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DA41 is derived from baseline run made on 2015-01-13 02:43:15.
  
  # Position for antenna DV22 is derived from baseline run made on 2015-01-13 02:43:15.
  
  # Position for antenna DV17 is derived from baseline run made on 2015-01-13 02:43:15.
  
  # Position for antenna DA63 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DA62 is derived from baseline run made on 2015-01-13 02:43:15.
  
  # Position for antenna PM02 is derived from baseline run made on 2015-01-13 02:43:15.
  
  # Position for antenna PM04 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DV11 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DV10 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DV13 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Note: the correction for antenna DA52 is larger than 2mm.
  
  # Position for antenna DA52 is derived from baseline run made on 2015-01-13 02:43:15.
  
  # Position for antenna DA50 is derived from baseline run made on 2014-12-02 07:19:25.
  
  # Position for antenna DA51 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DA57 is derived from baseline run made on 2015-01-13 02:43:15.
  
  # Position for antenna DA54 is derived from baseline run made on 2015-01-13 02:43:15.
  
  # Position for antenna DA59 is derived from baseline run made on 2014-12-21 05:53:17.
  
  # Position for antenna DV20 is derived from baseline run made on 2015-01-13 02:43:15.
  
  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.antpos') 
  gencal(vis = 'uid___A002_X9cffbd_Xefe.ms',
    caltable = 'uid___A002_X9cffbd_Xefe.ms.antpos',
    caltype = 'antpos',
    antenna = 'DV19,DV20,DA64,DA49,DA48,DA61,DA60,DA45,DA44,DA47,DV12,DA41,DA50,DV17,DA51,DA63,DA62,PM02,PM04,DV11,DV10,DV13,DA52,DV22,DA46,DA57,DA54,DA59',
    parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
  #  parameter = [0.000763224595131,-0.000872836862611,-0.00100151686389,0.000449148240922,-0.00121965529975,-0.000785080128059,0.000376327428967,-0.00146782677621,-0.00112532451749,0.000575381331146,-0.00161136779934,-0.00117099285126,0.00057431604709,-0.0011954347568,-0.000936748536314,0.000350542975176,-0.00136158594062,-0.00102771511075,-9.88165859491e-05,2.23514060329e-05,0.000206892960223,0.000471355393529,-0.00119987875223,-0.000884058885276,-0.000277784435574,0.000264455628235,-9.86561100355e-05,0.000228956807405,-0.000833646394312,-0.000312126707286,0.000500225694647,-0.000744895727704,-0.000412322215341,0.000407614279538,-0.00108007155359,-0.000530316960067,-0.000144578050822,-0.000582538545132,-0.000986936502159,0.000469437917569,-0.000701300406205,-0.000656311497542,0.000748454127461,-0.00149133522063,-0.000856994651258,0.000555722791109,-0.00126095405742,-0.000843223602917,0.000670030074481,-0.00150872308554,-0.000943140154195,0.000429643783718,-0.00154094118625,-0.000735029578209,0.000426281282526,-0.00140672852102,-0.00109221844716,0.00037343815848,-0.0013356736041,-0.000845442467062,0.000297389547474,-0.00103880338778,-0.000898549931055,0.000550707336515,-0.000622102059424,-0.000776093453169,0.000671388117899,-0.00192410811043,-0.0012088027029,0.000599960339188,-0.000518520008632,-0.000752280261638,0.000566912652314,-0.000942276669298,-0.00089417600233,0.000514037961512,-0.00116958478532,-0.000836663256079,0.000382543263633,-0.00130245732194,-0.00111832579152,0.000584799989147,-0.00144563166359,-0.00100361699165])
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_X9cffbd_Xefe.ms', tsystable = 'uid___A002_X9cffbd_Xefe.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_X9cffbd_Xefe.ms',
    field = '0',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_X9cffbd_Xefe.ms.tsys', 'uid___A002_X9cffbd_Xefe.ms.wvr', 'uid___A002_X9cffbd_Xefe.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X9cffbd_Xefe.ms',
    field = '1',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_X9cffbd_Xefe.ms.tsys', 'uid___A002_X9cffbd_Xefe.ms.wvr', 'uid___A002_X9cffbd_Xefe.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  # Note: J1752-2956 didn't have any Tsys measurement, so I used the one made on SgrB2. This is probably Ok.
  
  applycal(vis = 'uid___A002_X9cffbd_Xefe.ms',
    field = '2',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_X9cffbd_Xefe.ms.tsys', 'uid___A002_X9cffbd_Xefe.ms.wvr', 'uid___A002_X9cffbd_Xefe.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X9cffbd_Xefe.ms',
    field = '3~151',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_X9cffbd_Xefe.ms.tsys', 'uid___A002_X9cffbd_Xefe.ms.wvr', 'uid___A002_X9cffbd_Xefe.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  if applyonly != True: es.getCalWeightStats('uid___A002_X9cffbd_Xefe.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split') 
  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.flagversions') 
  split(vis = 'uid___A002_X9cffbd_Xefe.ms',
    outputvis = 'uid___A002_X9cffbd_Xefe.ms.split',
    datacolumn = 'corrected',
    spw = '17,19,21,23',
    keepflags = T)
  
  

print "# Calibration"

# Listobs, clear pointing table, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.listobs')
  listobs(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    listfile = 'uid___A002_X9cffbd_Xefe.ms.split.listobs')
  
  tb.open('uid___A002_X9cffbd_Xefe.ms.split/POINTING', nomodify = False)
  a = tb.rownumbers()
  tb.removerows(a)
  tb.close()
  
  if not os.path.exists('uid___A002_X9cffbd_Xefe.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    mode = 'shadow',
    flagbackup = F)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  setjy(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    standard = 'manual',
    field = 'J1733-130',
    fluxdensity = [2.38665110647, 0, 0, 0],
    spix = -0.70102947456,
    reffreq = '96.3504906483GHz')
  
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    caltable = 'uid___A002_X9cffbd_Xefe.ms.split.ap_pre_bandpass',
    field = '0', # J1733-1304
    spw = '0:3072~4608,1:3072~4608,2:3072~4608,3:3072~4608',
    scan = '1,2,4',
    solint = 'int',
    refant = 'DA64',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_X9cffbd_Xefe.ms.split.ap_pre_bandpass', msName='uid___A002_X9cffbd_Xefe.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    caltable = 'uid___A002_X9cffbd_Xefe.ms.split.bandpass',
    field = '0', # J1733-1304
    scan = '1,2,4',
    solint = 'inf',
    combine = 'scan',
    refant = 'DA64',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_X9cffbd_Xefe.ms.split.ap_pre_bandpass')
  
  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.bandpass_smooth20ch') 
  
  bandpass(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    caltable = 'uid___A002_X9cffbd_Xefe.ms.split.bandpass_smooth20ch',
    field = '0', # J1733-1304
    scan = '1,2,4',
    solint = 'inf,20ch',
    combine = 'scan',
    refant = 'DA64',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_X9cffbd_Xefe.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X9cffbd_Xefe.ms.split.bandpass_smooth20ch', msName='uid___A002_X9cffbd_Xefe.ms.split', interactive=False) 
  
  if applyonly != True: es.checkCalTable('uid___A002_X9cffbd_Xefe.ms.split.bandpass', msName='uid___A002_X9cffbd_Xefe.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    caltable = 'uid___A002_X9cffbd_Xefe.ms.split.phase_int',
    field = '0~2', # J1733-1304,J1733-130,J1752-2956
    solint = 'int',
    refant = 'DA64',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X9cffbd_Xefe.ms.split.bandpass_smooth20ch')
  
  if applyonly != True: es.checkCalTable('uid___A002_X9cffbd_Xefe.ms.split.phase_int', msName='uid___A002_X9cffbd_Xefe.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    caltable = 'uid___A002_X9cffbd_Xefe.ms.split.ampli_inf',
    field = '0~2', # J1733-1304,J1733-130,J1752-2956
    solint = 'inf',
    refant = 'DA64',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_X9cffbd_Xefe.ms.split.bandpass_smooth20ch', 'uid___A002_X9cffbd_Xefe.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_X9cffbd_Xefe.ms.split.ampli_inf', msName='uid___A002_X9cffbd_Xefe.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X9cffbd_Xefe.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    caltable = 'uid___A002_X9cffbd_Xefe.ms.split.ampli_inf',
    fluxtable = 'uid___A002_X9cffbd_Xefe.ms.split.flux_inf',
    reference = '1') # J1733-130
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_X9cffbd_Xefe.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_X9cffbd_Xefe.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    caltable = 'uid___A002_X9cffbd_Xefe.ms.split.phase_inf',
    field = '0~2', # J1733-1304,J1733-130,J1752-2956
    solint = 'inf',
    refant = 'DA64',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X9cffbd_Xefe.ms.split.bandpass_smooth20ch')
  
  if applyonly != True: es.checkCalTable('uid___A002_X9cffbd_Xefe.ms.split.phase_inf', msName='uid___A002_X9cffbd_Xefe.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0', '1']: # J1733-1304,J1733-130
    applycal(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
      field = str(i),
      gaintable = ['uid___A002_X9cffbd_Xefe.ms.split.bandpass_smooth20ch', 'uid___A002_X9cffbd_Xefe.ms.split.phase_int', 'uid___A002_X9cffbd_Xefe.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = T,
      flagbackup = F)
  
  applycal(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    field = '2,3~151', # SgrB2
    gaintable = ['uid___A002_X9cffbd_Xefe.ms.split.bandpass_smooth20ch', 'uid___A002_X9cffbd_Xefe.ms.split.phase_inf', 'uid___A002_X9cffbd_Xefe.ms.split.flux_inf'],
    gainfield = ['', '2', '2'], # J1752-2956
    interp = 'linear,linear',
    calwt = T,
    flagbackup = F)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.cal') 
  os.system('rm -rf uid___A002_X9cffbd_Xefe.ms.split.cal.flagversions') 
  split(vis = 'uid___A002_X9cffbd_Xefe.ms.split',
    outputvis = 'uid___A002_X9cffbd_Xefe.ms.split.cal',
    datacolumn = 'corrected',
    keepflags = T)
  
  

# Save flags after applycal
mystep = 19
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X9cffbd_Xefe.ms.split.cal',
    mode = 'save',
    versionname = 'AfterApplycal')
  
  

