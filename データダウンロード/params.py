host       = "ftp.gportal.jaxa.jp"
user       = "id"
pw         = "pw"
dtype      = "standard/GCOM-C/GCOM-C.SGLI/L2.LAND.RSRF/2"
start      = "2021-01-01"
end        = "2021-01-02"
delta      = "H"


##  取得するデータファイル名を設定する関数
# 作成方法に記載されているファイルの取り方は動作確認をしていません、あくまで例です。
def MakeDownloadFileList(ftp, TimeList, dtype):
	getfiles = []
	for dd in TimeList:
		yy, mm, dd, hh = dd[0], dd[1], dd[2], dd[3]

		## 作成方法1 : 直接文字列を指定する.
		DownloadFile = f"{dtype}/{yy}/{mm}/{dd}/GPMMRG_MAP_{yy[2:]}{mm}{dd}{hh}00_H_L3S_MCH_F4(←衛星バージョン).h5"
		getfiles.append(DownloadFile)

		## 作成方法2 : リモートフォルダを検索しながら追加していく
		# ftp.nlst : os.listdir()のようにリモートフォルダ内のファイルを返す
		# ftp.dir  : 指定パス内のフォルダを返す
		path0 = f"{dtype}/{yy}/{mm}/{dd}/"
		files = ftp.nlst(path0)  # os.listdir()みたいな感じ←階層構造を再現しながら文字列をつなげていく
		for file in files:
			getfiles.append(f"{path0}/{file}")
			## このメソッドを使うと・・・
			# フォルダを検索しながらファイルを取得していくので、見落としが少なくなるのか？
			# if文による条件式とで取得ファイルを選別とかもできる
			# ⇒作成方法1では指定しないといけなかった衛星バージョンとかも一括指定できるのかな？
