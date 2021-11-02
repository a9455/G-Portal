# Philippines

## GetDataFromFtp.py
### 概要
	ftpサーバーよりデータをダウンロードするコード

### 使い方
#### 1. params.pyの編集
```
host       : ftpサーバー
user       : user name
pw         : pass word
dir        : 要素先のパス(ftp)
TargetTail : 対象タイル
start   : 図化の開始時間
end     : 図化の終了時間
SavePath   : 保存先(local)
```

#### 2. ファイルリストを作成する
L61, MakeDownloadFileListの"for file in files"以降のスクリプトを作成する  
filesはos.listdir()と同じ結果を返してくるので、f"{dtype}/{yy}/{mm}/{dd}/"などとしてdtype以降のフォルダ構造を作成する(WinsCP等で事前に確認することをお勧めします)

#### 3. 実行後データがSavePathに保存される
	「Get data ...」と緑色でプリントされた場合：正常なダウンロード
	「Not data ...」と赤色でプリントされた場合：データが存在しないかダウンロードミス

