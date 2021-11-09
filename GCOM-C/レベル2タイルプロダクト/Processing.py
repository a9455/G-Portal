

"""
GCOM-C：レベル2タイルプロダクトに対応したデータ処理スクリプト
HandBook1, P56～

想定：
●DATAフォルダにすべてのファイルがそろっている
"""


import os
import glob
import h5py
import math
import shutil
import numpy as np
import pandas as pd
import geopandas as gpd
import datetime as dt
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt
from shapely.ops import cascaded_union

#########################################################################
#                               COMMON
#########################################################################
### Folder
def MKDIR(path):
	"""
	Creating a non-existent folder
	"""
	if os.path.exists(path)==False:
		os.makedirs(path)

def MakeNewDir(path):
	"""
	Folder initialization
	"""
	if os.path.exists(path)==False:
		os.makedirs(path)

### Make List
#   Times
def MakeTimeList(start:list, end:list, delta:str):
	"""
	Make time list : [year, month, day]
	"""
	## prepare
	Sdate = dt.datetime(*start)
	Edate = dt.datetime(*end)
	if delta=="H":
		delta = dt.timedelta(hours=1)
	elif delta == "D":
		delta = dt.timedelta(days=1)
	elif delta=="M":
		delta = relativedelta(months=1)
	## Main
	TimeList = []
	while Sdate <= Edate:
		TimeList.append([Sdate.year, Sdate.month, Sdate.day])
		Sdate += delta
	return TimeList

def MoveFiles(filename):
	## get folder name
	DIR = []
	dir1 = os.listdir("./tmp")
	for dirx in dir1:
		dir2 = os.listdir(f"./tmp/{dirx}")
		for dirx2 in dir2:
			print(dirx, dirx2)
			if dirx != "DATA":
				dir2x = dirx2.replace(".csv","")
				if dir2x == "COMMON":
					DIR.append([dirx, dirx2, dirx])
				else:
					DIR.append([dirx, dirx2, dir2x])
	## move files
	for dirx in DIR:
		MKDIR(f"./OUTPUT/ATTRIBUTES/{dirx[2]}")
		shutil.move(f"./tmp/{dirx[0]}/{dirx[1]}",
					f"./OUTPUT/ATTRIBUTES/{dirx[2]}/{filename}.csv")
#########################################################################
#                            Data Processing
#########################################################################
### SHP
def ShpProcess():
	## 背景図の読み込み
	shpfile = glob.glob("./SHP/GROUND/*.shp")
	if len(shpfile) ==1:
		shpb = ["Exists data", gpd.read_file(shpfile[0])]
	else:
		print("Cannot loaded back ground shp file, The illustrated png file has no background diagram")
		shpb = ["No data", 0] 
	## Point in polygonで利用するshpファイルの読込
	shpfolder = os.listdir("./SHP/PIP")
	PIP = []
	for folder in shpfolder:
		shpfile = glob.glob(f"./SHP/PIP/{folder}/*.shp")[0]
		shpdata = gpd.read_file(shpfile)
		shpdata = cascaded_union(shpdata.geometry)
		PIP.append([folder, shpdata])
	return shpb, PIP

### Lat and Lon
def Coordinate(Tile):
	### params ###
	Nmesh        = 4800 
	tileY, tileX = int(Tile[:2]), int(Tile[2:])
	### read tile's lat(lon) from tile number ###
	Lat = np.arange(90, -90, -10)
	tileYS, tileYE = Lat[tileY], Lat[tileY+1]
	Lon = np.arange(-180, 180, 10)
	tileXS, tileXE = Lon[tileX], Lon[tileX+1]
	### cal mesh's lat(lon) ###
	lat = np.zeros((Nmesh,Nmesh))
	for i in range(0,lat.shape[0]):
		lat[i,:] = np.linspace(tileYS, tileYE, Nmesh)[i]
	lon = np.zeros((Nmesh,Nmesh))
	for i in range(0,lon.shape[1]):
		lon[:,i] = np.linspace(tileXS, tileXE, Nmesh)[i]
	for i in range(0,Nmesh):
		for f in range(0,Nmesh):
			lon[i,f] = lon[i,f] / math.cos(lat[i,f] * np.pi / 180)
	return lon, lat

def GetCoor(Tile):
	if os.path.exists(f"./OUTPUT/COOR/{Tile}_Lon.npy")==False or os.path.exists(f"./OUTPUT/COOR/{Tile}_Lat.npy")==False:
		lon, lat = Coordinate(Tile)
		np.save(f"./OUTPUT/COOR/{Tile}_Lon.npy", lon)
		np.save(f"./OUTPUT/COOR/{Tile}_Lat.npy", lat)

### HDF5
def GetAttributesInfo(hdf5, GROUP, WorkPath, Name="COMMON"):
	"""
	hdf5データからメタ情報を読み取る関数\n
	hdf5  : hdf5 data\n
	GName : target attribute\n
	spath : save path\n
	"""
	attr = hdf5.attrs
	keys = attr.keys()
	if Name == "COMMON":
		Name = "COMMON"
	else:
		Name = Name
	MKDIR(f"{WorkPath}/{GROUP}")
	with open(f"{WorkPath}/{GROUP}/{Name}.csv", "w") as file:
		for key in keys:
			cont = str(attr[key][0]).replace("b'", "").replace("'", "").replace(",", " ")
			file.write(f"{key},{cont}\n")

def GetDatasetInfo(hdf5, WorkPath, GROUP):
	data = np.array(hdf5)
	np.save(f"./{WorkPath}/DATA/{GROUP}.npy", data)

def Readhdf5(WorkPath, filepath):
	MakeNewDir(WorkPath)                                   # フォルダの初期化
	MKDIR(f"./{WorkPath}/DATA")
	hdf5     = h5py.File(filepath, 'r')                    # hdf5ファイルの読み込み
	GROUP1   = list(hdf5.keys())                           # 一番浅い階層のグループ名を取得
	CONTENTS = []                                          # 変数名の箱
	for G1 in GROUP1:
		MKDIR(f"{WorkPath}/{G1}")
		hdf5G1 = hdf5[G1]
		GetAttributesInfo(hdf5G1, G1, WorkPath)              # 階層全般のメタ情報を取得
		GROUP2 = list(hdf5G1.keys())                         # 2番目の階層にあるグループ名を取得
		for G2 in GROUP2:
			hdf5G2 = hdf5G1[G2]
			CONTENTS.append([G1, G2])
			GetAttributesInfo(hdf5G2, G2, WorkPath, Name=G2) # 階層全般のメタ情報を取得
			GetDatasetInfo(hdf5G2, WorkPath, G2)             # 数値データの取得
	hdf5.close()
	return CONTENTS

def EditGeometry(WorkPath, filename, Tile, cont, XLIM, YLIM):
	MKDIR(f"./OUTPUT/CSV/{cont[1]}")
	## STEP0 : Load data
	lat  = np.load(f"./OUTPUT/COOR/{Tile}_Lat.npy")
	lon  = np.load(f"./OUTPUT/COOR/{Tile}_Lon.npy")
	data = np.load(f"{WorkPath}/DATA/{cont[1]}.npy")
	if lat.shape == data.shape:
		## STEP1 : reshape
		lat  = np.reshape(lat,  ((lat.shape[0]  * lat.shape[1]  ,1)))
		lon  = np.reshape(lon,  ((lon.shape[0]  * lon.shape[1]  ,1)))
		data = np.reshape(data, ((data.shape[0] * data.shape[1] ,1)))
		## STEP2 : within range
		# Edit(Update) coor limit
		if XLIM==[-9999,-9999]:
			XLIM = [np.nanmin(lon), np.nanmax(lon)]
		else:
			XLIM = XLIM
		if YLIM==[-9999,-9999]:
			YLIM = [np.nanmin(lat), np.nanmax(lat)]
		else:
			YLIM = YLIM
		la = np.where((YLIM[0]<=lat) & (lat<=YLIM[1]) ,1, 0)
		lo = np.where((XLIM[0]<=lon) & (lon<=XLIM[1]) ,1, 0)
		within = la + lo
		within = np.where(within==1, True, False)
		lat, lon, data = lat[within], lon[within], data[within]
		# reshape
		lat  = np.reshape(lat,  ((lat.shape[0]  ,1)))
		lon  = np.reshape(lon,  ((lon.shape[0]  ,1)))
		data = np.reshape(data, ((data.shape[0] ,1)))
		## STEP3 : concat
		res = np.append(lat, lon,  axis=1)
		res = np.append(res, data, axis=1)
		## STEP4 : To dataframe
		res = pd.DataFrame(res, columns=["LAT", "LON", cont[1]])
		res.to_csv(f"./OUTPUT/CSV/{cont[1]}/{filename}.csv", index=None)

def EditImage(Dflag, WorkPath, Tile, cont, XLIM, YLIM, PIPs, cmap, filename, GROUNDs, Element):
	## STEP0 : Load data
	lat  = np.load(f"./OUTPUT/COOR/{Tile}_Lat.npy")
	lon  = np.load(f"./OUTPUT/COOR/{Tile}_Lon.npy")
	data = np.load(f"{WorkPath}/DATA/{cont[1]}.npy")
	## 処理対象が2次元ならば。。。
	if lat.shape==data.shape:
		## STEP1 : Convert data
		info          = pd.read_csv(f"{WorkPath}/{cont[1]}/{cont[1]}.csv", index_col=0, header=None)
		offset, slope = float(info.loc["Offset",info.columns[0]]), float(info.loc["Slope",info.columns[0]])
		FillRange     = [float(info.loc["Minimum_valid_DN",info.columns[0]]), float(info.loc["Maximum_valid_DN",info.columns[0]])]
		data          = np.where((FillRange[0]<data) & (data<FillRange[1]), data*slope+offset, -999)
		## STEP2 : Extract the specified range of data
		# Edit(Update) coor limit
		if XLIM==[-9999,-9999]:
			XLIM = [np.nanmin(lon), np.nanmax(lon)]
		else:
			XLIM = XLIM
		if YLIM==[-9999,-9999]:
			YLIM = [np.nanmin(lat), np.nanmax(lat)]
		else:
			YLIM = YLIM
		# Get index within target area
		dx  = np.where((XLIM[0]<=lon) & (lon<=XLIM[1]), 1, 0) # within 1, without 0
		dy  = np.where((YLIM[0]<=lat) & (lat<=YLIM[1]), 1, 0) # within 1, without 0
		In  = np.where((dx == 1)      & (dy == 1),      1, 0) # within area
		dx  = np.array(np.where(np.sum(In, axis=0)>=1))       # pick index
		dxL = [np.nanmin(dx), np.nanmax(dx)]
		dy  = np.array(np.where(np.sum(In, axis=1)>=1))       # pick index
		dyL = [np.nanmin(dy), np.nanmax(dy)]
		lat, lon = lat[dyL[0]:dyL[1], dxL[0]:dxL[1]], lon[dyL[0]:dyL[1], dxL[0]:dxL[1]]
		data     = data[dyL[0]:dyL[1], dxL[0]:dxL[1]]
		df = OutputCsv(lat, lon, data, cont, filename)
		for shp in PIPs:
			PIP(shp, df, cont, filename)
		if Dflag == "yes":
			if XLIM != [-9999,-9999] and YLIM != [-9999,-9999]:
				OutputPng(lat, lon, data, GROUNDs, filename, cont, Element, cmap, XLIM, YLIM)

def CalImage(ColorPath, filename, vmin, vmax):
	# データ
	data = pd.read_csv(f"./OUTPUT/CSV/{ColorPath}/{filename}.csv")
	x, y, data = np.array(data.loc[:,"LON"]), np.array(data.loc[:,"LAT"]), np.array(data.iloc[:,2])
	data = np.where(data==-999, 0, data)
	color = NormColor(data, vmin, vmax)
	return x[::5], y[::5], color[::5]

### OUTPUT
def OutputCsv(lat, lon, data, cont, filename):
	MKDIR(f"./OUTPUT/CSV/{cont[1]}")
	## replace
	lat  = np.reshape(lat,  ((lat.shape[0]  * lat.shape[1],  1)))
	lon  = np.reshape(lon,  ((lon.shape[0]  * lon.shape[1],  1)))
	data = np.reshape(data, ((data.shape[0] * data.shape[1], 1)))
	df   = np.append(lat, lon,  axis=1)
	df   = np.append(df,  data, axis=1)
	df   = pd.DataFrame(df, columns=["LAT", "LON", cont[1]])
	df.to_csv(f"./OUTPUT/CSV/{cont[1]}/{filename}.csv", index=None)
	return df

def PIP(shp, df, cont, filename):
	## Prepare
	ShpName, Shpdata = shp[0], shp[1]
	## Main
	data = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LON, df.LAT))
	data = data.set_crs("EPSG:4326")
	col  = list(data.columns)
	SaveFolder = f"./OUTPUT/PIP/{cont[1]}/{ShpName}"
	MKDIR(SaveFolder)
	with open(f"{SaveFolder}/{filename}.csv", "w") as output:
		output.write(f"{col[0]},{col[1]},{col[2]}\n")
		for point in range(0, data.shape[0]):
			if Shpdata.contains(data.loc[point,"geometry"])==True:
				lon, lat = str(data.loc[point,col[0]]), str(data.loc[point,col[1]])
				ele      = str(data.loc[point,col[2]])
				output.write(f"{lon},{lat},{ele}\n")

def OutputPng(lat, lon, data, GROUNDs, filename, cont, Element, cmap, XLIM, YLIM):
	## prepare
	SaveDir = f"./OUTPUT/PNG/ROW/{cont[1]}"
	MKDIR(SaveDir)
	figX, figY, xticks, yticks = SetParams(XLIM, YLIM)
	## DRAW
	fig = plt.figure(figsize=(figX, figY), dpi=250)
	ax = fig.add_subplot(111)
	## COUNTOR PLOT
	data = data + 0
	nand = np.where(data==-999 , 99999,           data)
	data = np.where(nand==99999, np.nanmin(nand), data)
	if Element[0] == "ALL":
		Vmin, Vmax = np.nanmin(data), np.nanmax(data)
	else:
		Vmin, Vmax = Element[1], Element[2]
	contour = ax.pcolormesh(lon, lat, data, edgecolor="none",
							cmap=cmap, vmin=Vmin, vmax=Vmax, shading="gouraud", zorder=1)
	bar     = fig.colorbar(contour, ax=ax, ticks=np.linspace(Vmin,Vmax, 5), shrink=0.3)
	## SHP PLOT
	if GROUNDs[0] == "Exists data":
		GROUNDs[1].plot(ax=ax, facecolor="k", edgecolor="none", zorder=2)
	plt.xticks(xticks, rotation=45)
	plt.yticks(yticks, rotation=45)
	plt.xlim(XLIM)
	plt.ylim(YLIM)
	plt.savefig(f"{SaveDir}/{filename}.png", bbox_inches="tight")
	plt.close()


# Draw
def SetParams(XLIM, YLIM):
	## figure size
	degX, degY = XLIM[1] - XLIM[0], YLIM[1] - YLIM[0]
	if degX >= degY:
		figx, figy = 12, degY/degX*12
	else:
		figx, figy = degX/degY*12, 12
	figX, figY = figx, figy
	## xticks
	xticks = np.linspace(XLIM[0], XLIM[1], 5)
	yticks = np.linspace(YLIM[0], YLIM[1], 5)
	return figX, figY, xticks, yticks

def NormColor(x, vmin, vmax):
	x = np.where(x<vmin, vmin, x)
	x = np.where(x>vmax, vmax, x)
	res  = ((x - vmin) / (vmax - vmin))
	return res

def Stack(Rpath:list, Gpath:list, Bpath:list, filename):
	MKDIR("./OUTPUT/PNG/RGB")
	if Rpath[0]!=None and Gpath[0]!=None and Bpath[0]!=None:
		x, y, Reds   = CalImage(Rpath[0], filename, Rpath[1], Rpath[2])
		x, y, Greens = CalImage(Gpath[0], filename, Gpath[1], Gpath[2])
		x, y, Blues  = CalImage(Bpath[0], filename, Bpath[1], Bpath[2])
		x  = np.reshape(x, ((x.shape[0],1)))
		y  = np.reshape(y, ((y.shape[0],1)))
		colors = []
		for c in range(0,len(Reds)):
			colors.append((Reds[c], Greens[c], Blues[c]))
		plt.rcParams["figure.figsize"] = (14, 12)
		plt.scatter(x, y, c=colors, marker="s", s=3, edgecolor="none")
		plt.savefig(f"./OUTPUT/PNG/RGB/{filename}.png", bbox_inches="tight", dpi=250)
		plt.close()

### MAIN
if __name__ == "__main__":
	from params import *
	WorkPath     = f"./tmp"
	SaveCsvPath  = f"./OUTPUT/CSV"
	SavePngPath  = f"./OUTPUT/PNG"
	SavePIPPath  = f"./OUTPUT/PIP"
	SaveTailPath = f"./OUTPUT/COOR"
	#-------------------------------------------------------------------------
	#                                   MAIN
	#-------------------------------------------------------------------------
	## フォルダの作成
	MKDIR("./SHP/PIP")
	MKDIR("./SHP/GROUND")
	MKDIR(WorkPath)
	MKDIR(SaveCsvPath)
	MKDIR(SavePngPath)
	MKDIR(SavePIPPath)
	MKDIR(SaveTailPath)
	
	GROUNDs, PIPs = ShpProcess()                ## shpデータの読み込み
	TimeList = MakeTimeList(start, end, delta)  ## 処理する時間の取得

	for Time in TimeList:
		year, month, day = str(Time[0]).zfill(2), str(Time[1]).zfill(2), str(Time[2]).zfill(2)    ## 処理日時
		FilePath0 = f"./{Dfolder}/{Satelite}{Sensor}_{year}{month}{day}{A_D}{Ptu}_{Mapping}TileNo_{Level}{Type}_{ProductID}{Resolution}_{AlgoVer}{ppp}.h5"
		for Tile in TileNoList:
			try:
				FilePath = FilePath0.replace("TileNo", Tile)                                          ## ファイルパス
				filename = FilePath.split("/")[-1].replace(".h5","")
				GetCoor(Tile)                                                               ## cal lat and lon
				contents = Readhdf5(WorkPath, FilePath)                                               ## read datasets
				for cont in contents:
					if cont[0] == "Geometry_data":
						EditGeometry(WorkPath, filename, Tile, cont, XLIM, YLIM)         ## Geometry_dataに対する処理
					elif cont[0] == "Image_data":
						EditImage(Dflag, WorkPath, Tile, cont, XLIM, YLIM, PIPs, cmap, filename, GROUNDs, Element) ## Image_dataに対する処理(CSV出力, PIP出力, PNG出力)
				if Dflag == "yes":
					Stack(Rpath, Gpath, Bpath, filename)
				MoveFiles(filename)
				shutil.rmtree("./tmp")
			except FileNotFoundError:
				print(f"File doesn't exists, {year}/{month}/{day}")


