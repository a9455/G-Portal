# GSMaP処理スクリプト

## 目次
- [GSMaP](#gsmap)
  - [目次](#目次)
  - [1. 目的](#1-目的)
  - [2. 使い方](#2-使い方)
    - [2.0. G-Portalに登録し，ユーザー名，パスワードを取得する](#20-g-portalに登録しユーザー名パスワードを取得する)
    - [2.1. init.pyを編集](#21-initpyを編集)
    - [2.2. SHPファイルの準備](#22-shpファイルの準備)
    - [2.3. ファイルの実行](#23-ファイルの実行)
    - [2.4. 出力ファイルの説明](#24-出力ファイルの説明)




---
## 1. 目的
1. GSMaPデータのダウンロード  
2. hdf5から任意の領域のcsvに変換  
3. 任意の領域の図を出力  

---
## 2. 使い方
### 2.0. G-Portalに登録し，ユーザー名，パスワードを取得する  
   https://gportal.jaxa.jp/gpr/?lang=ja  

### 2.1. init.pyを編集  
   注意点 衛星のバージョンで以下が異なる場合、スクリプトの修正が必要  
   - ElementNumと緯度経度取得の部分を衛星のバージョンで変更するように修正する必要がある  
   ↑(更新しない場合は．)取得期間を合わせて，ElementNumを-1にすることで指定することができる  

   ``` 
   mode       : 0:ダウンロードのみ，1:データ処理のみ，2:ダウンロード・データ処理
   host       : ftpサーバーのホスト  
   user       : ユーザー名  
   pw         : パスワード  
   TargetFor  : 取得対象の拡張子(本コードはhdf5のみ対応)  
   lat        : 緯度[最小，最大]  
   lon        : 経度[最小，最大]  
   start      : 開始時間  [year, month, day, hour]
   end        : 終了時間  [year, month, day, hour]
   delta      : 時間解像度・・・H:時間, M:月
   ElementNum : データ種別  (init.py参照)
   ```
       

### 2.2. SHPファイルの準備  
   ./SHPフォルダの中にPoint In Polygonで利用したいshpファイルを準備する  
   ※ shpファイルはArea1, Area2...のようにフォルダに分けて準備する(ファイル名は任意)

### 2.3. ファイルの実行
   python GSMaP.py  
   ※図化に時間がかかる場合は緯度経度の範囲を小さくするか、図化部分を除く

### 2.4. 出力ファイルの説明
   OUTPUTフォルダに出力される  
   ```
   ./OUTPUT/ROW/**：ダウンロードしたh5ファイルの生データ  
   ./OUTPUT/CSV/**：ダウンロードしたh5ファイルから指定した緯度経度の範囲を抽出しcsvファイルとして保存  
   ./OUTPUT/PNG/**：ダウンロードしたh5ファイルから指定した緯度経度の範囲を抽出しpngファイルとして保存(簡易的)   
   ./OUTPUT/PIP/**：ダウンロードしたh5ファイルから2.で準備したSHPの範囲内のデータ抽出しcsvファイルとして保存  
   ```