# GetDataFromFtp.py
### 概要
	ftpサーバーよりデータをダウンロードするコード

### 使い方
#### 1. params.pyの編集
```
host  : ftpサーバー
user  : user name
pw    : pass word
dtype : 要素先のパス(ftp)
start : ダウンロードの開始時間
end   : ダウンロードの終了時間
delta : タイムステップの幅

MakeDownloadFileListの作成
WinsCP等でリモートサーバーの構造を確認しながらこの部分を完成させる
初期はGSMaPに対応
```

#### 2. 実行
```
python GetDataFromFtp.py
```

#### 3. 実行後データがSavePathに保存される
	「Get data ...」と緑色でプリントされた場合：正常なダウンロード
	「Not data ...」と赤色でプリントされた場合：データが存在しないかダウンロードミス

