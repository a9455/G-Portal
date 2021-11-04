start   = [2021, 10, 28]
end     = [2021, 10, 29]
delta   = "D"
XLIM    = [-9999, -9999]
YLIM    = [-9999, -9999]
Dflag   = "yes"
cmap    = "rainbow"
Element = ["ALL", 0]
Rpath   = ["Rs_VN08", 0, 0.20]  # [要素名、バンドの最小、バンド最大]
Gpath   = ["Rs_VN05", 0, 0.13]  # [要素名、バンドの最小、バンド最大]
Bpath   = ["Rs_VN03", 0, 0.20]  # [要素名、バンドの最小、バンド最大]
## ファイル名用パラメータ(参考：Handbook1, P56あたり)
# year , month, dayはstart, endで設定
Satelite   = "GC1"
Sensor     = "SG1"
A_D        = "D"    # 衛星進行方向 [A, D]のいずれか
Ptu        = "01D"  # 統計データ日数("01D"：1日, "08D"：8日, "01M"：一月)
Mapping    = "T"    # 投影法 [T:Tail]
TileNoList = ["0528"]
Level      = "L2"   # 処理レベル
Type       = "SG"   # 処理プロダクト(ほぼ固定)
ProductID  = "RSRF" # プロダクトID
Resolution = "Q"    # 分解能[K：1000m, Q:250m, F:1/24deg, C:1/12deg]
AlgoVer    = "2"    # アルゴリズムバージョン？
ppp        = "000"  # パラメータバージョン？