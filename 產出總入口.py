# -*- coding: utf-8 -*-
r"""從 `製作完成區\` 掃出所有單元，把資料注入 index.html 的 `const 資料 = __資料__;`。

用法：
    python 產出總入口.py            # 只掃第一學期（預設）
    python 產出總入口.py --全部     # 兩個學期都掃

🛑 **`index.html` 裡的資料是產生出來的，不要手動編輯。**
   新增單元、改了網址或圖卡張數，重跑本腳本即可。

🛑 **統計數字一律「數實體檔案」，不是解析 data.js 的字串**（2026-08-15 通則：
   印出來的數字必須是數出來的）。`data.js` 有兩種寫法（早期 key 沒加引號），
   而且正則很容易多抓（`"詞":` 會命中別的欄位）——
   所以頁數與圖卡數改成數 `assets/pages/*.webp` 與 `assets/cards/*_front.webp`，
   題數才用 `題頁` 計數（那個 key 只出現在評量物件裡）。
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))          # 製作完成區\_教材總入口
完成區 = os.path.dirname(ROOT)

# 領域顯示順序與樣式（新增領域時補這三張表）
序 = {"自然": 1, "社會": 2, "數學": 3, "語文": 4, "健體": 5,
     "綜合": 6, "藝文": 7, "特需生活管理": 8, "特需功能性動作訓練": 9}
# 封面檔名用的英文代碼（與 生成封面.py 的 `檔名()` 必須一致）
代碼 = {"自然": "nature", "社會": "society", "數學": "math", "語文": "chinese",
      "健體": "pe", "綜合": "life", "藝文": "arts",
      "特需生活管理": "selfcare", "特需功能性動作訓練": "motor"}
圖 = {"自然": "🌱", "社會": "🏮", "數學": "📐", "語文": "📖", "健體": "🏃",
     "綜合": "🌏", "藝文": "🎨", "特需生活管理": "🏠", "特需功能性動作訓練": "🤸"}
色 = {"自然": "#3f9142", "社會": "#c0562e", "數學": "#3a6ea8", "語文": "#8a5a2b",
     "健體": "#c2410c", "綜合": "#2f8f8f", "藝文": "#9333a8",
     "特需生活管理": "#b8860b", "特需功能性動作訓練": "#4f5bd5"}


def 掃單元(樣式):
    out = []
    for d in sorted(glob.glob(os.path.join(完成區, 樣式))):
        名 = os.path.basename(d)
        m = re.match(r"(.+?)_(第.學期)_第(\d+)單元_(.+)$", 名)
        if not m:
            continue
        領域, 學期, 序號, 單元 = m.group(1), m.group(2), int(m.group(3)), m.group(4)

        # 🛑 沒有線上網址就不要放進入口頁——放了會是死連結
        p = os.path.join(d, "線上網址.txt")
        if not os.path.exists(p):
            print("   ⚠️ 跳過（沒有 線上網址.txt）：%s" % 名)
            continue
        t = open(p, encoding="utf-8", errors="replace").read()
        mm = re.search(r"https://[a-z0-9.-]+/[a-z0-9-]+/", t)
        if not mm:
            print("   ⚠️ 跳過（線上網址.txt 裡找不到網址）：%s" % 名)
            continue

        站 = os.path.join(d, "教學網站")
        頁 = len(glob.glob(os.path.join(站, "assets", "pages", "*.webp")))
        卡 = len(glob.glob(os.path.join(站, "assets", "cards", "*_front.webp")))
        dj = os.path.join(站, "js", "data.js")
        題, 週 = 0, ""
        if os.path.exists(dj):
            s = open(dj, encoding="utf-8", errors="replace").read()
            題 = len(re.findall(r'"?題頁"?\s*:', s))
            w = re.search(r'"?週次"?\s*:\s*"([^"]+)"', s)
            週 = w.group(1) if w else ""
            # 🔴 2026-08-15：舊單元的 `data.js` 有 4 筆把**單元標籤**填進週次欄
            #    （〈校園探險家〉「第2單元」、〈熱對物質的影響〉「第5單元」、
            #      〈重量〉「第 2 單元」、〈線對稱圖形〉「第五單元」）。
            #    照印會在卡片上與旁邊的「第 N 單元」標籤重複，看起來像出錯。
            #    🛑 **寧可留空也不要印一個不是週次的東西**——這一欄本來就是選填。
            #    判準：字串裡必須真的有「週」。
            if "週" not in 週:
                週 = ""
        # 封面圖：covers\<領域代碼><序號>[b].webp，沒有就留空（頁面會顯示純色底＋單元名）
        # 🛑 第二學期要加後綴 `b`（2026-08-16）：兩個學期的「領域＋序號」會撞號，
        #    例如藝文一上第 3 單元與藝文二下第 3 單元都算出 `arts03`。
        #    沒有這個後綴，二下的單元會去引用一上那張封面——**圖會顯示、但是錯的**，
        #    而且不會有任何錯誤訊息。命名規則見 生成封面.py 的 檔名()。
        後綴 = "b" if 學期 == "第二學期" else ""
        代號 = "%s%02d%s" % (代碼[領域], 序號, 後綴) if 領域 in 代碼 else ""
        封面 = ""
        if 代號 and os.path.exists(os.path.join(ROOT, "covers", 代號 + ".webp")):
            封面 = "covers/%s.webp" % 代號

        out.append(dict(領域=領域, 學期=學期, 序=序號, 單元=單元,
                        網址=mm.group(0), 週=週, 頁=頁, 題=題, 卡=卡, 封面=封面))
    return out


def main():
    樣式 = "*" if "--全部" in sys.argv else "*第一學期*"
    單元們 = 掃單元(樣式)
    assert 單元們, "🛑 一個單元都沒掃到，八成是路徑錯了（不要讓空清單變成成功）"

    未知 = {x["領域"] for x in 單元們} - set(序)
    assert not 未知, "🛑 這些領域還沒登記顯示順序／圖示／顏色：%s" % 未知

    # 🛑 兩個學期一起掃時要**先分學期再排序號**（2026-08-16）：
    #    只用序號排會變成 1、1、2、2、3、3… 一上二下交錯，
    #    而單元卡上只有封面與單元名（老師指定），看的人分不出哪張是哪個學期。
    #    這裡只動順序、不加任何標籤，維持「只有封面圖＋單元名」。
    群 = {}
    for x in sorted(單元們, key=lambda a: (序[a["領域"]], a["學期"], a["序"])):
        群.setdefault(x["領域"], []).append(x)
    資料 = [{"名": k, "圖": 圖[k], "色": 色[k],
            "單元": [{"序": u["序"], "名": u["單元"], "網址": u["網址"],
                    "封面": u["封面"]}
                   for u in v]}
          for k, v in sorted(群.items(), key=lambda a: 序[a[0]])]

    # 🛑 素材健檢仍要做（雖然數字不再顯示在頁面上）：0 代表素材沒建置或路徑錯
    壞 = [x["單元"] for x in 單元們 if not (x["頁"] and x["題"] and x["卡"])]
    assert not 壞, "🛑 這些單元的頁數／題數／圖卡數是 0，先查素材：%s" % 壞

    p = os.path.join(ROOT, "index.html")
    html = open(p, encoding="utf-8").read()
    新 = "const 資料 = %s;" % json.dumps(資料, ensure_ascii=False, indent=1)
    html2, n = re.subn(r"const 資料 = .*?;\n", 新 + "\n", html, count=1, flags=re.S)
    assert n == 1, "🛑 index.html 裡找不到 `const 資料 = …;` 這一行"
    open(p, "w", encoding="utf-8").write(html2)

    print("✅ 已寫入 index.html：%d 個領域／%d 個單元"
          % (len(資料), sum(len(d["單元"]) for d in 資料)))
    for d in 資料:
        有封面 = sum(1 for u in d["單元"] if u["封面"])
        print("   %s %s　%d 單元　封面 %d／%d%s"
              % (d["圖"], d["名"], len(d["單元"]), 有封面, len(d["單元"]),
                 "" if 有封面 == len(d["單元"]) else "　← 還沒生封面"))


if __name__ == "__main__":
    main()
