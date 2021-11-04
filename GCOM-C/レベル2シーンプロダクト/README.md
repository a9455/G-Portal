# GCOM-C.h5の処理
### 取得項目：([詳しくは後述](#ActScript))
1. 指定範囲のcsvファイル[緯度、経度、特定のデータ]
2. 指定範囲の簡易的なpng画像(shpファイルがあれば、併記可能)
3. Point in Polygonを行ったcsvファイル[緯度、経度、特定のデータ]
4. ファイルのメタ(属性)データ

---
## 目次
1. [実行環境](#SetEnv)
2. [事前準備](#SetInit)
3. [実行・実行後の出力ファイル一覧](#ActScript)
4. [最後に．．．](#Final)





---
<a id="SetEnv"></a>

## 1. 実行環境

- Ubuntu == 20.04.3 LTS (Focal Fossa)
- python == 3.8.10
- instelled using pip
  	- numpy      == 1.19.5
  	- pandas     == 1.2.4
  	- geopandas  == 0.9.0
  	- matplotlib == 3.4.1
  	- shapely    == 1.7.1

-----------------------外部ライブラリの一括インストール方法-----------------------  
<span style="color: red; ">
python3をインストール済み，かつUbuntかCentOSを利用している方用です  
(Ubuntuは動作確認済みです、CentOSは意見ください．．．)  
</span>

1. ./Requirements pipを開く
2. python3 PIP.py "Linux distribution"  
	例) python3 PIP.py Ubuntu  
		Linux distribution : "Ubuntu" or "CentOS"  

 



---
<a id="SetInit"></a>

## 2. 事前準備
<a id="FolderTree"></a>

### はじめに : フォルダ構造
```
repositry ---- init.py
           |- Processing.py
           |- DATA?(これより深い階層はファイルパスが指定できればなんでもいいです)
           |- SHP --- GROUND --- Name.shp(ファイル名は自由，他の設定ファイルもここに置く)
           |       |- PIP    --- Area1(フォルダ名は自由) -- Name1.shp(ファイル名は自由, ※1)
           |                  |- Area2(フォルダ名は自由) -- Name2.shp(ファイル名は自由, ※1) 
           |                  |- 以降，複数設定可能
           |- OUTPUT(実行後作成される) --- CSV  --- 指定範囲内のcsv出力用フォルダ
                                   　　|- PNG  --- 指定範囲内のpng出力用フォルダ
                                   　　|- PIP  --- データ種別1--- Area1(PIPで作成したフォルダ名) -- PIP(Area1)のcsv出力用フォルダ
                                   　　|        |             |- Area2(PIPで作成したフォルダ名) -- PIP(Area2)のcsv出力用フォルダ
                                   　　|        |             |- 以降，SHP/PIPで作成したフォルダの数だけ作成される
                                   　　|        |- データ種別2--- Area1(PIPで作成したフォルダ名) -- PIP(Area1)のcsv出力用フォルダ
                                   　　|        |             |- Area2(PIPで作成したフォルダ名) -- PIP(Area2)のcsv出力用フォルダ
                                   　　|        |             |- 以降，SHP/PIPで作成したフォルダの数だけ作成される
                                　　   |        |- 以降，hdf5ファイルに格納されているデータ分だけ出力される
                                　　   | 
                                   　　|- INFO --- ファイルにある属性情報の分だけフォルダが作成される(ファイル名で管理) 

※1 shpファイルを置くところには他の設定ファイルも置く
```

### 2.0. G-Poralからデータをダウンロードする   
登録は[こちら](https://gportal.jaxa.jp/gpr/?lang=ja)  
別レポジトリにダウンロード用スクリプトを公開する予定です．   

### 2.1. init.pyを編集し，条件を設定  
   ```
	〇 出力フォルダを初期化する(異なるプロダクトのデータを利用する場合に使うかも．．)  
	FolderInitialization = 出力フォルダを初期化する("Yes")かしない("No")か  
	
	〇 XLIM, YLIMの指定範囲内のデータを処理(CSV変換，図化)する
	YLIM = 緯度[最小, 最大値]を指定  
	XLIM = 経度[最小, 最大値]を指定  
	
	〇 データ種別の設定
	Element = ファイルから取得するデータ種別を指定  
	          ◆ すべてのデータを出力したい場合は["ALL"]とする
                  ⇒ 図化時はデータの最小・最大値からカラーバーが決まる
              ◆ 特定のデータを指定したい場合は，["データ種別", "VMIN", "VMAX"]とする
                  ⇒ 図化時はVMIN・VMAXからカラーバーが決まる
	
	〇 カラーバーの設定
	cmap = 図示時のカラーマップを指定  
		Noneの場合は"rainbow"
		色のリストでも指定可能．例）["red", "blue", "green"]
	
	〇処理ファイルのリストを作成
	filelist = 処理したいファイルパスのリスト(フォルダ構造が様々だと思うので設定してください)
   ```
   
### 2.2. shpファイルの準備([フォルダ構造参照](#FolderTree))
#### 2.2.1. 図示時の背景図用shpファイル(任意)
SHP/GROUNDフォルダを作成し，図化に利用するshpファイルを<span style="color: red; ">一つだけ</span>置く
#### 2.2.2. PointInPolygon用(PIP)のshpファイル(任意)
SHP/PIPフォルダを作成し，PIPに利用するshpファイルを<span style="color: red; ">一つずつ</span>置く






---
<a id="ActScript"></a>

## 3. 実行・実行後の出力ファイル一覧
#### 0. 実行
```
python Processing.py
```
#### 1. OUTPUT/CSV  : 指定範囲のcsvファイル[緯度、経度、特定のデータ]
- XLIM, YLIMで設定した範囲内のデータが各hdf5ファイルごとにcsv出力される
- 欠損値：-999
#### 2. OUTPUT/PNG  : 指定範囲の簡易的なpng画像(shpファイルがあれば、併記可能)
- XLIM, YLIMで設定した範囲内のデータが各hdf5ファイルごとにpng出力される
- 欠損値：データの最小値と同じ色で出力(修正しないとなぁ．．)
#### 3. OUTPUT/PIP  : Point in Polygonを行ったcsvファイル[緯度、経度、特定のデータ]
- shpファイルで指定された領域範囲内のデータが各hdf5ファイルごとにcsv出力される
- 欠損値：-999
#### 4. OUTPUT/INFO : ファイルのメタ(属性)データ
- 属性値の一般情報(作成者等)
- slopeやOffset等の各属性値の詳細情報
- QAflagやObsTime等のデータ一覧






---
<a id="Final"></a>

## 4. 最後に．．．
レポジトリのダウンロードやcloneをするのは自由ですが，責任や保証は一切しません．