
import os
import glob
import shutil



class COMMON():
	def MakeFilelist(self):
		""" データ選別 """
		filelist = glob.glob(f"./{self.DataFolder}/*.h5")
		filelist = sorted(filelist)
		return filelist

	# フォルダ処理関係
	# --------------------------------------------------
	def mkdir(self, path):
		""" フォルダ作成 """
		if os.path.exists(path) == False:
			os.makedirs(path)

	def RemakeFolder(self, path):
		""" フォルダの再作成 """
		if os.path.exists(path)==True:
			shutil.rmtree(path)
		os.makedirs(path)
	
	def ResetOutFolder(self):
		""" 出力フォルダのリセット """
		## Reset folder
		if self.Refolder == "Yes":
			self.RemakeFolder("./OUTPUT/CSV")
			self.RemakeFolder("./OUTPUT/PNG")
			self.RemakeFolder("./OUTPUT/PIP")
		else:
			self.mkdir("./OUTPUT/CSV")
			self.mkdir("./OUTPUT/PNG")
			self.mkdir("./OUTPUT/PIP")
	
	def MoveFiles(self):
		""" データの移動 """
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
			self.mkdir(f"./OUTPUT/ATTRIBUTES/{dirx[2]}")
			shutil.move(f"{self.Workdir}/{dirx[0]}/{dirx[1]}",
						f"./OUTPUT/ATTRIBUTES/{dirx[2]}/{self.filename}.csv")



















