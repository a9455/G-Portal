import glob

## parameter ##
FolderInitialization = "No"
YLIM                 = [9, 15]
XLIM                 = [123.7, 123.9]
Element              = ['ALL'] 
cmap                 = None
###  PLEASE MAKE FILELIST  ###
#filelist = glob.glob("DATA DIRECTORY/*.h5")
filelist = glob.glob("./DATA/*IWPRQ*.h5")



"""
パラメータの説明
FolderInitialization : OUTPUTフォルダを初期化(ファイル削除含む)をする(Yes)かしない(No)かのフラグ
VLIM     : 図化するときの値　の最小・最大値
XLIM     : 図化するときの軽度の最小・最大値
YLIM     : 図化するときの緯度の最小・最大値
Element  : データ種別
            "ALL" : 格納されているすべてのデータを出力する
            ※ "CHLA"等、特定のデータを指定することも可能←特定のデータを選ぶ場合はValue Rangeを指定する
            例）　Element = ["CHLA", 0, 50]
cmap     : color map.デフォルト：rainbow(None)
filelist : フォルダ構造に沿って処理ファイルのリストを作成する
"""



print("----------------------  PARAMETER  ----------------------")
print(f"FolderInitialization = {FolderInitialization}")
print(f"lon   range : min={XLIM[0]} ~ max={XLIM[1]}")
print(f"lat   range : min={YLIM[0]} ~ max={YLIM[1]}")
print(f"Target element = {Element}")
print("---------------------------------------------------------")
