
import sys
import numpy as np
import pandas as pd

class SearchIndex():
	"""
	抽出
	"""
	def __init__(self, SearchRange, SearchValue, XYname, mode):
		"""
		SearchRange : 対象グリッドのX,Yを含むDataFrame
		SearchValue : 検索地点の[X,Y]
		mode        : 補間方法(1:最近傍、2:重み月平均)
		"""
		self.SearchRange	= SearchRange
		self.SearchValue	= SearchValue
		self.XYname			= XYname
		self.mode			= mode
	
	def NearestSearch(self):
		""" 最近傍の検索 """
		### カラム
		Xc	= self.XYname[0]
		Yc	= self.XYname[1]
		### 距離を計算
		Xdiff	= np.array(self.SearchRange.loc[:,Xc]) - self.SearchValue[0]
		Xdiffs	= np.abs(Xdiff**2)
		Ydiff	= np.array(self.SearchRange.loc[:,Yc]) - self.SearchValue[1]
		Ydiffs	= np.abs(Ydiff**2)
		dis		= np.sqrt(Xdiffs**2 + Ydiffs**2)
		dismin	= np.nanmin(dis)
		return np.where(dis==dismin)

	def WeightSearch(self):
		""" 重み月平均の検索 """
		print("未実装です。")
		return 0
	
	def check_XY_col(self):
		if self.XYname[0] not in list(self.SearchRange.columns):
			print("SearchRangeのheaderに'X'がありません。\nプログラムを終了します。")
		if self.XYname[1] not in list(self.SearchRange.columns):
			print("SearchRangeのheaderに'Y'がありません。\nプログラムを終了します。")


	def run(self):
		### データの確認
		self.check_XY_col()
		if self.mode == 1:
			ind = self.NearestSearch()
			return ind[0][0]
		elif self.mode == 2:
			ind = self.WeightSearch()
		