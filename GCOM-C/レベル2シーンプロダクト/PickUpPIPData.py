
import os
import sys
import glob
import shutil
import numpy as np
import pandas as pd
import datetime as dt


#sys.path.append("")		# searchgridpointindex.pyを置いたフォルダパス
from pysrc.searchgridpointindex import *


class PickUpPIPData():
	def __init__(self):
		### 対象範囲のデータ
		self.AreaShpName    = "tmp"
		self.ElementList	= ["SST"]
		self.ColXYName		= {
			"X" : "LON",
			"Y" : "LAT",
		}
		### 抽出対象のデータ
		self.PointCsvFile   = "./saseboObsPoint.csv"
		self.ResultColList	= {
			"X"		: "X",
			"Y"		: "Y", 
			"Label" : "LOCATIONNA"
		}
		### 出力
		self.DataFolder = "./OUTPUT/PIP"
		self.OutFolder	= "./OUTPUT/PIPPoint"

	# 汎用
	# --------------------------------------------------
	def mkdir(self, path):
		if os.path.exists(path) == True:
			shutil.rmtree(path)
		os.makedirs(path)

	def make_load_pip_csv_file_list(self):
		self.PIPCsvList		= sorted(glob.glob(f"{self.DataFolder}/{self.ElementList[0]}/{self.AreaShpName}/*.csv"))

	# データ読み込み
	# --------------------------------------------------
	def read_pip_csv(self, filepath):
		date	= filepath.split("/")[-1].split("_")[1]
		year	= int(date[:4])
		month	= int(date[4:6])
		day		= int(date[6:8])
		hour	= int(date[8:10])
		minite	= int(date[10:12])
		return dt.datetime(year, month, day, hour, minite), pd.read_csv(filepath, index_col=None)

	# 抽出したいポイントデータ
	def read_target_point_csv(self):
		data	= pd.read_csv(self.PointCsvFile, index_col=None)
		Label	= list(data.loc[:,self.ResultColList["Label"]])
		return data, Label

	def check_col_List(self, data):
		Columns	= list(data.columns)
		col		= self.ResultColList["X"]
		if col not in Columns:
			print(f"{self.PointCsvFile}のにHeaderに'{col}'が存在しません。\nプログラムを終了します。")
		col		= self.ResultColList["Y"]
		if col not in Columns:
			print(f"{self.PointCsvFile}のにHeaderに'{col}'が存在しません。\nプログラムを終了します。")

	# メイン
	# --------------------------------------------------
	def run(self):
		### カラムの整理
		PcolX	= self.ColXYName["X"]
		PcolY	= self.ColXYName["Y"]
		TcolX	= self.ResultColList["X"]
		TcolY	= self.ResultColList["Y"]
		self.make_load_pip_csv_file_list()						# 処理するファイルパスのリストを作成
		TargetPoint, Labels	= self.read_target_point_csv()		# 抽出したいポイントファイル
		
		### ファイルの初期設定
		OutInit	= "Label"
		for Label in Labels:
			OutInit += f",{Label}"
		OutInit += "\nX"
		for x in list(TargetPoint.loc[:,TcolX]):
			OutInit += f",{x}"
		OutInit += "\nY"
		for y in list(TargetPoint.loc[:,TcolY]):
			OutInit += f",{y}"
		OutInit += "\n"

		LogInit	= "Label"
		for Label in Labels:
			if Label == Labels[-1]:
				LogInit += f",{Label}\n"
			else:
				LogInit += f",{Label},"
		LogInit += "XY"
		for i in range(0, TargetPoint.shape[0]):
			LogInit += f",{TargetPoint.loc[i,TcolX]}"
			LogInit += f",{TargetPoint.loc[i,TcolY]}"
		LogInit += "\n"


		self.mkdir(self.OutFolder)
		for Element in self.ElementList:
			OutFile	= open(f"{self.OutFolder}/{Element}.csv", "w", encoding="shift-jis")
			LogFile	= open(f"{self.OutFolder}/{Element}_Log.csv", "w", encoding="shift-jis")
			OutFile.write(OutInit)
			LogFile.write(LogInit)

			for filepath in self.PIPCsvList:						# 各出力ファイル
				
				date, SearchRange	= self.read_pip_csv(filepath)	# データ読み込み
				SearchRange			= SearchRange[SearchRange[Element] != -999]
				SearchRange.index	= range(0, SearchRange.shape[0])
				OutFile.write(str(date))
				LogFile.write(str(date))
				
				if SearchRange.shape[0] < 1:
					pass
				else:
					for i in range(0, TargetPoint.shape[0]):			# 各抽出地点のループ
						XY	= [
							float(TargetPoint.loc[i,TcolX]),
							float(TargetPoint.loc[i,TcolY]),
						]
						ind	= SearchIndex(SearchRange, XY, [PcolX,PcolY], 1).run()
						"""
						print(
							"Index    = ", ind,
							"\nTarget X = ", XY[0],
							"\nRange  X = ", SearchRange.loc[ind,PcolX],
							"\nTarget Y = ", XY[1],
							"\nRange  Y = ", SearchRange.loc[ind,PcolY],
						)
						"""
						OutFile.write(f",{SearchRange.loc[ind,Element]}")
						LogFile.write(f",{SearchRange.loc[ind,PcolX]}")
						LogFile.write(f",{SearchRange.loc[ind,PcolY]}")

				OutFile.write("\n")
				LogFile.write("\n")
			OutFile.close()




if __name__ == "__main__":
	PickUpPIPData().run()










