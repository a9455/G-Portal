# SSTの図化

## SSTを図化するためのコード

## 利用方法
1. parameterの設定  
    DrawChlorophyll.py、L193~198を設定する  
    vmin：カラーバーの最小値  
    vmax：カラーバーの最大値   
    shp ：利用するshpファイルのpath  
    XLIM：グラフの描画範囲[min, max]  
    YLIM：グラフの描画範囲[min, max]  
    cmap：Noneとすると"rainbow"，L194のように色を自由に設定することも可能    

2. データのファイルリスト(L135)の設定  
    図化したいファイルのパスのリストを作成する

## 出力される結果
PNGフォルダに"SST_ファイル名.png"という名前で画像が出力される  

