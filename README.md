# GCOM-Cから得られるSSTの図化
## 目的 : GCOM-C.h5ファイルから任意の範囲のデータを抽出・図化

## 利用方法
### 0. G-Poralからデータをダウンロードする   
	登録はこちらから⇒ https://gportal.jaxa.jp/gpr/?lang=ja  

### 1. 前準備  
#### 1. DATAフォルダの中にダウンロードした処理したいh5ファイルを置く   
- ※ファイルリストを作ることができればなんでもいいです。   
#### 2. init.pyを編集する   
- 詳細はinit.pyの中に書いてあります。  
#### 3. shpファイルを準備する  
- 背景地図に利用するshpファイルを準備  
	⇒./SHP/GROUND/フォルダにshpファイルを一つだけ入れる．いらない場合は何も入れない  
- Point in polygonで利用するshpファイルを準備  
	⇒shpファイルが格納されたフォルダをそのまま入れる  
	　このフォルダ名が出力時に利用される(出力結果を参照)  
		例）./SHP/PIP/Area1/area1.shp, ./SHP/PIP/Area2/area2.shp  

### 2. 実行
#### 1. 出力結果の説明  
出力ファイルはすべてOUTPUTに保存されます  
- OUTPUT/CSV       : 指定範囲内のポイントデータがまとめられたcsvファイルが保存される
- OUTPUT/PIP/AreaX : SHP/PIPに入れたshpのPoint in Polygonの結果が保存される．この時のAreaX(フォルダ名)はSHP/PIPと同じ
- OUTPUT/PNG       : 指定範囲内を描画したpngが保存される．












