import os
import glob

##############################################################################################
#                                        parameter
##############################################################################################
Ele    = [0,1,8]
slope  = 0.0012
offset = -10.0
vmin   = -5
vmax   = 35
XLIM   = [120, 125]
YLIM   = [8, 13]
cmap   = None


###  PLEASE MAKE FILELIST  ###
filelist = glob.glob("./DATA/*.h5")




"""
〇　パラメータ説明
Ele    : 要素番号[緯度，経度，データ]
         既知の場合 ⇒ 要素番号のリストを作成する
	     未知の場合 ⇒ わからない要素番号に-1を入れたリストを作成する
slope  : データ変換用の定数[傾き]
offset : データ変換用の定数[切片]
		 ※slopeとoffsetの定数は"https://shikisai.jaxa.jp/faq/docs/GCOM-C_FAQ_DNconversion_en_200422.pdf"から引用
vmin   : 描画時の最小値
vmax   : 描画時の最大値
XLIM   : 経度の範囲  [min, max]
YLIM   : 緯度の範囲  [min, max]
cmap   : デフォルト⇒rainbow(None)
		 任意のカラーバーを作成したい場合は色のリストを作成する
		 例）["slateblue", "blue", "cyan", "lime", "lawngreen", "yellow", "tomato", "red"]

filelist : ファイルパスのリスト 

〇　備考
◆　XLIMとYLIMに関して．．．
全領域のデータが欲しい場合，XLIM，YLIMともに[-9999,-9999]とする
その場合，緯度経度の最小・最大値を自動取得しcsvファイルとして保存する
しかし，範囲が広大となり時間がかかるため，描画はしないようになっている
"""


##############################################################################################
#                                        output
##############################################################################################
print("------------------------------------------------------")
print(f"Element number     = {Ele[0]}, {Ele[1]}, {Ele[2]}")
print(f"Element slope      = {slope}")
print(f"Element offset     = {offset}")
print(f"Draw value range   = {vmin} - {vmax}")
print(f"Draw lon. range    = {XLIM[0]} - {XLIM[1]}")
print(f"Draw lat. range    = {YLIM[0]} - {YLIM[1]}")
print(f"color map list     = {cmap}")
print("------------------------------------------------------")