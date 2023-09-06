import glob, sys
sys.path.insert(1, '/home/satreps/.libraries/olah/proj1/denetcdf/src/denetcdf')
import denetcdf
import netCDF4 as nc
import numpy as np
from wrf import getvar, vinterp, to_np, get_basemap, latlon_coords, extract_times, ALL_TIMES

fl = sorted(glob.glob('/home/satreps/.libraries/test/output/2023090400/wrfout*'))

fh=nc.Dataset(fl[0])
lats=to_np(getvar(fh, "lat"))[:,0]
lons=to_np(getvar(fh, "lon"))[0,:]
fh.close()
fh=[nc.Dataset(i) for i in fl]
titles=[];vars=[];units=[];data=[]
titles.append('Particulate Matter 10 (g/kg)')
vars.append('pm10')
units.append('g/kg')
pm_10=[to_np(fh[i]['PM10']) for i in range(len(fl))];data.append(np.squeeze(np.array(pm_10))[:,0,:,:])
titles.append('Particulate Matter 2.5 (g/kg)')
vars.append('pm25')
units.append('g/kg')
pm_25=[to_np(fh[i]['PM2_5_DRY']) for i in range(len(fl))];data.append(np.squeeze(np.array(pm_10))[:,0,:,:])
titles.append('Sulfur dioxide (SO2) (ppm)')
vars.append('so2')
units.append('ppm')
pm_so=[to_np(fh[i]['so2']) for i in range(len(fl))];data.append(np.squeeze(np.array(pm_10))[:,0,:,:])
titles.append('Carbon monoxide (CO) (ppm)')
vars.append('co')
units.append('ppm')
pm_co=[to_np(fh[i]['co']) for i in range(len(fl))];data.append(np.squeeze(np.array(pm_10))[:,0,:,:])
data=np.array(data)
denetcdf.create('testm.nc', lats, lons, 'Inaaqm Output', '20230905000000', len(fl), titles,vars,units, data)

