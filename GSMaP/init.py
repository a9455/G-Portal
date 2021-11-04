mode       = 1
host       = "ftp.gportal.jaxa.jp"
user       = "id"
pw         = "pw"
TargetFor  = ".h5"
lat        = [0, 20]
lon        = [100, 150]
start      = [2021, 10, 10, 10]
end        = [2021, 10, 10, 12]
delta      = "H"
ElementNum = 2

"""
-----------------以下メモ欄-----------------
〇 mode : 0:ダウンロードのみ，1:データ処理のみ，2:ダウンロード・データ処理
                
〇 ElementNumのデータ種別(04Fは確認済み)
-1 : データ内の略称名を見て決めたい方用
2  : Grid hourlyPrecipRate
3  : Grid satelliteInfoFlag
4  : Grid observationTimeFlag
5  : Grid hourlyPrecipRateGC
6  : Grid gaugeQualityInfo
7  : Grid snowProbability

"""