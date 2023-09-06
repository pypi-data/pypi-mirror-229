from netCDF4 import Dataset, date2num
import numpy as np
import datetime
# copyrigh @ den@2023
def create(filen, lats, lons, judul, xxxx, nt, name,var,unit,data):
	fname = filen
	ncfile = Dataset(fname,'w',format='NETCDF4') 
	ncfile.title = judul
	lats=lats
	lons=lons
	xxxx=xxxx
	ncfile.createDimension('lon',len(lons))
	ncfile.createDimension('lat',len(lats))
	ncfile.createDimension('time',int(nt))
	longitude = ncfile.createVariable('lon','f4','lon')
	longitude.grads_dim='x'
	longitude.grads_mapping='linear'
	longitude.grads_size=str(len(lons))
	longitude.units='degrees_east'
	longitude.long_name='longitude'
	longitude.minimum=str(lons.min())
	longitude.maximum=str(lons.max())
	longitude[:] = lons

	latitude = ncfile.createVariable('lat','f4','lat')
	latitude.grads_dim='y'
	latitude.grads_mapping='linear'
	latitude.grads_size=str(len(lats))
	latitude.units='degrees_north'
	latitude.long_name='latitude'
	latitude.minimum=str(lats.min())
	latitude.maximum=str(lats.max())
	latitude.resolution=str(lats[-1]-lats[-2])
	latitude[:] = lats

	baseTimeS = [datetime.datetime(int(xxxx[:4]),int(xxxx[4:6]),int(xxxx[6:8]),int(xxxx[8:10]),int(xxxx[10:12]),int(xxxx[12:]))+datetime.timedelta(hours=i) for i in range(int(nt))]
	ttime = ncfile.createVariable('time','i4','time')
	ttime.grads_dim='t'
	ttime.grads_mapping='linear'
	ttime.units='hours since '+xxxx[:4]+'-'+xxxx[4:6]+'-'+xxxx[6:8]+' '+xxxx[8:10]+':'+xxxx[10:12]+':'+xxxx[12:]+''
	ttime.calendar = 'gregorian'
	ttime.long_name='time'
	ttime[:]=date2num(baseTimeS,units=ttime.units,calendar=ttime.calendar)

	for i in range(len(name)):
		wb = ncfile.createVariable(var[i],'f4',('time','lat','lon'))
		wb.units = unit[i]
		wb.standard_name = name[i]
		wb[:,:,:]=data[i,...]
	ncfile.close()


if __name__ == "__main__":
    create()
