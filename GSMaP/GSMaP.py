import os
import h5py
import glob
import shutil
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
from ftplib import FTP
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import geopandas as gpd
from shapely.ops import cascaded_union

#######################################################################################
#                                       common
#######################################################################################
def OutputInit():
	"""
	取得条件の書き出し
	"""
	print("------------------取得条件--------------------")
	print(f"host       = {host}")
	print(f"user       = {user}")
	print(f"pw         = {pw}")
	print(f"TargetFor  = {TargetFor}")
	print(f"lon        = {lat}")
	print(f"lat        = {lon}")
	print(f"start      = {start}")
	print(f"end        = {end}")
	print(f"delta time = {delta}")
	print(f"ElementNum = {ElementNum}")
	print("---------------------------------------------")

### prepare folder
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
	RemakeFolder("./OUTPUT/ROW")
	RemakeFolder("./OUTPUT/CSV")
	RemakeFolder("./OUTPUT/PNG")

### get date info from datetime
def DatetimeToElement(date):
	"""
	datetime型から年月日時を取得する
	年　　：4桁
	月日時：2桁
	"""
	year  = str(date.year)
	month = str(date.month).zfill(2)
	day   = str(date.day).zfill(2)
	hour  = str(date.hour).zfill(2)
	return year, month, day, hour

### make file list
def MakeFileList(start:list, end:list, delta):
	"""
	取得時間のリストを作成
	start : 取得開始時間
	end   : 取得終了時間
	"""
	print("Make File List", end="")
	Sdate = dt.datetime(*start)
	Edate = dt.datetime(*end)
	FilePaths = []
	## 時間
	if delta == "H":
		dirA = "standard/GSMaP/3.GSMAP.H/Unknown"
		while Sdate<=Edate:
			yy, mm, dd, hh = DatetimeToElement(Sdate)
			dirB           = f"{yy}/{mm}/{dd}/GPMMRG_MAP_{yy[2:]}{mm}{dd}{hh}00_H_L3S_MCH_Unknown.h5"
			FilePaths.append(f"{dirA}/{dirB}")
			Sdate = Sdate + dt.timedelta(hours=1)
	## 月
	elif delta == "M":
		dirA = "standard/GSMaP/3.GSMAP.M/Unknown"
		while Sdate<=Edate:
			yy, mm, dd, hh = DatetimeToElement(Sdate)
			dirB = f"{yy}/GPMMRG_MAP_{yy[2:]}{mm}_M_L3S_MCM_Unknown.h5"
			FilePaths.append(f"{dirA}/{dirB}")
			Sdate = Sdate + relativedelta(months=1)
	print(f"  Total {len(FilePaths)} files")
	return dirA.replace("/Unknown",""), FilePaths


def Scale(lon, lat):
	londeg = lon[1] - lon[0]
	latdeg = lat[1] - lat[0]
	if londeg >= latdeg:
		londeg = 16
		latdeg = latdeg/londeg * 16
	else:
		londeg = londeg/latdeg * 16
		latdeg = 16
	return londeg, latdeg
#######################################################################################
#                                      ftp server
#######################################################################################
def GetSateliteVarsion(ftp, dirA):
	Satelite = ftp.nlst(dirA)
	for s in range(0,len(Satelite)):
		Satelite[s] = Satelite[s].replace(f"{dirA}/","")
	return Satelite

def DownloadFile(ftp, Filepath, Satelites):
	for s in Satelites:
		filepath = Filepath.replace("Unknown", s)
		filename = filepath.split("/")[-1]
		try:
			with open(f"./OUTPUT/ROW/{filename}", "wb") as f:  # make new file to write data
				ftp.retrbinary('RETR %s' % filepath, f.write)  # write data
				break
		except Exception:
			os.remove(f"./OUTPUT/ROW/{filename}")              # if Error occured, maked file is deleted
	return filename

#######################################################################################
#                                    file processing
#######################################################################################
def ReadRowFile(file, ElementNum):
	data = h5py.File(file, 'r')
	G1 = data.keys()
	ELEMENT = []
	for i in G1:
		G2 = data[i].keys()
		for f in G2:
			ELEMENT.append([i, f])
	LAT, LON = 0, 1
	if ElementNum == -1:
		for i in range(0,len(ELEMENT)):
			print(i,ELEMENT[i][0],ELEMENT[i][1])
		ELE = int(input("PLEASE CHOOSE ELEMENT NUMBER\n"))
	else:
		ELE = int(ElementNum)
	LON1, LON2 = ELEMENT[LON][0], ELEMENT[LON][1]
	LAT1, LAT2 = ELEMENT[LAT][0], ELEMENT[LAT][1]
	G1,   G2   = ELEMENT[ELE][0], ELEMENT[ELE][1]
	### READ DATA
	LON   = np.array(data[LON1][LON2], dtype=float)
	LAT   = np.array(data[LAT1][LAT2], dtype=float)
	DATA  = np.array(data[G1][G2],     dtype=float)
	data.close()
	out = [LON, LAT, DATA]
	return out, G2, ELE

def OutputCsv(data, lon, lat, G2, Savefilepath):
	LON, LAT, DATA = data[0], data[1], data[2]
	## Reshape
	LON  = np.reshape(LON,  ((LON.shape[0]  * LON.shape[1],  1)))
	LAT  = np.reshape(LAT,  ((LAT.shape[0]  * LAT.shape[1],  1)))
	DATA = np.reshape(DATA, ((DATA.shape[0] * DATA.shape[1], 1)))
	## concat
	out  = np.append(LON, LAT,  axis=1)
	out  = np.append(out, DATA, axis=1)
	df = []
	for i in range(0,out.shape[0]):
		x, y = out[i,0], out[i,1]
		if lon[0]<=x and x<=lon[1] and lat[0]<=y and y<=lat[1]:
			df.append([np.round(out[i,0],2), np.round(out[i,1],2), np.round(out[i,2],2)])
	df = pd.DataFrame(df, columns=["LON", "LAT", G2])
	df.to_csv(Savefilepath, index=None)

def OutputPng(data, lon, lat, G2, Savefilep):
	## prepare vars
	LON, LAT, DATA = data[0], data[1], data[2]
	xmin, xmax     = lon[0], lon[1]
	ymin, ymax     = lat[0], lat[1]
	## get draw area
	plons = np.where((xmin<=LON) & (LON<=xmax), 1, 0)          # if within⇒1, not within⇒0
	plats = np.where((ymin<=LAT) & (LAT<=ymax), 1, 0)          # if within⇒1, not within⇒0
	DATA  = DATA * plons * plats                               # within⇒DATA, not within⇒0
	plat, plon = [], []
	for i in range(0, DATA.shape[0]):
		if np.sum(DATA[i,:]) != 0:
			plat.append(i)
	for i in range(0, DATA.shape[1]):
		if np.sum(DATA[:,i]) != 0:
			plon.append(i)
	LON  = LON[plat, :][:,plon]
	LAT  = LAT[plat, :][:,plon]
	DATA = DATA[plat, :][:,plon]
	## draw
	Sx, Sy = Scale(lon, lat)
	plt.rcParams["figure.figsize"] = [Sy,Sx]
	plt.rcParams["font.size"] = 20
	fig = plt.figure()
	ax = fig.add_subplot(111)
	pp = ax.pcolormesh(LON, LAT, DATA, cmap="rainbow",
						shading="gouraud", norm=LogNorm())
	cbar = fig.colorbar(pp, ax=ax)
	cbar.set_label(G2)
	plt.xlabel("LON")
	plt.ylabel("LAT")
	plt.savefig(Savefilep, bbox_inches="tight")
	plt.close()

#######################################################################################
#                                    shp processing
#######################################################################################
def ReadShp():
	shplist = os.listdir("./SHP")
	area = []
	for shp in shplist:
		shpfile = glob.glob(f"./SHP/{shp}/*.shp")[0]
		shpdata = gpd.read_file(shpfile)
		shpdata = cascaded_union(shpdata.geometry)
		area.append([shp, shpdata])
		RemakeFolder(f"./OUTPUT/PIP/{shp}")
	return area

def PIP(shpname, shpdata):
	files = glob.glob("./OUTPUT/CSV/*.csv")
	for file in files:
		filename = file.split("/")[-1]
		data = pd.read_csv(file)
		data["Inarea"] = 0
		data = gpd.GeoDataFrame(data,geometry=gpd.points_from_xy(data.LON,data.LAT))
		data = data.set_crs("EPSG:4326")
		for point in range(0, data.shape[0]):
			if shpdata.contains(data.loc[point,"geometry"])==True:
				data.loc[point,"Inarea"] = 1
		pipdata = data[data["Inarea"]==1].drop(["Inarea","geometry"], axis=1)
		pipdata.to_csv(f"./OUTPUT/PIP/{shpname}/{filename}", index=None)


#######################################################################################
#                                       MAIN
#######################################################################################
if __name__ == "__main__":
	from init import *
	OutputInit()                                             # output initial condition
	# mode : 0:ダウンロードのみ，1:データ処理のみ，2:ダウンロード・データ処理
	if mode!=1:
		MakeFolder()                                         # prepare output folder
		print("accessing ftp server...", end=""  )           # access ftp server
		ftp = FTP(host=host, user=user, passwd=pw)
		print("\rOK, accessed ftp server        ")
		Satelite, FileList = MakeFileList(start, end, delta) # download files list
		Satelite = GetSateliteVarsion(ftp, Satelite)         # get satelite version
		## download files from ftp
		filenames = []
		for File in FileList:
			filename = DownloadFile(ftp, File, Satelite)
			filenames.append(filename)
		print("Finish, closed ftp server")
		ftp.quit()                                        # close ftp server
	else:
		print("Not download files mode")
		filenames = os.listdir("./OUTPUT/ROW/")
	
	## Read download files, output as csv
	if mode!=0:
		print("Start to output csv(png)")
		for filename in filenames:
			file      = "./OUTPUT/ROW/" + filename                        # get filename (.h5 filename)
			Savefilec = "./OUTPUT/CSV/" + filename.replace(".h5", ".csv") # get filename (to save csv)
			Savefilep = "./OUTPUT/PNG/" + filename.replace(".h5", ".png") # get filename (to save png)
			data, Ele, ElementNum = ReadRowFile(file, ElementNum)         # read file from h5 file
			OutputCsv(data, lon, lat, Ele, Savefilec)                     # output csv file
			OutputPng(data, lon, lat, Ele, Savefilep)                     # output png file

		## point in polygon
		print("Point In Polygon")
		shplist = ReadShp()
		for shp in shplist:
			PIP(shp[0], shp[1])
	else:
		print("Not output csv(png) mode")



