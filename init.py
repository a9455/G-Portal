import glob



########################################################################
# READMEを見て設定してみてください
########################################################################

## parameter ##
FolderInitialization = "Yes"
YLIM                 = [10, 13]
XLIM                 = [123, 125]
Element              = ['ALL'] 
cmap                 = None
###  PLEASE MAKE FILELIST  ###
filelist = glob.glob("./DATA/*IWPRQ*.h5")

filelist = filelist + filelist


















print("----------------------  PARAMETER  ----------------------")
print(f"FolderInitialization = {FolderInitialization}")
print(f"lon range : {XLIM[0]} ~ {XLIM[1]}")
print(f"lat range : {YLIM[0]} ~ {YLIM[1]}")
print(f"Target element = {Element}")
print("---------------------------------------------------------")
