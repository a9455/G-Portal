
import sys
import subprocess as sp

LinuxDis = sys.argv[1]

## python3-gdalのインストール
if LinuxDis == "Ubuntu":
    sp.call("sudo apt-get install -y python3-gdal", shell=True)
elif LinuxDis == "CentOS":
    sp.call("sudo yum install -y python3-gdal", shell=True)

## requirements.txtからPIPでインストール
with open("./requirements.txt", "r") as f:
    library = f.read().split("\n")
sp.call("pip install -r requirements.txt", shell=True)
