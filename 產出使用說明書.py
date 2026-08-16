# -*- coding: utf-8 -*-
r"""替第一學期 45 個單元各產生一份「使用說明書」網頁，放進 `說明\<代號>.html`。

    python 產出使用說明書.py            # 產出全部
    python 產出使用說明書.py --list     # 乾跑，只印每一份會寫進去什麼
    python 產出使用說明書.py 自然       # 只重出某個領域

資料來源三邊，各司其職（**不要在本檔手打任何課程內容**）：
  ① `..\..\課程目標_第一學期.json`　← `抽課程目標.py` 從教學進度表 docx 抽的
     （學年目標／學期目標／學習表現／學習內容／週次／單元內容）
  ② 各站 `教學網站\js\data.js`　　　← 教學重點標題
  ③ 各站 `教學網站\assets\`　　　　　← 頁數、圖卡數（**數實體檔案**，不解析字串）

🛑 **學生姓名絕對不可以出現**（專案硬性規範第 1 條）。
   課程計畫的學期目標是按 A／B／C 三組寫的，而**組別標籤後面直接跟著學生姓名**。
   上游 `抽課程目標.py` 已經在 `_去識別()` 切掉，本檔輸出前**再擋一次**
   （`_驗無姓名()`，比對 docx 裡實際出現過的姓名）——
   這是會上公開網站的東西，兩道關卡都要在。

📌 學期目標的呈現方式＝**三組合併成一段敘述**（老師 2026-08-16 裁示）。
   🛑 **不做「A組第 n 條 ↔ B組第 n 條」的逐條配對**：實測 A／B／C 三組的條目
   　 數量與順序都對不齊（例：熱對物質的影響 A 有 3 條、C 只有 2 條，
   　 而且 A 的第 1 條講熱傳播方式、B／C 的第 1 條講觸覺感知），
   　 硬配會製造出**看起來很整齊但內容錯置**的對應。
   　 改成「同一層次的目標併成一個子句」，忠實但不宣稱逐條對應。
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
完成區 = os.path.dirname(ROOT)
BASE = os.path.dirname(完成區)
OUT = os.path.join(ROOT, "說明")
目標檔 = os.path.join(BASE, "課程目標_第一學期.json")
進度表 = os.path.join(BASE, "教學進度表")

代碼 = {"自然": "nature", "社會": "society", "數學": "math", "語文": "chinese",
      "健體": "pe", "綜合": "life", "藝文": "arts",
      "特需生活管理": "selfcare", "特需功能性動作訓練": "motor"}
圖 = {"自然": "🌱", "社會": "🏮", "數學": "📐", "語文": "📖", "健體": "🏃",
     "綜合": "🌏", "藝文": "🎨", "特需生活管理": "🏠", "特需功能性動作訓練": "🤸"}
色 = {"自然": "#3f9142", "社會": "#c0562e", "數學": "#3a6ea8", "語文": "#8a5a2b",
     "健體": "#c2410c", "綜合": "#2f8f8f", "藝文": "#9333a8",
     "特需生活管理": "#b8860b", "特需功能性動作訓練": "#4f5bd5"}

# 三個程度層次的引導語（對應課程計畫的 A／B／C 組，**不寫組別代號也不寫姓名**）
# 🛑 引導語**不可以用「能」收尾**：課程計畫的目標原文本來就是「能說明…」開頭，
#    寫成「要能」會接出「要能能說明…」（2026-08-16 第一版 45 份全中，開檔才看到）。
層次語 = [
    ("A組", "能力較佳、可獨立完成的學生，"),
    ("B組", "需要提示或圖示輔助的學生，"),
    ("C組", "需要較多協助的學生，"),
]


def _姓名池():
    """把 docx 組別標籤裡出現過的姓名收集起來，只作為輸出前的黑名單比對用。"""
    try:
        import docx
    except ImportError:
        return []
    名 = set()
    for p in glob.glob(os.path.join(進度表, "*.docx")):
        for tb in docx.Document(p).tables:
            for r in tb.rows:
                for c in r.cells:
                    for m in re.finditer(r"[（(]\s*[ABC]\s*組\s*[）)]([^\n\r]*)", c.text):
                        for n in m.group(1).split():
                            if 2 <= len(n) <= 4 and re.fullmatch(r"[一-鿿]+", n):
                                名.add(n)
    return sorted(名)


def _驗無姓名(文字, 誰, 池):
    中 = [n for n in 池 if n in 文字]
    assert not 中, "🛑 %s 的成品裡出現學生姓名，已中止（絕對不可以上公開網站）" % 誰


def _淨(條):
    """去掉編號前綴與『（教學期程…）』，只留目標本文。"""
    s = re.sub(r"^\s*\d+\s*-\s*\d+\s*", "", 條)
    s = re.sub(r"[（(]\s*教學期程.*?[）)]", "", s)
    return s.strip().rstrip("。").strip()


def 學習目標敘述(x):
    """三組合併成一段敘述（不逐條配對，理由見檔頭）。

    🔴 **兩組內容完全相同時要合併成一句**（2026-08-16）：
       課程計畫裡有 5 個單元的兩組目標是一字不差的
       （健體 2、藝文 1／4／5、語文 5——差異化沒有真的差異化）。
       照原樣分段印會出現**兩段一模一樣的文字**，讀的人會以為程式壞了。
       🛑 但**不可以只印一組就算了**——那等於擅自把課程計畫的分組資訊吃掉。
       　 正確做法是把層次語併起來講（「能力較佳與需要提示的學生，能…」），
       　 內容忠實、也看得出這兩個層次的要求相同。
    """
    # 先收成 [(層次語, 條目串)]，再把相鄰且內容相同的合併
    收 = []
    for 組, 引 in 層次語:
        條 = [_淨(c) for c in x["學期目標"].get(組, []) if _淨(c)]
        if 條:
            收.append([[引], "；".join(條)])
    合 = []
    for 引, 文 in 收:
        if 合 and 合[-1][1] == 文:
            合[-1][0].extend(引)
        else:
            合.append([list(引), 文])

    段 = []
    for 引們, 文 in 合:
        if len(引們) == 1:
            頭 = 引們[0]
        else:
            # 「能力較佳、可獨立完成的學生，」＋「需要提示或圖示輔助的學生，」
            #  → 「能力較佳、可獨立完成的學生與需要提示或圖示輔助的學生，」
            頭 = "與".join(s.rstrip("，") for s in 引們) + "，"
        段.append("%s%s。" % (頭, 文))
    return 段


def 讀重點(站):
    """從 data.js 取**教學重點**標題。

    🛑 不可以直接掃所有 `標題:`——`短片`、子頁等等也有 `標題`，
       〈熱對物質的影響〉那樣會抓出 6 條，其中 3 條根本是子頁標題
       （2026-08-16 開檔逐份看才發現，程式本身不會報錯）。
    🔑 錨點是 `編號`：**只有頂層的重點物件帶 `編號:`**，短片物件沒有。
    """
    p = os.path.join(站, "js", "data.js")
    if not os.path.exists(p):
        return []
    s = open(p, encoding="utf-8", errors="replace").read()
    out = []
    for m in re.finditer(r'"?編號"?\s*:\s*\d+\s*,\s*"?標題"?\s*:\s*"([^"]+)"', s):
        t = m.group(1).strip()
        if t and t not in out:
            out.append(t)
    return out


def 素材(站):
    頁 = len(glob.glob(os.path.join(站, "assets", "pages", "*.webp")))
    卡 = len(glob.glob(os.path.join(站, "assets", "cards", "*_front.webp")))
    題 = 0
    p = os.path.join(站, "js", "data.js")
    if os.path.exists(p):
        題 = len(re.findall(r'"?題頁"?\s*:',
                          open(p, encoding="utf-8", errors="replace").read()))
    影 = len(glob.glob(os.path.join(站, "assets", "video", "*.mp4")))
    return 頁, 題, 卡, 影


def 網址(資料夾):
    p = os.path.join(完成區, 資料夾, "線上網址.txt")
    if not os.path.exists(p):
        return ""
    m = re.search(r"https://[a-z0-9.-]+/[a-z0-9-]+/",
                  open(p, encoding="utf-8", errors="replace").read())
    return m.group(0) if m else ""


def 找資料夾(x):
    頭 = "%s_第一學期_第%d單元_" % (x["領域"], x["序"])
    for d in sorted(os.listdir(完成區)):
        if d.startswith(頭) and os.path.isdir(os.path.join(完成區, d)):
            return d
    return None


def 頁面(x, 資料夾, 池):
    站 = os.path.join(完成區, 資料夾, "教學網站")
    重點 = 讀重點(站)
    頁, 題, 卡, 影 = 素材(站)
    網 = 網址(資料夾)
    e = html.escape
    領 = x["領域"]

    目標段 = 學習目標敘述(x)
    列 = [
        ("領域", 領), ("學期", "115 學年度　第 1 學期"),
        ("單元", "第 %d 單元　%s" % (x["序"], x["單元"])),
        ("教學期程", "%s　%s" % (x["週次"], x["起迄日"])),
    ]

    重點html = "".join("<li>%s</li>" % e(t) for t in 重點) or "<li class='無'>（本單元的 data.js 沒有標示教學重點）</li>"
    內容html = "".join("<li>%s</li>" % e(t) for t in
                     [s for s in re.split(r"[／\n]", x["單元內容"]) if s.strip()])
    目標html = "".join("<p>%s</p>" % e(s) for s in 目標段) or "<p class='無'>（課程計畫未列學期目標）</p>"

    doc = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(x['單元'])}｜使用說明書</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='26' font-size='26'>📖</text></svg>">
<style>
:root{{--底:#faf6ee;--紙:#fffdf8;--框:#e2d8c4;--字:#33291c;--淡字:#6f6152;--主:{色[領]};--主淡:#00000010;}}
*{{box-sizing:border-box;}} html,body{{margin:0;padding:0;}}
body{{background:var(--底);color:var(--字);
 font-family:"Microsoft JhengHei","PingFang TC","Noto Sans TC",sans-serif;
 font-size:19px;line-height:1.75;-webkit-text-size-adjust:100%;}}
.頁首{{background:var(--主);color:#fff;padding:24px 20px;text-align:center;}}
.頁首 .眉{{font-size:17px;opacity:.9;}}
.頁首 h1{{margin:6px 0 0;font-size:34px;letter-spacing:1px;}}
.頁首 .副{{margin-top:6px;font-size:18px;opacity:.92;}}
main{{max-width:940px;margin:0 auto;padding:24px 18px 80px;}}
.列{{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 22px;}}
.鈕{{font-size:18px;text-decoration:none;font-weight:700;border-radius:10px;
 padding:9px 18px;border:2px solid var(--主);color:var(--主);background:var(--紙);}}
.鈕:hover{{background:var(--主);color:#fff;}}
.鈕.實{{background:var(--主);color:#fff;}}
section{{background:var(--紙);border:2px solid var(--框);border-left:9px solid var(--主);
 border-radius:14px;padding:20px 24px;margin:0 0 18px;}}
h2{{margin:0 0 12px;font-size:25px;color:var(--主);}}
h3{{margin:16px 0 6px;font-size:20px;}}
table{{border-collapse:collapse;width:100%;}}
th,td{{border:1px solid var(--框);padding:8px 12px;text-align:left;vertical-align:top;}}
th{{background:#00000008;width:130px;white-space:nowrap;}}
ul{{margin:6px 0;padding-left:1.3em;}} li{{margin:4px 0;}}
p{{margin:8px 0;}} .無{{color:var(--淡字);}}
.數{{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;}}
.數 span{{background:#00000008;border:1px solid var(--框);border-radius:9px;padding:6px 14px;font-weight:700;}}
.註{{font-size:17px;color:var(--淡字);}}
.頁尾{{max-width:940px;margin:0 auto;padding:0 18px 40px;color:var(--淡字);font-size:16px;}}
@media print{{
 .列{{display:none;}} body{{background:#fff;font-size:12pt;}}
 section{{break-inside:avoid;box-shadow:none;}} .頁首{{color:#000;background:#fff;border-bottom:3px solid #000;}}
}}
</style>
</head>
<body>
<header class="頁首">
  <div class="眉">{圖[領]} {e(領)}　115 學年度第 1 學期</div>
  <h1>{e(x['單元'])}</h1>
  <div class="副">教材使用說明書　｜　{e(x['週次'])}</div>
</header>
<main>
  <div class="列">
    <a class="鈕" href="../index.html#{e(領)}">← 回 {e(領)} 單元列表</a>
    {'<a class="鈕 實" href="' + e(網) + '" target="_blank" rel="noopener noreferrer">前往教學網站 →</a>' if 網 else ''}
  </div>

  <section>
    <h2>一、單元基本資料</h2>
    <table><tbody>
      {''.join(f'<tr><th>{e(k)}</th><td>{e(v)}</td></tr>' for k, v in 列)}
    </tbody></table>
    <h3>課程計畫所列單元內容</h3>
    <ul>{內容html}</ul>
  </section>

  <section>
    <h2>二、學年目標</h2>
    <p>{e(x['學年目標'])}</p>
    <p class="註">（本單元屬於這一條學年目標底下；同一條學年目標可能涵蓋多個單元。）</p>
  </section>

  <section>
    <h2>三、學習目標（本學期）</h2>
    <p class="註">課程計畫依學生程度分三個層次撰寫，以下合併敘述：</p>
    {目標html}
  </section>

  <section>
    <h2>四、領綱學習重點（{e(領)}科．本學年共用）</h2>
    <p class="註">🛑 課程計畫的學習表現與學習內容是<b>整個領域一整學年共用</b>的，
      不是分單元寫的——底下會出現其他單元的條目，屬正常，不是排錯。</p>
    <h3>學習表現</h3>
    <p>{e(x['學習表現']) or '<span class="無">（課程計畫未列）</span>'}</p>
    <h3>學習內容</h3>
    <p>{e(x['學習內容']) or '<span class="無">（課程計畫未列）</span>'}</p>
  </section>

  <section>
    <h2>五、這個單元的教材有什麼</h2>
    <h3>教學重點</h3>
    <ul>{重點html}</ul>
    <div class="數">
      <span>教學頁 {頁} 頁</span><span>評量 {題} 題</span>
      <span>學習圖卡 {卡} 張</span><span>影片 {影} 支</span>
    </div>
  </section>

  <section>
    <h2>六、怎麼上這一課</h2>
    <ul>
      <li><b>🙋 點點名</b>：抽籤點名暖身，一輪內每個人只會被抽到一次。</li>
      <li><b>🃏 圖詞輪播</b>：先唸「詞」再唸「說明句」，可分開重複點按練習。</li>
      <li><b>🎬 教學影片</b>：先看主影片建立整體概念；旁邊的短片清單可以只播某一個重點。</li>
      <li><b>📚 教材教學區</b>：每個重點的流程是<b>教學頁 → 主題短片 → 形成性評量</b>，答對才過。</li>
      <li><b>📝 總評量</b>：兩選一，<b>答錯不重答</b>，標出正解後直接進下一題。</li>
      <li><b>🔗 延伸學習</b>：外部影片，需要網路；沒有合適素材的單元會註明。</li>
    </ul>
    <p class="註">建議節奏：點名暖身 → 看主影片 → 依重點逐段教學與形成性評量 → 下課前做總評量。
      紙本的學習單與評量練習單可搭配課後使用。</p>
  </section>

  <section>
    <h2>七、注意事項</h2>
    <ul>
      <li><b>教室版／公開版會自動判斷</b>：用電腦直接開檔案是教室版（可上傳學生照片）；
        用網址開啟是公開版，<b>照片上傳自動關閉</b>。</li>
      <li><b>學生姓名與照片只留在這台電腦</b>，不會上傳、也不會進到網路上。</li>
      <li>教室版不需要網路；只有「延伸學習」的外部影片需要連網。</li>
    </ul>
  </section>
</main>
<footer class="頁尾">本說明書由 <code>產出使用說明書.py</code> 依教學進度表課程計畫自動產生，請勿手動編輯。</footer>
</body>
</html>
"""
    _驗無姓名(doc, "%s 第%d單元 %s" % (領, x["序"], x["單元"]), 池)
    return doc


def main():
    assert os.path.exists(目標檔), "🛑 找不到 %s，先跑 `python 抽課程目標.py --寫入`" % 目標檔
    資料 = json.load(open(目標檔, encoding="utf-8"))
    只 = [a for a in sys.argv[1:] if not a.startswith("--")]
    if 只:
        資料 = [x for x in 資料 if x["領域"] in 只]
        assert 資料, "🛑 找不到領域 %s" % 只

    池 = _姓名池()
    print("姓名黑名單 %d 個（輸出前逐份比對）" % len(池))
    os.makedirs(OUT, exist_ok=True)

    成功, 缺 = 0, []
    for x in 資料:
        d = 找資料夾(x)
        if not d:
            缺.append("%s 第%d單元 %s" % (x["領域"], x["序"], x["單元"]))
            continue
        代號 = "%s%02d" % (代碼[x["領域"]], x["序"])
        doc = 頁面(x, d, 池)
        if "--list" in sys.argv:
            print("── %s → 說明/%s.html（%d 字）" % (x["單元"], 代號, len(doc)))
            continue
        open(os.path.join(OUT, 代號 + ".html"), "w", encoding="utf-8").write(doc)
        成功 += 1

    if "--list" in sys.argv:
        return
    # 🛑 印的是數出來的值
    實 = len(glob.glob(os.path.join(OUT, "*.html")))
    print("✅ 產出 %d 份；說明\\ 實際有 %d 個 html" % (成功, 實))
    assert 缺 == [], "🛑 這些單元找不到 製作完成區 資料夾：%s" % 缺
    assert 實 == 成功, "🛑 寫出的份數與資料夾內檔案數不符（%d vs %d）" % (成功, 實)


if __name__ == "__main__":
    main()
