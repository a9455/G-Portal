
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
import matplotlib
import matplotlib.pyplot as plt
from shapely.ops import cascaded_union

####################################################################################
#                                      common
####################################################################################
def Cmap(cols):
	nmax = float(len(cols)-1)
	color_list = []
	for n, c in enumerate(cols):
		color_list.append((n/nmax, c))
	return matplotlib.colors.LinearSegmentedColormap.from_list('cmap', color_list)

def mkdir(path):
	if os.path.exists(path)==False:
		os.makedirs(path)

def RemakeFolder(path):
	if os.path.exists(path)==True:
		shutil.rmtree(path)
	os.makedirs(path)

def ReContents(contents, ELEMENT):
	if ELEMENT != "ALL":
		for cont in contents:
			if cont[1] == ELEMENT:
				content = cont
				break
		contents = content
	return contents

def Interpolation(point:list):
	"""Object : 内挿補間(BILINEAR)\n
	point : [左上，右上，左下，右下]\n
	CONTENTS :\n
	STEP1 : Make New Grid\n
	STEP2 : processing(BILINEAR)\n
	"""
	## STEP1 : Make New Grid
	NG  = np.zeros((11,11))
	NGc = [[0,0], [0,10], [10,0], [10,10]]  # New Grid corner
	## STEP2 : processing
	NG[0,0], NG[0,10], NG[10,0], NG[10,10] = point[0], point[1], point[2], point[3]
	for i in range(0, NG.shape[0]):
		for f in range(0, NG.shape[1]):
			if [i,f] not in NGc:
				dx, dy = f/10, i/10
				Ax = (1-dx) * (1-dy) * NG[0,0]
				Bx = dx     * (1-dy) * NG[0,10]
				Cx = (1-dx) * dy     * NG[10,0]
				Dx = dx     * dy     * NG[10,10]
				NG[i,f] = Ax + Bx + Cx + Dx
	return NG[:10,:10]

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

class DataProcess():
	def  __init__(self, Resetfolder, XLIM, YLIM, Element, cmap):
		self.Refolder= Resetfolder
		self.XLIM    = XLIM
		self.YLIM    = YLIM
		self.Element = Element # データ種別
		self.cmap    = cmap    # cmap
		self.dpflag  = 0       # 緯度経度の展開を判断するフラグ(0:する、1:しない)
		self.Workdir = "./tmp"
		self.GROUNDs, self.PIPs = ShpProcess()   # read shp files

		## Reset folder
		if self.Refolder == "Yes":
			RemakeFolder("./OUTPUT/CSV")
			RemakeFolder("./OUTPUT/PNG")
			RemakeFolder("./OUTPUT/PIP")
		else:
			mkdir("./OUTPUT/CSV")
			mkdir("./OUTPUT/PNG")
			mkdir("./OUTPUT/PIP")
		pass

	#################################################################################
	#                           Read dataset from hdf5 
	#################################################################################
	def GetAttributesInfo(self, Name="COMMON"):
		"""
		hdf5データからメタ情報を読み取る関数\n
		hdf5  : hdf5 data\n
		GName : target attribute\n
		spath : save path\n
		"""
		attr = self.hdf5.attrs
		keys = attr.keys()
		if Name == "COMMON":
			Name = "COMMON"
		else:
			Name = Name
		with open(f"./{self.Workdir}/{self.G1}/{Name}.csv", "w") as file:
			for key in keys:
				cont = str(attr[key][0]).replace("b'", "").replace("'", "").replace(",", " ")
				file.write(f"{key},{cont}\n")

	def GetDatasetInfo(self):
		data = np.array(self.hdf5)
		np.save(f"./{self.Workdir}/DATA/{self.G2}.npy", data)

	def READ(self, filepath):
		RemakeFolder(self.Workdir)            # フォルダの初期化
		mkdir(f"./{self.Workdir}/DATA")
		hdf5      = h5py.File(filepath, 'r')  # hdf5ファイルの読み込み
		GROUP1    = list(hdf5.keys())         # 一番浅い階層のグループ名を取得
		CONTENTS  = []                        # 変数名の箱
		for self.G1 in GROUP1:
			mkdir(f"{self.Workdir}/{self.G1}")
			self.hdf5 = hdf5[self.G1]
			self.GetAttributesInfo()                # 階層全般のメタ情報を取得
			GROUP2 = list(self.hdf5.keys())         # 2番目の階層にあるグループ名を取得
			for self.G2 in GROUP2:
				self.hdf5 = hdf5[self.G1][self.G2]
				CONTENTS.append([self.G1, self.G2])
				self.GetAttributesInfo(self.G2)     # 階層全般のメタ情報を取得
				self.GetDatasetInfo()               # 数値データの取得
		hdf5.close()
		return CONTENTS

	#################################################################################
	#                               data processing
	#################################################################################
	def EditGeometry(self):
		mkdir(self.SaveDirC)
		## STEP0 : Load data
		lat  = np.load(f"{self.Workdir}/DATA/Latitude.npy")
		lon  = np.load(f"{self.Workdir}/DATA/Longitude.npy")
		data = np.load(f"{self.Workdir}/DATA/{self.cont[1]}.npy")

		## STEP1 : reshape
		lat  = np.reshape(lat,  ((lat.shape[0]  * lat.shape[1]  ,1)))
		lon  = np.reshape(lon,  ((lon.shape[0]  * lon.shape[1]  ,1)))
		data = np.reshape(data, ((data.shape[0] * data.shape[1] ,1)))
		## STEP2 : within range
		# Edit(Update) coor limit
		if self.XLIM==[-9999,-9999]:
			XLIM = [np.nanmin(lon), np.nanmax(lon)]
		else:
			XLIM = self.XLIM
		if self.YLIM==[-9999,-9999]:
			YLIM = [np.nanmin(lat), np.nanmax(lat)]
		else:
			YLIM = self.YLIM
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
		res = pd.DataFrame(res, columns=["LAT", "LON", self.cont[1]])
		res.to_csv(f"./OUTPUT/CSV/{self.cont[1]}/{self.filename}.csv", index=None)

	def OutputCsv(self):
		## replace
		lat  = np.reshape(self.lat,  ((self.lat.shape[0]  * self.lat.shape[1],  1)))
		lon  = np.reshape(self.lon,  ((self.lon.shape[0]  * self.lon.shape[1],  1)))
		data = np.reshape(self.data, ((self.data.shape[0] * self.data.shape[1], 1)))
		df   = np.append(lat, lon,  axis=1)
		df   = np.append(df,  data, axis=1)
		self.df   = pd.DataFrame(df, columns=["LAT", "LON", self.cont[1]])
		self.df.to_csv(f"./OUTPUT/CSV/{self.cont[1]}/{self.filename}.csv", index=None)
	
	def PIP(self):
		## Prepare
		ShpName, Shpdata = self.shp[0], self.shp[1]
		## Main
		data = gpd.GeoDataFrame(self.df,
								geometry=gpd.points_from_xy(self.df.LON, self.df.LAT))
		data = data.set_crs("EPSG:4326")
		col  = list(data.columns)
		SaveFolder = f"./OUTPUT/PIP/{self.cont[1]}/{ShpName}"
		mkdir(SaveFolder)
		with open(f"{SaveFolder}/{self.filename}.csv", "w") as output:
			output.write(f"{col[0]},{col[1]},{col[2]}\n")
			for point in range(0, data.shape[0]):
				if Shpdata.contains(data.loc[point,"geometry"])==True:
					lon, lat = str(data.loc[point,col[0]]), str(data.loc[point,col[1]])
					ele      = str(data.loc[point,col[2]])
					output.write(f"{lon},{lat},{ele}\n")

	def EditImage(self):
		"""Object : データ変換及び取得範囲の設定\n
		filename : filename
		self.cont: variables list [G1, G2]\n
		XLIM     : Lon. range [min, max]\n
		YLIM     : Lat. range [min, max]\n
		CONTENTS:\n
		STEP1 : Convert data\n
		STEP2 : Extract the specified range of data\n
		STEP3 : Interpolation Coor.\n
		"""
		mkdir(self.SaveDirC)                        # prepare output folders
		## STEP0 : Load data
		lat  = np.load(f"{self.Workdir}/DATA/Latitude.npy")
		lon  = np.load(f"{self.Workdir}/DATA/Longitude.npy")
		data = np.load(f"{self.Workdir}/DATA/{self.cont[1]}.npy")
		## 処理対象が2次元ならば。。。
		if len(data.shape) == 2:
			info = pd.read_csv(f"{self.Workdir}/{self.cont[0]}/{self.cont[1]}.csv", index_col=0, header=None)
			offset, slope = float(info.loc["Offset",info.columns[0]]), float(info.loc["Slope",info.columns[0]])
			FillRange     = [float(info.loc["Minimum_valid_DN",info.columns[0]]), float(info.loc["Maximum_valid_DN",info.columns[0]])]
			## STEP1 : Convert data
			data = np.where((FillRange[0]<=data) & (data<=FillRange[1]), data*slope+offset, -999)
			if self.dpflag ==0:   ## データ処理は一回目だけでいいはず
				## STEP2 : Extract the specified range of data
				# Edit(Update) coor limit
				if self.XLIM==[-9999,-9999]:
					XLIM = [np.nanmin(lon), np.nanmax(lon)]
				else:
					XLIM = self.XLIM
				if self.YLIM==[-9999,-9999]:
					YLIM = [np.nanmin(lat), np.nanmax(lat)]
				else:
					YLIM = self.YLIM
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
				self.dxL, self.dyL = dxL, dyL
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
				self.lat  = LAT
				self.lon  = LON
			elif self.dpflag ==1:
				data = data[self.dyL[0]*10:(self.dyL[1]-1)*10, self.dxL[0]*10:(self.dxL[1]-1)*10]
			self.dpflag = 1
			self.data = data
			self.OutputCsv()
			for self.shp in self.PIPs:
				self.PIP()
			if self.XLIM != [-9999,-9999] and self.YLIM != [-9999,-9999]:
				self.OutputPng()
				del self.data  # 念のため変数削除(次のデータに持ち越さないため)
			
	#################################################################################
	#                                    Draw
	#################################################################################
	def SetParams(self):
		## figure size
		degX, degY = self.XLIM[1] - self.XLIM[0], self.YLIM[1] - self.YLIM[0]
		if degX >= degY:
			figx, figy = 12, degY/degX*12
		else:
			figx, figy = degX/degY*12, 12
		self.figX, self.figY = figx, figy
		## cmap
		if self.cmap == None:
			self.CMAP="rainbow"
		else:
			self.CMAP=Cmap(self.cmap)
		## xticks
		self.xticks = np.linspace(self.XLIM[0], self.XLIM[1], 5)
		self.yticks = np.linspace(self.YLIM[0], self.YLIM[1], 5)
		

	def OutputPng(self):
		## prepare
		mkdir(self.SaveDirP)
		self.SetParams()
		## DRAW
		fig = plt.figure(figsize=(self.figX, self.figY), dpi=250)
		ax = fig.add_subplot(111)
		## COUNTOR PLOT
		data = self.data + 0
		nand = np.where(data==-999 , 99999,           self.data)
		data = np.where(nand==99999, np.nanmin(nand), self.data)
		if self.Element[0] == "ALL":
			Vmin, Vmax = np.nanmin(data), np.nanmax(data)
		else:
			Vmin, Vmax = self.Element[1], self.Element[2]
		contour = ax.pcolormesh(self.lon, self.lat, data, edgecolor="none",
								cmap=self.CMAP, vmin=Vmin, vmax=Vmax, shading="gouraud", zorder=1)
		bar     = fig.colorbar(contour, ax=ax, ticks=np.linspace(Vmin,Vmax, 5), shrink=0.3)
		## SHP PLOT
		if self.GROUNDs[0] == "Exists data":
			self.GROUNDs[1].plot(ax=ax, facecolor="k", edgecolor="none", zorder=2)
		plt.xticks(self.xticks, rotation=45)
		plt.yticks(self.yticks, rotation=45)
		plt.xlim(XLIM)
		plt.ylim(YLIM)
		plt.savefig(f"./OUTPUT/PNG/{self.cont[1]}/{self.filename}.png", bbox_inches="tight")
		plt.close()

	#################################################################################
	#                                   COMMON
	#################################################################################
	def MoveFiles(self):
		## get folder name
		DIR = []
		dir1 = os.listdir(self.Workdir)
		for dirx in dir1:
			dir2 = os.listdir(f"{self.Workdir}/{dirx}")
			for dirx2 in dir2:
				if dirx != "DATA":
					dir2x = dirx2.replace(".csv","")
					if dir2x == "COMMON":
						DIR.append([dirx, dirx2, dirx])
					else:
						DIR.append([dirx, dirx2, dir2x])
		## move files
		for dirx in DIR:
			mkdir(f"./OUTPUT/ATTRIBUTES/{dirx[2]}")
			shutil.move(f"{self.Workdir}/{dirx[0]}/{dirx[1]}",
						f"./OUTPUT/ATTRIBUTES/{dirx[2]}/{self.filename}.csv")
		
	#################################################################################
	#                                    Main
	#################################################################################
	def ProcessHDF5File(self, filepath):
		self.filename = filepath.split("/")[-1].split(".")[0]
		contents = self.READ(filepath)
		contents = ReContents(contents, self.Element[0])  # select contents
		self.dpflag = 0    # 緯度経度を展開するのかのフラグ(処理するのは1つのファイルにつき一回でいいよね)
		for self.cont in contents:
			self.SaveDirC = f"./OUTPUT/CSV/{self.cont[1]}"
			self.SaveDirP = f"./OUTPUT/PNG/{self.cont[1]}"
			if self.cont[0] == "Geometry_data":
				if "Lat"  in self.cont[1] or "Lon"  in self.cont[1]: # 緯度経度の時は出力しない(意味がないから)
					pass
				else:
					self.EditGeometry()              # Geometry_dataに対する処理
			elif self.cont[0] == "Image_data":
				self.EditImage()                     # Image_dataに対する処理(CSV出力, PIP出力, PNG出力)
		self.MoveFiles()                             # 属性情報を移動
		shutil.rmtree(self.Workdir)                  # ワーキングディレクトリの削除
		del self.dxL, self.dyL, self.lat, self.lon   # 念のため変数削除(次に持ち越さない)


if __name__ == "__main__":
	from init import *
	IDATA = DataProcess(FolderInitialization, XLIM, YLIM, Element, cmap)
	count = 1
	for filepath in filelist:
		print(f"{count} / {len(filelist)}")
		IDATA.ProcessHDF5File(filepath)
		count += 1




