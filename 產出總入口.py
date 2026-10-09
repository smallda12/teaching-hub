# -*- coding: utf-8 -*-
r"""從 `製作完成區\` 掃出所有單元，把資料注入 index.html 的 `const 資料 = __資料__;`。

用法：
    python 產出總入口.py            # 只掃第一學期，寫入 115-1\index.html（預設）
    python 產出總入口.py --學期二   # 只掃第二學期，寫入 115-2\index.html
    python 產出總入口.py --全部     # 兩個學期都掃，寫入根目錄 index.html（舊版合併頁，備用）

    python 產出總入口.py --階段一            # 第一學習階段（新班級）第一學期 → stage1-1\index.html
    python 產出總入口.py --階段一 --學期二   # 第一學習階段（新班級）第二學期 → stage1-2\index.html
    python 產出總入口.py --階段二            # 第二學習階段 第一學期 → stage2-1\index.html（2026-10-07 起）
    python 產出總入口.py --階段二 --學期二   # 第二學習階段 第二學期 → stage2-2\index.html（有站再建子頁）

🆕 2026-10-09 第二學習階段第一學期整合語文、社會與自然三領域；目前各 5 個單元，共 15 個單元。
   代號前綴 `two`（`twosociety01`），與封面、說明書三處一致。不用 `s2`：封面正則 `[a-z]+\d{2}` 不吃中間數字。
   🛑 第二學習階段是**陸續上線**，不檢查「每領域 5 單元」；子頁副標的領域數／單元數由本腳本數出來後改寫。

🔴 2026-10-04 起入口有兩個班級（老師裁示「根首頁分兩區」）：
   ・第三學習階段（白鯨班，90 站）：115-1\、115-2\，**不加參數就是它**，行為與以前完全一樣
   ・第一學習階段（新班級，60 站）：stage1-1\、stage1-2\，要加 `--階段一`
   兩個班級的單元資料夾名稱格式一樣（`領域_第N學期_第N單元_單元名`），**不能靠名字分**。
   分班依據＝該單元素材資料夾 `教材規格.py` 開頭有沒有「第一學習階段」
   （與 `站號對照.md` 的「第 91～150 站」兩個獨立來源核對過，60 站完全一致）。
   🛑 預設（白鯨班）模式會**排除**新班級單元——否則同領域同序號會混進同一頁。

🛑 2026-09-03 起改成「學年度總覽 → 學期 → 領域 → 單元」四層結構：
   根目錄 index.html 是純靜態的學期選單（2 個連結，不是本腳本產生的），
   115-1\、115-2\ 底下才是各自的「9 領域 45 單元」頁（本腳本產生資料）。
   兩個子頁沿用同一份 covers\、說明\（放在 ROOT 底下共用，子頁用 ../ 開頭引用）。

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
素材區 = os.path.dirname(完成區)                              # 網站製作區（單元素材資料夾所在）

# 領域顯示順序與樣式（新增領域時補這三張表）
序 = {"自然": 1, "社會": 2, "數學": 3, "語文": 4, "健體": 5,
     "綜合": 6, "藝文": 7, "特需生活管理": 8, "特需功能性動作訓練": 9, "生活": 10}
# 封面檔名用的英文代碼（與 生成封面.py 的 `檔名()` 必須一致）
# 🛑 「生活」不能用 "life"——那個代碼已經給「綜合」用了，撞號會讓 套用封面.py 互相覆蓋。
代碼 = {"自然": "nature", "社會": "society", "數學": "math", "語文": "chinese",
      "健體": "pe", "綜合": "life", "藝文": "arts",
      "特需生活管理": "selfcare", "特需功能性動作訓練": "motor", "生活": "daily"}
圖 = {"自然": "🌱", "社會": "🏮", "數學": "📐", "語文": "📖", "健體": "🏃",
     "綜合": "🌏", "藝文": "🎨", "特需生活管理": "🏠", "特需功能性動作訓練": "🤸",
     "生活": "🎒"}
色 = {"自然": "#3f9142", "社會": "#c0562e", "數學": "#3a6ea8", "語文": "#8a5a2b",
     "健體": "#c2410c", "綜合": "#2f8f8f", "藝文": "#9333a8",
     "特需生活管理": "#b8860b", "特需功能性動作訓練": "#4f5bd5", "生活": "#d6538c"}
# 新班級（第一學習階段）只有六個領域；顯示順序照課程計畫常見排法（生活排在數學之後）
序一 = {"語文": 1, "數學": 2, "生活": 3, "健體": 4, "特需生活管理": 5, "特需功能性動作訓練": 6}


def 學習階段(單元資料夾名):
    """回傳 "一"／"二"／"三"：這個單元屬於哪個學習階段的班級。
    ・"一"＝新班級（第一學習階段）：素材資料夾 教材規格.py 開頭有「第一學習階段」
      （與 站號對照.md 的第 91～150 站兩個獨立來源核對過，60 站完全一致）
    ・"二"＝第二學習階段：`課程依據` 那一行寫「第二學習階段」（2026-10-07 起有 stage2-1 子頁）
    ・"三"＝白鯨班（第三學習階段）：其餘全部。舊世代單元多半沒有任何標記，**預設就是它**。
    🛑 找不到 教材規格.py 一律當 "三"（舊世代單元沒有這支檔）。"""
    p = os.path.join(素材區, 單元資料夾名, "教材規格.py")
    if not os.path.exists(p):
        return "三"
    with open(p, encoding="utf-8", errors="replace") as f:
        頭 = f.read(6000)
    # 🔴 2026-10-09：新版範本的 教材規格.py 有一行註解列出「第一學習階段」「第二學習階段」「第三學習階段」三個選項，
    #    只找字串會把每個新範本單元都判成「一」（〈怎麼不見了〉〈奇妙的磁鐵〉實際中招）。
    #    → 先讀明確的 `學習階段 = "…"` 欄位，沒有這個欄位（舊世代單元）才沿用下面的舊判準。
    m0 = re.search(r"^學習階段\s*=\s*[\"']([^\"']*)[\"']", 頭, re.M)
    if m0:
        return {"第一學習階段": "一", "第二學習階段": "二"}.get(m0.group(1).strip(), "三")
    if "第一學習階段" in 頭:
        return "一"
    m = re.search(r'^課程依據\s*=\s*"([^"]*)"', 頭, re.M)
    if m and "第二學習階段" in m.group(1):
        return "二"
    return "三"


# 階段 → 代號前綴（與 生成封面.py 的 檔名()、產出使用說明書.py 一致）
階段前綴 = {"一": "new", "二": "two", "三": ""}


def 掃單元(樣式, 新班=False, 階段要="三"):
    if 新班:
        階段要 = "一"
    out = []
    for d in sorted(glob.glob(os.path.join(完成區, 樣式))):
        名 = os.path.basename(d)
        m = re.match(r"(.+?)_(第.學期)_第(\d+)單元_(.+)$", 名)
        if not m:
            continue
        領域, 學期, 序號, 單元 = m.group(1), m.group(2), int(m.group(3)), m.group(4)

        # 🛑 班級過濾：預設只收白鯨班（三），--階段一／--階段二 只收該階段（三班資料夾名格式相同）
        if 學習階段(名) != 階段要:
            continue

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
        # 新班級的封面代號加前綴 new（與 生成封面.py 的 檔名() 一致），避免與白鯨班整組撞號
        代號 = ("%s%s%02d%s" % (階段前綴[階段要], 代碼[領域], 序號, 後綴)
              if 領域 in 代碼 else "")

        # 使用說明書：說明\<代號>.html（由 產出使用說明書.py 產生），沒有就不顯示按鈕
        說明 = ""
        if 代號 and os.path.exists(os.path.join(ROOT, "說明", 代號 + ".html")):
            說明 = "說明/%s.html" % 代號
        封面 = ""
        if 代號 and os.path.exists(os.path.join(ROOT, "covers", 代號 + ".webp")):
            封面 = "covers/%s.webp" % 代號

        out.append(dict(領域=領域, 學期=學期, 序=序號, 單元=單元,
                        網址=mm.group(0), 週=週, 頁=頁, 題=題, 卡=卡, 封面=封面,
                        說明=說明))
    return out


def main():
    新班 = "--階段一" in sys.argv
    二階 = "--階段二" in sys.argv
    assert not (新班 and 二階), "🛑 --階段一 與 --階段二 只能擇一"
    if 二階:
        assert "--全部" not in sys.argv, "🛑 --階段二 不支援 --全部"
        學 = "2" if "--學期二" in sys.argv else "1"
        樣式 = "*第二學期*" if 學 == "2" else "*第一學期*"
        目標, 前綴 = os.path.join(ROOT, "stage2-" + 學, "index.html"), "../"
    elif 新班:
        assert "--全部" not in sys.argv, "🛑 --階段一 不支援 --全部（新班級沒有合併頁）"
        if "--學期二" in sys.argv:
            樣式, 目標, 前綴 = "*第二學期*", os.path.join(ROOT, "stage1-2", "index.html"), "../"
        else:
            樣式, 目標, 前綴 = "*第一學期*", os.path.join(ROOT, "stage1-1", "index.html"), "../"
    elif "--全部" in sys.argv:
        樣式, 目標, 前綴 = "*", os.path.join(ROOT, "index.html"), ""
    elif "--學期二" in sys.argv:
        樣式, 目標, 前綴 = "*第二學期*", os.path.join(ROOT, "115-2", "index.html"), "../"
    else:
        樣式, 目標, 前綴 = "*第一學期*", os.path.join(ROOT, "115-1", "index.html"), "../"

    單元們 = 掃單元(樣式, 新班, "二" if 二階 else "三")
    assert 單元們, "🛑 一個單元都沒掃到，八成是路徑錯了（不要讓空清單變成成功）"

    領域序 = 序一 if 新班 else 序
    未知 = {x["領域"] for x in 單元們} - set(領域序)
    assert not 未知, "🛑 這些領域還沒登記顯示順序／圖示／顏色：%s" % 未知
    # 🛑 每個領域在每個學期頁都應該剛好 5 個單元；缺了代表有站沒上線或沒被掃到
    各領域數 = {}
    for x in 單元們:
        各領域數[x["領域"]] = 各領域數.get(x["領域"], 0) + 1
    if 新班:
        assert set(各領域數) == set(序一), "🛑 新班級應有六個領域，實際：%s" % sorted(各領域數)
        assert all(n == 5 for n in 各領域數.values()), "🛑 每個領域每學期應有 5 單元：%s" % 各領域數

    # 🛑 兩個學期一起掃時要**先分學期再排序號**（2026-08-16）：
    #    只用序號排會變成 1、1、2、2、3、3… 一上二下交錯，
    #    而單元卡上只有封面與單元名（老師指定），看的人分不出哪張是哪個學期。
    #    這裡只動順序、不加任何標籤，維持「只有封面圖＋單元名」。
    群 = {}
    for x in sorted(單元們, key=lambda a: (領域序[a["領域"]], a["學期"], a["序"])):
        群.setdefault(x["領域"], []).append(x)
    資料 = [{"名": k, "圖": 圖[k], "色": 色[k],
            "單元": [{"序": u["序"], "名": u["單元"], "網址": u["網址"],
                    "封面": (前綴 + u["封面"]) if u["封面"] else "",
                    "說明": (前綴 + u["說明"]) if u["說明"] else ""}
                   for u in v]}
          for k, v in sorted(群.items(), key=lambda a: 領域序[a[0]])]

    # 🛑 素材健檢仍要做（雖然數字不再顯示在頁面上）：0 代表素材沒建置或路徑錯
    壞 = [x["單元"] for x in 單元們 if not (x["頁"] and x["題"] and x["卡"])]
    assert not 壞, "🛑 這些單元的頁數／題數／圖卡數是 0，先查素材：%s" % 壞

    p = 目標
    assert os.path.exists(p), "🛑 目標檔案不存在，先建立子頁模板：%s" % p
    html = open(p, encoding="utf-8").read()
    新 = "const 資料 = %s;" % json.dumps(資料, ensure_ascii=False, indent=1)
    html2, n = re.subn(r"const 資料 = .*?;\n", 新 + "\n", html, count=1, flags=re.S)
    assert n == 1, "🛑 index.html 裡找不到 `const 資料 = …;` 這一行"
    if 二階:
        # 第二學習階段陸續上線：副標的數字一律用數出來的，不手寫
        學期名 = "第二學期" if "--學期二" in sys.argv else "第一學期"
        副 = "<p>第二學習階段　%s　%d 個領域　%d 個單元</p>" % (
            學期名, len(資料), sum(len(d["單元"]) for d in 資料))
        html2, n = re.subn(r"<p>第二學習階段　.*?</p>", 副, html2, count=1)
        assert n == 1, "🛑 stage2 子頁找不到「<p>第二學習階段　…</p>」副標"
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
