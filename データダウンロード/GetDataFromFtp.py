from params import *
import os
import datetime as dt
from dateutil.relativedelta import relativedelta
from ftplib import FTP

##########################################################################################
#                                       common
##########################################################################################
def MKDIR(path):
	if os.path.exists(path)==False:
		os.makedirs(path)

def AccessFtp(host, user, pw):
	print("access ftp server", end="")
	ftp = FTP(host=host, user=user, passwd=pw)
	print("\rOK, accessed                 ")
	return ftp

def DatetimeToElement(date):
	"""
	datetime型から年月日時を取得する
	年　　：4桁
	月日時：2桁
	"""
	year  = str(date.year)
	month = str(date.month).zfill(2)
	day   = str(date.day).zfill(2)
	hour  = str(date.hour).zfill(2)
	return year, month, day, hour

def MakeTimeList(start:list, end:list, delta):
	"""
	取得時間のリストを作成
	start : 取得開始時間
	end   : 取得終了時間
	"""
	print("Make File List", end="")
	Sdate = dt.datetime(*list(map(int,start.split("-"))))
	Edate = dt.datetime(*list(map(int,end.split("-"))))
	TimeList = []
	## 時間
	if delta == "H":
		while Sdate<=Edate:
			yy, mm, dd, hh = DatetimeToElement(Sdate)
			TimeList.append([yy, mm, dd, hh])
			Sdate = Sdate + dt.timedelta(hours=1)
	elif delta == "D":
		while Sdate<=Edate:
			yy, mm, dd, hh = DatetimeToElement(Sdate)
			TimeList.append([yy, mm, dd, hh])
			Sdate = Sdate + dt.timedelta(day=1)
	## 月
	elif delta == "M":
		while Sdate<=Edate:
			yy, mm, dd, hh = DatetimeToElement(Sdate)
			TimeList.append([yy, mm, dd, hh])
			Sdate = Sdate + relativedelta(months=1)
	print(f"  Total {len(TimeList)} times")
	return TimeList

def Download(ftp, DownloadFiles):
	for DownloadFile in DownloadFiles:
		filename = DownloadFile.split("/")[-1]
		try:
			with open(f"./OUTPUT/{filename}", "wb") as f:          # open file in local directory
				ftp.retrbinary('RETR %s' % DownloadFile, f.write)  # write
			print(f"\033[32m Get data, {filename}")
		# Error
		except Exception:  
			print(f"\033[31m Not data, {filename}")
			ftp.quit()

def GETDATAFROMFTP(host, user, pw, dtype, start, end, delta):
	MKDIR("./OUTPUT")
	TimeList = MakeTimeList(start, end, delta)                 # get time list
	ftp = AccessFtp(host, user, pw)                            # open and login ftp server
	DownloadFiles = MakeDownloadFileList(ftp, TimeList, dtype) # Make Download list
	Download(ftp, DownloadFiles)                               # Download
	ftp.quit()

if __name__=="__main__":
	# L62:MakeDownloadFileList(ftp, TimeList, dtype)を何とかする
	GETDATAFROMFTP(host, user, pw, dtype, start, end, delta)