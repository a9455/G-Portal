

from pysrc.common import *
import numpy as np
import h5py



class READ(COMMON):
	# HDF5(.h5)ファイルの読み込み
	# ---------------------------------------------------
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
		self.RemakeFolder(self.Workdir)				# フォルダの初期化
		self.mkdir(f"./{self.Workdir}/DATA")		# ./tmp/DATAの作成
		hdf5      = h5py.File(filepath, 'r')		# hdf5ファイルの読み込み
		GROUP1    = list(hdf5.keys())				# 一番浅い階層のグループ名を取得
		CONTENTS  = []								# 変数名の箱
		for self.G1 in GROUP1:
			self.mkdir(f"{self.Workdir}/{self.G1}")	# 変数名のフォルダを作成
			self.hdf5 = hdf5[self.G1]				# 変数データを読み込む
			self.GetAttributesInfo()                # 階層全般のメタ情報を取得
			GROUP2 = list(self.hdf5.keys())         # 2番目の階層にあるグループ名を取得
			for self.G2 in GROUP2:
				self.hdf5 = hdf5[self.G1][self.G2]
				CONTENTS.append([self.G1, self.G2])
				self.GetAttributesInfo(self.G2)     # 階層全般のメタ情報を取得
				self.GetDatasetInfo()               # 数値データの取得
		hdf5.close()
		return CONTENTS