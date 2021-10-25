
from init import *
import os
import h5py
import shutil
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib 
import matplotlib.pyplot as plt
from shapely.ops import cascaded_union

##############################################################################################
#                                          common
##############################################################################################
def Cmap(cols):
	nmax = float(len(cols)-1)
	color_list = []
	for n, c in enumerate(cols):
		color_list.append((n/nmax, c))
	return matplotlib.colors.LinearSegmentedColormap.from_list('cmap', color_list)
def RemakeFolder(path):
	"""
	データをリセットし、フォルダを再作成
	"""
	if os.path.exists(path)==True:
		shutil.rmtree(path)
	os.makedirs(path)
def MakeFolder():
	"""
	フォルダの再構成
	"""
	RemakeFolder("./OUTPUT/CSV")
	RemakeFolder("./OUTPUT/PNG")
##############################################################################################
#                                       shp processing
##############################################################################################
def ShpProcess():
	## back ground
	shpfile = glob.glob("./SHP/GROUND/*.shp")
	if len(shpfile) ==1:
		shpb = ["Exists data", gpd.read_file(shpfile[0])]
	else:
		print("cannot corrected back ground shp file, please check")
		print("output png is not included shp data")
		shpb = ["No data", 0] 
	## Point in polygon
	shpfolder = os.listdir("./SHP/PIP")
	PIP = []
	for folder in shpfolder:
		RemakeFolder(f"./OUTPUT/PIP/{folder}")
		shpfile = glob.glob(f"./SHP/PIP/{folder}/*.shp")[0]
		shpdata = gpd.read_file(shpfile)
		shpdata = cascaded_union(shpdata.geometry)
		PIP.append([folder, shpdata])
	return shpb, PIP
##############################################################################################
#                                       data processing
##############################################################################################
def READ(filename, Ele):
	"""Object : filenameのデータを読み込み，そのデータとデータ種別名を返す関数. 
	filename  : file path
	Ele       : Element Number [lat, lon, data]

	CONTENTS  :
	STEP1 : Read data
	STEP2 : Get keys and select Element number[string]
	STEP3 : Get specific data
	"""
	## STEP1
	data = h5py.File(filename, 'r')
	## STEP2
	G1 = data.keys()
	COUNT, ELEMENT = 0, []
	for i in G1:
		G2 = data[i].keys()
		for f in G2:
			ELEMENT.append([i, f])
			COUNT = COUNT + 1
	if Ele[0]==-1 or Ele[1]==-1 or Ele[2]==-1:
		print("-----------------Contents--------------------")
		for i in range(0,len(ELEMENT)):
			print(i, ELEMENT[i][0], ELEMENT[i][1])
		print("---------------------------------------------")
		LAT = int(input("PLEASE SELECT LAT NUMBER\n"))
		LON = int(input("PLEASE SELECT LON NUMBER\n"))
		ELE = int(input("PLEASE SELECT DATA NUMBER\n"))
	else:
		LAT, LON, ELE = Ele[0], Ele[1], Ele[2]
	LAT1, LAT2 = ELEMENT[LAT][0], ELEMENT[LAT][1]
	LON1, LON2 = ELEMENT[LON][0], ELEMENT[LON][1]
	ELE1, ELE2 = ELEMENT[ELE][0], ELEMENT[ELE][1]
	### STEP3
	LAT    = np.array(data[LAT1][LAT2])
	LON    = np.array(data[LON1][LON2])
	DATA   = np.array(data[ELE1][ELE2])
	data.close()
	return LAT, LON, DATA, ELEMENT[ELE][1]

def Interpolation(point:list):
	"""Object : 内挿補間(BILINEAR)\n
	point : [左上，右上，左下，右下]\n
	CONTENTS :\n
	STEP1 : Make New Grid
	STEP2 : processing(BILINEAR)
	"""
	## STEP1 : Make New Grid
	NG = np.zeros((10,10))
	NGc      = [[0,0], [0,9], [9,0], [9,9]]          # New Grid corner
	## STEP2 : processing
	NG[0,0], NG[0,9], NG[9,0], NG[9,9] = point[0], point[1], point[2], point[3]
	for i in range(0, NG.shape[0]):
		for f in range(0, NG.shape[1]):
			if [i,f] not in NGc:
				dx, dy = f/9, i/9
				Ax = (1-dx) * (1-dy) * NG[0,0]
				Bx = dx     * (1-dy) * NG[0,9]
				Cx = (1-dx) * dy     * NG[9,0]
				Dx = dx     * dy     * NG[9,9]
				NG[i,f] = Ax + Bx + Cx + Dx
	return NG

def EditDATA(lat, lon, data, slope, offset, XLIM, YLIM):
	"""Object : データ変換及び取得範囲の設定
	lat     : 緯度
	lon     : 経度
	data    : データ
	slope   : slope
	offset  : offset 
	XLIM    : Lon. range [min, max]
	YLIM    : Lat. range [min, max]

	CONTENTS:
	STEP1 : Convert data
	STEP2 : Extract the specified range of data
	STEP3 : Interpolation Coor.
	"""
	## STEP1 : Convert data
	data = np.where(data>=65532, -999, data*slope+offset)  ## processing of lack and low quality data
	## STEP2 : Extract the specified range of data
	# Edit(Update) coor limit
	if XLIM==[-9999,-9999]:
		XLIM = [np.nanmin(lon), np.nanmax(lon)]
	if YLIM==[-9999,-9999]:
		YLIM = [np.nanmin(lat), np.nanmax(lat)]
	# Get index within target area
	dx  = np.where((XLIM[0]<=lon) & (lon<=XLIM[1]), 1, 0) # within 1, without 0
	dy  = np.where((YLIM[0]<=lat) & (lat<=YLIM[1]), 1, 0) # within 1, without 0
	In  = np.where((dx == 1)      & (dy == 1),      1, 0) # within area
	dx  = np.array(np.where(np.sum(In, axis=0)>=1))       # pick index
	dxL = [np.nanmin(dx), np.nanmax(dx)]
	dy  = np.array(np.where(np.sum(In, axis=1)>=1))       # pick index
	dyL = [np.nanmin(dy), np.nanmax(dy)]
	lat, lon = lat[dyL[0]:dyL[1], dxL[0]:dxL[1]], lon[dyL[0]:dyL[1], dxL[0]:dxL[1]]
	data     = data[dyL[0]*10:(dyL[1]-1)*10, dxL[0]*10:(dxL[1]-1)*10]
	#############################################################################
	#                        STEP3 : Interpolation Coor.
	# Latitude and longitude are compressed to 1/10, so need to interpolate
	#############################################################################
	# make result box
	LAT = np.zeros(((lat.shape[0]-1)*10, (lon.shape[1]-1)*10)) + np.nan
	LON = np.zeros(((lat.shape[0]-1)*10, (lon.shape[1]-1)*10)) + np.nan
	for a in range(0, lat.shape[0]-1):
		for o in range(0, lon.shape[1]-1):
			## LAT
			LATc = [lat[a,o], lat[a,o+1], lat[a+1,o], lat[a+1,o+1]]
			LAT[a*10:(a+1)*10, o*10:(o+1)*10] = Interpolation(LATc)
			## LON
			LONc = [lon[a,o], lon[a,o+1], lon[a+1,o], lon[a+1,o+1]]
			LON[a*10:(a+1)*10, o*10:(o+1)*10] = Interpolation(LONc)
	return LAT, LON, data

def OutputCsv(filename, dtype, lat, lon, data):
	## Prepare
	SaveName = filename.split("/")[-1].replace(".h5", ".csv")
	## replace
	lat  = np.reshape(lat,  ((lat.shape[0]  * lat.shape[1],  1)))
	lon  = np.reshape(lon,  ((lon.shape[0]  * lon.shape[1],  1)))
	data = np.reshape(data, ((data.shape[0] * data.shape[1], 1)))
	df   = np.append(lat, lon,  axis=1)
	df   = np.append(df,  data, axis=1)
	df   = pd.DataFrame(df, columns=["LAT", "LON", dtype])
	df.to_csv(f"./OUTPUT/CSV/{SaveName}", index=None)
	return df

def PIP(filename, data, shp):
	## Prepare
	ShpName, Shpdata = shp[0], shp[1]
	SaveName = filename.split("/")[-1].replace(".h5", ".txt")
	SavePath = f"./OUTPUT/PIP/{ShpName}/{SaveName}"
	## Main
	data = gpd.GeoDataFrame(data,geometry=gpd.points_from_xy(data.LON,data.LAT)) # dataframe to geodataframe
	data = data.set_crs("EPSG:4326")                                             # set coor type
	col  = list(data.columns)
	with open(SavePath, "w") as output:
		output.write(f"{col[0]},{col[1]},{col[2]}\n")
		for point in range(0, data.shape[0]):
			if Shpdata.contains(data.loc[point,"geometry"])==True:
				lon, lat = str(data.loc[point,col[0]]), str(data.loc[point,col[1]])
				ele      = str(data.loc[point,col[2]])
				output.write(f"{lon},{lat},{ele}\n")

##############################################################################################
#                                          Draw
##############################################################################################
def SetParams(cmap, XLIM, YLIM):
	## figure size
	degX, degY = XLIM[1] - XLIM[0], YLIM[1] - YLIM[0]
	if degX >= degY:
		figx, figy = 12, degY/degX*12
	else:
		figx, figy = degX/degY*12, 12
	## cmap
	if cmap == None:
		cmap="rainbow"
	else:
		cmap=Cmap(cmap)
	## xticks
	xticks = np.linspace(XLIM[0], XLIM[1], 5)
	yticks = np.linspace(YLIM[0], YLIM[1], 5)
	return [figx, figy], cmap, xticks, yticks

def OutputPng(filename, lat, lon, data, vmin, vmax, cmap, shp):
	## prepare
	FigSize, cmap, xticks, yticks = SetParams(cmap, XLIM, YLIM)
	savename = filename.split("/")[-1].replace(".h5", ".png")
	## DRAW
	fig = plt.figure(figsize=(FigSize[0], FigSize[1]), dpi=250)
	ax = fig.add_subplot(111)
	## COUNTOR PLOT
	contour = ax.pcolormesh(lon, lat, data, edgecolor="none",
							cmap=cmap, vmin=vmin, vmax=vmax, shading="gouraud", zorder=1)
	bar     = fig.colorbar(contour, ax=ax, ticks=np.linspace(vmin, vmax, 5), shrink=0.3)
	## SHP PLOT
	if shp[0] == "Exists data":
		shp[1].plot(ax=ax, facecolor="k", edgecolor="none", zorder=2)
	plt.xticks(xticks, rotation=45)
	plt.yticks(yticks, rotation=45)
	plt.xlim(XLIM)
	plt.ylim(YLIM)
	plt.savefig(f"./OUTPUT/PNG/{savename}", bbox_inches="tight")
	plt.close()
	

if __name__ == "__main__":
	MakeFolder()                   # make output folder
	GROUNDs, PIPs = ShpProcess()   # read shp files
	count = 1
	for file in filelist:
		print(f"{count} / {len(filelist)}")
		count +=1
		lat, lon, data, EleName = READ(file, Ele)                             # read file
		lat, lon, data = EditDATA(lat, lon, data, slope, offset, XLIM, YLIM)  # Edit data
		df = OutputCsv(file, EleName, lat, lon, data)                         # output csv
		for shp in PIPs:
			PIP(file, df, shp)
		if XLIM != [-9999,-9999] and YLIM != [-9999,-9999]:
			OutputPng(file, lat, lon, data, vmin, vmax, cmap, GROUNDs)