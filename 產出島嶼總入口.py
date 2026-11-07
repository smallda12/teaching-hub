# -*- coding: utf-8 -*-
r"""產出 3D 領域群島與各領域獨立三階段導覽總入口 (index.html / index_classic.html / island-lifeskill.html)。

用法：
    python 產出島嶼總入口.py

設計原則：
1. 資料唯一來源：直接讀取本目錄下已由 `產出總入口.py` 產出的六個學期頁
   (`stage1-1`, `stage1-2`, `stage2-1`, `stage2-2`, `115-1`, `115-2`)，
   自動彙整全部 240 站（第一階段 60、第二階段 90、第三階段 90），不手抄第二份網址。
2. 雙層 3D 島嶼架構（Three.js 黏土微縮沙盤風格）：
   - 第一層【🌊 領域群島總覽】：中央總廣場 ＋ 10 座領域立體島嶼緊密聚合。
   - 第二層【🏝️ 各領域獨立導覽島】：點選任一領域島進入，島上對應三個學習階段聚落
     （🌱 第一階段啟蒙村、🌿 第二階段實踐鎮、🌳 第三階段進階城），每單元皆有立體建築與浮動膠囊標籤。
   - 第三層【🎁 教材寶箱抽屜卡片】：點選任一單元彈出，含紙雕封面預覽、70頁簡報、5支短片、
     互動評量、10組圖卡、幸運輪盤、教學使用說明書、完整獨立網站直達連結。
3. 雙軌切換與 100% 可逆保證：
   - 保留原版學期入口為 `index_classic.html`（並附切換回 3D 島嶼按鈕）。
   - 3D 島嶼頁面內建「📋 領域清單總覽」與「🗂️ 原版學期入口」一鍵切換。
"""
import io
import json
import os
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
PROTO_DIR = os.path.join(os.path.dirname( os.path.dirname(ROOT)), "島嶼網站原型_生活管理")

# 10 大領域島設定（將二階「藝術」與三階「藝文」整合為同一座「藝術與人文島」，確保跨階段螺旋連貫）
DOMAIN_CONFIG = [
    {
        "id": "selfcare",
        "name": "特需生活管理",
        "islandName": "特需生活管理島",
        "icon": "🏠",
        "color": "#1565c0",
        "trimColor": "#42a5f5",
        "groundColor": "#e3f2fd",
        "themeDesc": "衣食住行、穿脫洗漱、清潔打掃與自我保護",
        "landmarkType": "lighthouse_whale",
        "sourceDomains": ["特需生活管理"],
        "shareStage1Daily": False
    },
    {
        "id": "motor",
        "name": "特需功能性動作訓練",
        "islandName": "特需動作訓練島",
        "icon": "🤸",
        "color": "#4f5bd5",
        "trimColor": "#7986cb",
        "groundColor": "#e8eaf6",
        "themeDesc": "上肢精細操作、下肢平衡移動、姿勢控制與雙手協調",
        "landmarkType": "gym_rainbow",
        "sourceDomains": ["特需功能性動作訓練"],
        "shareStage1Daily": False
    },
    {
        "id": "chinese",
        "name": "語文",
        "islandName": "語文溝通島",
        "icon": "📖",
        "color": "#8a5a2b",
        "trimColor": "#ffb74d",
        "groundColor": "#fff8e1",
        "themeDesc": "生活語彙、聽說讀寫、繪本故事與人際表達",
        "landmarkType": "book_tower",
        "sourceDomains": ["語文"],
        "shareStage1Daily": False
    },
    {
        "id": "math",
        "name": "數學",
        "islandName": "生活數學島",
        "icon": "📐",
        "color": "#2b6cb0",
        "trimColor": "#64b5f6",
        "groundColor": "#e1f5fe",
        "themeDesc": "數與量、時間金錢、幾何圖形與邏輯序列",
        "landmarkType": "clock_pyramid",
        "sourceDomains": ["數學"],
        "shareStage1Daily": False
    },
    {
        "id": "pe",
        "name": "健體",
        "islandName": "健康與體育島",
        "icon": "🏃",
        "color": "#c2410c",
        "trimColor": "#ff8a65",
        "groundColor": "#fbe9e7",
        "themeDesc": "體能運動遊戲、健康飲食、安全防護與身心活力",
        "landmarkType": "stadium_torch",
        "sourceDomains": ["健體"],
        "shareStage1Daily": False
    },
    {
        "id": "nature",
        "name": "自然",
        "islandName": "自然探險島",
        "icon": "🌱",
        "color": "#2e7d32",
        "trimColor": "#81c784",
        "groundColor": "#e8f5e9",
        "themeDesc": "動植物生態、天氣變化、奇妙磁力與科學探索",
        "landmarkType": "windmill_greenhouse",
        "sourceDomains": ["自然"],
        "shareStage1Daily": True
    },
    {
        "id": "society",
        "name": "社會",
        "islandName": "社會生活島",
        "icon": "🏮",
        "color": "#c0562e",
        "trimColor": "#e57373",
        "groundColor": "#ffebee",
        "themeDesc": "家庭學校、社區資源、交通旅遊與多元文化",
        "landmarkType": "gate_town",
        "sourceDomains": ["社會"],
        "shareStage1Daily": True
    },
    {
        "id": "life",
        "name": "綜合",
        "islandName": "綜合活動島",
        "icon": "🌏",
        "color": "#00838f",
        "trimColor": "#4dd0e1",
        "groundColor": "#e0f7fa",
        "themeDesc": "桌遊輪流、人際互動、生活美感與環境保護",
        "landmarkType": "ferris_camp",
        "sourceDomains": ["綜合"],
        "shareStage1Daily": True
    },
    {
        "id": "arts",
        "name": "藝術與人文",
        "islandName": "藝術創想島",
        "icon": "🎨",
        "color": "#8e24aa",
        "trimColor": "#ba68c8",
        "groundColor": "#f3e5f5",
        "themeDesc": "色彩造型、音樂律動、視覺美感與創意手作",
        "landmarkType": "palette_pavilion",
        "sourceDomains": ["藝術", "藝文"],
        "shareStage1Daily": True
    },
    {
        "id": "daily",
        "name": "生活課程",
        "islandName": "生活課程啟蒙島",
        "icon": "🎒",
        "color": "#d81b60",
        "trimColor": "#f06292",
        "groundColor": "#fce4ec",
        "themeDesc": "第一學習階段跨領域統整：校園探索、四季自然與生活體驗",
        "landmarkType": "schoolbag_park",
        "sourceDomains": ["生活"],
        "shareStage1Daily": False
    }
]


def load_all_240_units():
    pages = [
        (1, "一上", "第一學期", "stage1-1/index.html"),
        (1, "一下", "第二學期", "stage1-2/index.html"),
        (2, "二上", "第一學期", "stage2-1/index.html"),
        (2, "二下", "第二學期", "stage2-2/index.html"),
        (3, "三上", "第一學期", "115-1/index.html"),
        (3, "三下", "第二學期", "115-2/index.html"),
    ]
    all_units = []
    uid_counter = 1
    for stage, sem_short, sem_full, rel_path in pages:
        full_path = os.path.join(ROOT, rel_path)
        assert os.path.exists(full_path), f"🛑 找不到學期入口檔：{full_path}"
        html = open(full_path, encoding="utf-8").read()
        m = re.search(r"const 資料 = (\[.*?\]);\n", html, re.S)
        assert m, f"🛑 {rel_path} 內找不到 const 資料"
        data = json.loads(m.group(1))
        for d in data:
            orig_domain = d["名"]
            for u in d["單元"]:
                cover = u.get("封面", "").replace("../", "")
                manual = u.get("說明", "").replace("../", "")
                assert cover and os.path.exists(os.path.join(ROOT, cover)), f"🛑 缺封面：{orig_domain} {u['名']}"
                assert manual and os.path.exists(os.path.join(ROOT, manual)), f"🛑 缺說明書：{orig_domain} {u['名']}"
                all_units.append({
                    "uid": uid_counter,
                    "stage": stage,
                    "sem": sem_short,
                    "semFull": sem_full,
                    "origDomain": orig_domain,
                    "u": u["序"],
                    "name": u["名"],
                    "url": u["網址"],
                    "cover": cover,
                    "manual": manual
                })
                uid_counter += 1
    assert len(all_units) == 240, f"🛑 總站數應為 240，實際為 {len(all_units)}"
    return all_units


def build_domains_payload(all_units):
    daily_stage1_units = [u for u in all_units if u["origDomain"] == "生活" and u["stage"] == 1]
    assert len(daily_stage1_units) == 10, "🛑 第一階段生活課程應為 10 單元"

    domains_data = []
    for cfg in DOMAIN_CONFIG:
        own_units = [u for u in all_units if u["origDomain"] in cfg["sourceDomains"]]
        own_count = len(own_units)

        s1 = [u for u in own_units if u["stage"] == 1]
        s2 = [u for u in own_units if u["stage"] == 2]
        s3 = [u for u in own_units if u["stage"] == 3]

        stage1_note = ""
        if cfg["shareStage1Daily"] and not s1:
            # 國小一二年級為「生活課程」合科，於自然/社會/綜合/藝術島內提供第一階段生活課程銜接
            s1 = [dict(u, isSharedDaily=True) for u in daily_stage1_units]
            stage1_note = "國小第一學習階段合科為「🎒 生活課程」（10 單元）"

        domains_data.append({
            "id": cfg["id"],
            "name": cfg["name"],
            "islandName": cfg["islandName"],
            "icon": cfg["icon"],
            "color": cfg["color"],
            "trimColor": cfg["trimColor"],
            "groundColor": cfg["groundColor"],
            "themeDesc": cfg["themeDesc"],
            "landmarkType": cfg["landmarkType"],
            "ownCount": own_count,
            "stage1Note": stage1_note,
            "stages": {
                "1": s1,
                "2": s2,
                "3": s3
            }
        })
    return domains_data


def update_classic_index():
    bak_path = os.path.join(ROOT, "index.html.bak_20261107_島嶼改版前")
    classic_path = os.path.join(ROOT, "index_classic.html")
    assert os.path.exists(bak_path), "🛑 找不到 index.html.bak_20261107_島嶼改版前 備份檔"
    raw = open(bak_path, encoding="utf-8").read()
    target = "<p>請先選學習階段，再選學期</p>"
    replacement = (
        '<p>請先選學習階段，再選學期（經典學期清單版）</p>\n'
        '  <p style="margin-top:14px;">'
        '<a href="index.html" style="display:inline-flex;align-items:center;gap:8px;'
        'background:#fff;color:#2f6f4f;font-weight:800;font-size:18px;padding:8px 22px;'
        'border-radius:28px;text-decoration:none;box-shadow:0 4px 12px rgba(0,0,0,.18);">'
        '🏝️ 切換至 3D 領域群島導覽版 →</a></p>'
    )
    assert target in raw, "🛑 原版 index.html 找不到副標題段落"
    out = raw.replace(target, replacement, 1)
    open(classic_path, "w", encoding="utf-8").write(out)
    print("✅ 已更新經典學期總入口：index_classic.html")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>高雄特殊教育學校國小部 115 學年度教材｜3D 領域群島與三階段導覽</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='26' font-size='26'>🏝️</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@500;700;900&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<style>
:root {
  --bg-sea: #e6f2f5;
  --text-main: #1e293b;
  --text-muted: #64748b;
  --white: #ffffff;
  --s1-color: #2e7d32;
  --s1-light: #e8f5e9;
  --s2-color: #1565c0;
  --s2-light: #e3f2fd;
  --s3-color: #e65100;
  --s3-light: #fff3e0;
  --shadow-soft: 0 10px 28px rgba(15, 23, 42, 0.12);
  --shadow-card: 0 22px 50px rgba(15, 23, 42, 0.28);
}

* { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }

body {
  font-family: "Noto Sans TC", "Microsoft JhengHei", sans-serif;
  background: var(--bg-sea);
  color: var(--text-main);
  overflow: hidden;
  width: 100vw;
  height: 100vh;
  user-select: none;
}

/* ── 第一列：頂部全域導覽列 ── */
header.topbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 64px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(14px);
  border-bottom: 2px solid rgba(203, 213, 225, 0.8);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 18px;
  z-index: 200;
  gap: 12px;
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.back-world-btn {
  display: none;
  align-items: center;
  gap: 6px;
  background: #0284c7;
  color: #fff;
  border: none;
  padding: 7px 14px;
  border-radius: 20px;
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 3px 10px rgba(2, 132, 199, 0.28);
  transition: all 0.2s;
  white-space: nowrap;
}
.back-world-btn:hover { background: #0369a1; transform: translateY(-1px); }

.brand-logo {
  font-size: 30px;
  line-height: 1;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.12));
}
.brand-titles h1 {
  font-size: 19px;
  font-weight: 900;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.brand-titles p {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
  white-space: nowrap;
}

/* 階段切換膠囊（進入領域島時顯示） */
.stage-switcher {
  display: none;
  align-items: center;
  gap: 5px;
  background: #f1f5f9;
  padding: 4px;
  border-radius: 28px;
  border: 1px solid #cbd5e1;
}
.stage-btn {
  border: none;
  background: transparent;
  padding: 6px 14px;
  border-radius: 20px;
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.stage-btn:hover { color: var(--text-main); background: rgba(255,255,255,0.6); }
.stage-btn.active {
  background: var(--white);
  color: var(--text-main);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.stage-btn.active[data-stage="1"] { color: var(--s1-color); outline: 2px solid var(--s1-color); }
.stage-btn.active[data-stage="2"] { color: var(--s2-color); outline: 2px solid var(--s2-color); }
.stage-btn.active[data-stage="3"] { color: var(--s3-color); outline: 2px solid var(--s3-color); }

/* 右側工具群 */
.top-right-tools {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}
.search-input {
  width: 170px;
  padding: 7px 12px 7px 32px;
  border-radius: 20px;
  border: 2px solid #cbd5e1;
  font-family: inherit;
  font-size: 14px;
  font-weight: 700;
  background: #f8fafc;
  color: var(--text-main);
  transition: all 0.2s;
}
.search-input:focus {
  outline: none;
  border-color: #0284c7;
  background: #fff;
  width: 220px;
}
.search-icon {
  position: absolute;
  left: 10px;
  font-size: 14px;
  pointer-events: none;
}

.search-dropdown {
  position: absolute;
  top: 44px;
  right: 0;
  width: 340px;
  max-height: 420px;
  overflow-y: auto;
  background: #fff;
  border-radius: 16px;
  box-shadow: var(--shadow-card);
  border: 2px solid #cbd5e1;
  display: none;
  z-index: 500;
  padding: 8px;
}
.search-dropdown.open { display: block; }
.search-item {
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  border-bottom: 1px solid #f1f5f9;
}
.search-item:hover { background: #f0f9ff; }
.search-item-title { font-size: 15px; font-weight: 800; color: var(--text-main); }
.search-item-meta { font-size: 12px; font-weight: 700; color: var(--text-muted); }

.icon-pill-btn {
  height: 38px;
  padding: 0 12px;
  border-radius: 20px;
  border: 2px solid #cbd5e1;
  background: var(--white);
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  color: var(--text-main);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  transition: all 0.2s;
  white-space: nowrap;
}
.icon-pill-btn:hover {
  border-color: #0284c7;
  color: #0284c7;
  transform: translateY(-1px);
}
.icon-pill-btn.primary-toggle {
  background: #f0fdf4;
  border-color: #86efac;
  color: #166534;
}
.icon-pill-btn.primary-toggle:hover {
  background: #166534;
  color: #fff;
}
.icon-pill-btn.classic-link {
  background: #fffbeb;
  border-color: #fde68a;
  color: #92400e;
}
.icon-pill-btn.classic-link:hover {
  background: #b45309;
  color: #fff;
}

/* ── 第二列：領域島嶼快速切換列 ── */
nav.domain-bar {
  position: fixed;
  top: 64px; left: 0; right: 0;
  height: 50px;
  background: rgba(248, 250, 252, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 18px;
  overflow-x: auto;
  z-index: 190;
  scrollbar-width: none;
}
nav.domain-bar::-webkit-scrollbar { display: none; }

.domain-chip {
  border: 2px solid transparent;
  background: var(--white);
  color: var(--text-main);
  padding: 5px 13px;
  border-radius: 18px;
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  transition: all 0.18s;
  flex-shrink: 0;
}
.domain-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.domain-chip.active {
  background: #0f172a;
  color: #fff;
  border-color: #38bdf8;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.22);
}
.domain-chip .chip-count {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 10px;
  background: rgba(0,0,0,0.07);
}
.domain-chip.active .chip-count {
  background: rgba(255,255,255,0.22);
  color: #fff;
}

/* ── 3D 沙盤主視口 ── */
#stage-3d {
  position: absolute;
  top: 114px; left: 0; right: 0; bottom: 0;
  overflow: hidden;
  cursor: grab;
}
#stage-3d:active { cursor: grabbing; }

canvas#canvas-3d {
  width: 100%;
  height: 100%;
  display: block;
}

/* 3D 空間投影膠囊標籤層 */
#labels-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 20;
}

.label-pin {
  position: absolute;
  pointer-events: auto;
  transform: translate(-50%, -100%);
  cursor: pointer;
  transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s;
  white-space: nowrap;
}
.label-pin:hover {
  transform: translate(-50%, -114%) scale(1.12);
  z-index: 80 !important;
}

.label-pill {
  background: rgba(255, 255, 255, 0.96);
  padding: 7px 14px;
  border-radius: 26px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.16), 0 2px 5px rgba(15, 23, 42, 0.08);
  border: 2px solid rgba(255, 255, 255, 0.98);
  display: flex;
  align-items: center;
  gap: 7px;
  position: relative;
}
.label-pill::after {
  content: "";
  position: absolute;
  bottom: -7px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 7px 6px 0 6px;
  border-style: solid;
  border-color: rgba(255, 255, 255, 0.96) transparent transparent transparent;
}

.pin-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.stage-1 .pin-dot { background: var(--s1-color); box-shadow: 0 0 0 3px rgba(46,125,50,0.22); }
.stage-2 .pin-dot { background: var(--s2-color); box-shadow: 0 0 0 3px rgba(21,101,192,0.22); }
.stage-3 .pin-dot { background: var(--s3-color); box-shadow: 0 0 0 3px rgba(230,81,0,0.22); }

.pin-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--text-main);
}
.pin-badge {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  background: #f1f5f9;
  padding: 1px 6px;
  border-radius: 8px;
}

/* 中央核心與聚落大標籤 */
.pill-center {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  border: 2px solid #7dd3fc;
  padding: 9px 18px;
  box-shadow: 0 10px 26px rgba(2, 132, 199, 0.35);
}
.pill-center .pin-title { color: #fff; font-size: 16px; }
.pill-center .pin-dot { background: #fde047; box-shadow: 0 0 0 3px rgba(253,224,71,0.35); }
.pill-center::after { border-color: #0369a1 transparent transparent transparent; }

.pill-stage-header {
  padding: 7px 16px;
  color: #fff;
  border-width: 2px;
}
.pill-stage-header .pin-title { color: #fff; font-size: 15px; }
.pill-stage-header .pin-badge { background: rgba(255,255,255,0.24); color: #fff; }
.pill-s1-hdr { background: var(--s1-color); border-color: #a5d6a7; }
.pill-s1-hdr::after { border-color: var(--s1-color) transparent transparent transparent; }
.pill-s2-hdr { background: var(--s2-color); border-color: #90caf9; }
.pill-s2-hdr::after { border-color: var(--s2-color) transparent transparent transparent; }
.pill-s3-hdr { background: var(--s3-color); border-color: #ffcc80; }
.pill-s3-hdr::after { border-color: var(--s3-color) transparent transparent transparent; }

/* 底部單元快速導覽船塢 (Quick Unit Dock - 領域島內顯示全部 30 單元) */
.unit-quick-dock {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: min(94vw, 1180px);
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(14px);
  border: 2px solid #cbd5e1;
  border-radius: 22px;
  padding: 10px 16px;
  box-shadow: var(--shadow-soft);
  z-index: 40;
  display: none;
  flex-direction: column;
  gap: 8px;
}
.unit-quick-dock.visible { display: flex; }

.dock-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 800;
  color: var(--text-muted);
}
.dock-pills-scroll {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.dock-unit-btn {
  border: 2px solid #e2e8f0;
  background: #f8fafc;
  color: var(--text-main);
  padding: 6px 12px;
  border-radius: 14px;
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  flex-shrink: 0;
  transition: all 0.16s;
}
.dock-unit-btn:hover {
  transform: translateY(-2px);
  border-color: #0284c7;
  background: #f0f9ff;
}
.dock-unit-btn.s1 { border-left: 5px solid var(--s1-color); }
.dock-unit-btn.s2 { border-left: 5px solid var(--s2-color); }
.dock-unit-btn.s3 { border-left: 5px solid var(--s3-color); }

/* 右下角 3D 鏡頭控制按鈕 */
.cam-controls {
  position: absolute;
  right: 20px;
  bottom: 115px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 45;
}
.cam-btn {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid #cbd5e1;
  box-shadow: var(--shadow-soft);
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.cam-btn:hover, .cam-btn.active {
  background: #0284c7;
  color: #fff;
  border-color: #0284c7;
  transform: scale(1.08);
}

/* 左上角島嶼資訊橫幅 */
.island-info-banner {
  position: absolute;
  top: 16px;
  left: 20px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  border: 2px solid #cbd5e1;
  border-radius: 18px;
  padding: 12px 18px;
  box-shadow: var(--shadow-soft);
  z-index: 35;
  max-width: 420px;
  pointer-events: auto;
}
.banner-title {
  font-size: 18px;
  font-weight: 900;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 8px;
}
.banner-desc {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-muted);
  margin-top: 4px;
}
.banner-note {
  margin-top: 6px;
  font-size: 12px;
  font-weight: 800;
  color: #b45309;
  background: #fef3c7;
  padding: 3px 10px;
  border-radius: 10px;
  display: none;
}

/* ── 領域 × 三階段清單模式視圖 (List View) ── */
#list-view {
  position: absolute;
  top: 114px; left: 0; right: 0; bottom: 0;
  overflow-y: auto;
  background: #f8fafc;
  padding: 30px 20px 90px;
  display: none;
  z-index: 60;
}
.list-container {
  max-width: 1200px;
  margin: 0 auto;
}
.list-domain-header {
  background: var(--white);
  border-radius: 22px;
  padding: 24px 28px;
  margin-bottom: 24px;
  border: 2px solid #e2e8f0;
  box-shadow: var(--shadow-soft);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}
.list-stage-block {
  background: var(--white);
  border-radius: 20px;
  padding: 24px 28px;
  margin-bottom: 24px;
  border: 2px solid #e2e8f0;
  box-shadow: var(--shadow-soft);
}
.list-stage-title {
  font-size: 22px;
  font-weight: 900;
  padding-bottom: 12px;
  margin-bottom: 18px;
  border-bottom: 2px solid #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.unit-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}
.unit-visual-card {
  background: #fff;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}
.unit-visual-card:hover {
  transform: translateY(-4px);
  border-color: #0284c7;
  box-shadow: 0 12px 24px rgba(2, 132, 199, 0.14);
}
.unit-card-thumb {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
  background: #f1f5f9;
  border-bottom: 1px solid #e2e8f0;
}
.unit-card-body {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.unit-card-sem {
  font-size: 12px;
  font-weight: 800;
  color: var(--text-muted);
}
.unit-card-name {
  font-size: 18px;
  font-weight: 900;
  color: var(--text-main);
}

/* ── 抽屜式教材寶箱視窗 (Option A Modal Drawer) ── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(8px);
  z-index: 2000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.modal-backdrop.open { display: flex; }

.treasure-modal {
  background: var(--white);
  width: 100%;
  max-width: 720px;
  max-height: 92vh;
  overflow-y: auto;
  border-radius: 26px;
  box-shadow: var(--shadow-card);
  border: 3px solid #cbd5e1;
  animation: modalPop 0.26s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes modalPop {
  from { transform: scale(0.92) translateY(20px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}

.modal-top {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 18px;
  border-bottom: 2px solid #f1f5f9;
  background: #f8fafc;
}
.modal-cover-img {
  width: 120px;
  height: 78px;
  object-fit: cover;
  border-radius: 12px;
  border: 2px solid #cbd5e1;
  flex-shrink: 0;
  background: #fff;
}
.modal-title-wrap {
  flex: 1;
  min-width: 0;
}
.modal-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 6px;
}
.m-badge {
  font-size: 12px;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 14px;
}
.m-badge-s1 { background: var(--s1-light); color: var(--s1-color); }
.m-badge-s2 { background: var(--s2-light); color: var(--s2-color); }
.m-badge-s3 { background: var(--s3-light); color: var(--s3-color); }
.m-badge-domain { background: #e2e8f0; color: #334155; }

.modal-unit-title {
  font-size: 26px;
  font-weight: 900;
  color: var(--text-main);
  line-height: 1.25;
}
.modal-close-btn {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2px solid #cbd5e1;
  background: #fff;
  font-size: 20px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
}
.modal-close-btn:hover {
  background: #ef4444;
  color: #fff;
  border-color: #ef4444;
}

.modal-content {
  padding: 22px 24px 26px;
}
.modal-sec-label {
  font-size: 14px;
  font-weight: 800;
  color: var(--text-muted);
  margin-bottom: 12px;
}
.treasure-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 18px;
}
.t-card-btn {
  background: #fff;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: var(--text-main);
  transition: all 0.18s;
}
.t-card-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(0,0,0,0.08);
  border-color: #0284c7;
}
.t-card-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}
.t-card-title { font-size: 17px; font-weight: 900; display: block; }
.t-card-desc { font-size: 12px; font-weight: 700; color: var(--text-muted); margin-top: 2px; display: block; }

.modal-bottom-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}
.nav-adj-btn {
  padding: 14px 16px;
  border-radius: 16px;
  border: 2px solid #cbd5e1;
  background: #f8fafc;
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  color: var(--text-main);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.18s;
}
.nav-adj-btn:hover { background: #e2e8f0; }

.launch-full-btn {
  flex: 1;
  background: linear-gradient(135deg, #0284c7 0%, #1e40af 100%);
  color: #fff;
  text-decoration: none;
  padding: 15px 22px;
  border-radius: 16px;
  font-size: 17px;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 8px 20px rgba(2, 132, 199, 0.3);
  transition: all 0.2s;
}
.launch-full-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 26px rgba(2, 132, 199, 0.42);
}

@media (max-width: 820px) {
  .brand-titles p, .island-info-banner { display: none; }
  .treasure-grid { grid-template-columns: 1fr; }
  .search-input { width: 120px; }
  .search-input:focus { width: 160px; }
}
</style>
</head>
<body>

<!-- 第一列：頂部全域導覽列 -->
<header class="topbar">
  <div class="brand-group">
    <button class="back-world-btn" id="btn-back-world" onclick="enterWorldView()">
      <span>🌊</span>
      <span>返回領域群島</span>
    </button>
    <div class="brand-logo" id="top-logo">🏝️</div>
    <div class="brand-titles">
      <h1 id="top-title">高雄特教國小部｜3D 領域群島總入口</h1>
      <p id="top-subtitle">10 大領域島嶼 × 三個學習階段 × 240 個互動單元</p>
    </div>
  </div>

  <!-- 階段聚焦切換（領域島內顯示） -->
  <div class="stage-switcher" id="stage-switcher">
    <button class="stage-btn active" data-stage="all" onclick="selectStage('all')">🌐 全島總覽</button>
    <button class="stage-btn" data-stage="1" onclick="selectStage('1')">🌱 第一階段 (10)</button>
    <button class="stage-btn" data-stage="2" onclick="selectStage('2')">🌿 第二階段 (10)</button>
    <button class="stage-btn" data-stage="3" onclick="selectStage('3')">🌳 第三階段 (10)</button>
  </div>

  <!-- 右側功能列 -->
  <div class="top-right-tools">
    <div class="search-box">
      <span class="search-icon">🔍</span>
      <input type="search" class="search-input" id="unit-search" placeholder="搜尋 240 單元..." autocomplete="off">
      <div class="search-dropdown" id="search-results"></div>
    </div>

    <button class="icon-pill-btn" id="btn-tod" onclick="cycleTimeOfDay()" title="切換白天／夕陽／星夜">☀️ 時段</button>
    <button class="icon-pill-btn primary-toggle" id="btn-view-mode" onclick="toggleDisplayMode()">
      <span id="view-mode-icon">📋</span>
      <span id="view-mode-text">領域清單模式</span>
    </button>
    <a class="icon-pill-btn classic-link" href="index_classic.html" title="切換回原本依學習階段與學期分類的總入口">
      <span>🗂️</span>
      <span>原版學期入口</span>
    </a>
  </div>
</header>

<!-- 第二列：10 大領域島嶼快速導覽列 -->
<nav class="domain-bar" id="domain-bar"></nav>

<!-- 3D 沙盤主視口 -->
<main id="stage-3d">
  <canvas id="canvas-3d"></canvas>
  <div id="labels-layer"></div>

  <!-- 左上角當前島嶼資訊卡 -->
  <div class="island-info-banner" id="island-banner">
    <div class="banner-title" id="banner-title">🌊 特教學習大世界（10 大領域群島）</div>
    <div class="banner-desc" id="banner-desc">點擊任一領域島嶼，即可進入該領域的「第一、二、三學習階段」立體教材村落！</div>
    <div class="banner-note" id="banner-note"></div>
  </div>

  <!-- 右下角鏡頭控制 -->
  <div class="cam-controls">
    <button class="cam-btn" id="btn-all-pins" onclick="toggleShowAllPins()" title="切換顯示全部單元標籤／精選標籤" style="display:none;">🏷️</button>
    <button class="cam-btn" onclick="resetCamera()" title="重置視角">⟲</button>
    <button class="cam-btn" id="btn-tour" onclick="toggleTour()" title="自動環島巡航運鏡">🎬</button>
  </div>

  <!-- 底部單元快速導覽船塢（進入領域島時顯示該島 30 單元） -->
  <div class="unit-quick-dock" id="unit-dock">
    <div class="dock-header">
      <span id="dock-title">📍 本島單元快速點選（點擊直接開啟教材寶箱）：</span>
      <span id="dock-count">共 30 單元</span>
    </div>
    <div class="dock-pills-scroll" id="dock-list"></div>
  </div>
</main>

<!-- 領域 × 三階段清單模式視口 -->
<section id="list-view">
  <div class="list-container" id="list-container"></div>
</section>

<!-- 抽屜式教材寶箱視窗 (Option A) -->
<div class="modal-backdrop" id="treasure-modal" onclick="if(event.target===this)closeModal()">
  <div class="treasure-modal">
    <div class="modal-top">
      <img class="modal-cover-img" id="m-cover" src="" alt="單元封面">
      <div class="modal-title-wrap">
        <div class="modal-badges">
          <span class="m-badge m-badge-domain" id="m-domain-badge">特需生活管理</span>
          <span class="m-badge m-badge-s2" id="m-stage-badge">🌿 第二階段・二上 第 2 單元</span>
        </div>
        <h2 class="modal-unit-title" id="m-title">會穿脫鞋襪</h2>
      </div>
      <button class="modal-close-btn" onclick="closeModal()" aria-label="關閉">✕</button>
    </div>

    <div class="modal-content">
      <div class="modal-sec-label">🎁 點選下方教材模組（開新分頁進入）：</div>
      <div class="treasure-grid">
        <a class="t-card-btn" id="m-link-ppt" href="#" target="_blank">
          <div class="t-card-icon" style="background:#fee2e2;">📊</div>
          <div>
            <span class="t-card-title">70 頁教學簡報</span>
            <span class="t-card-desc">支援 ⛶ 全螢幕放映・四重點教學</span>
          </div>
        </a>

        <a class="t-card-btn" id="m-link-video" href="#" target="_blank">
          <div class="t-card-icon" style="background:#dcfce7;">🎬</div>
          <div>
            <span class="t-card-title">主題教學影片</span>
            <span class="t-card-desc">主影片 ＋ 4 支重點短片播放清單</span>
          </div>
        </a>

        <a class="t-card-btn" id="m-link-quiz" href="#" target="_blank">
          <div class="t-card-icon" style="background:#ffedd5;">🎯</div>
          <div>
            <span class="t-card-title">互動評量挑戰</span>
            <span class="t-card-desc">16 題兩選一語音測驗・自動計分</span>
          </div>
        </a>

        <a class="t-card-btn" id="m-link-cards" href="#" target="_blank">
          <div class="t-card-icon" style="background:#dbeafe;">🗂️</div>
          <div>
            <span class="t-card-title">認知學習圖卡</span>
            <span class="t-card-desc">10 組核心語詞圖卡・雙面 PDF 下載</span>
          </div>
        </a>

        <a class="t-card-btn" id="m-link-wheel" href="#" target="_blank">
          <div class="t-card-icon" style="background:#f3e8ff;">🎡</div>
          <div>
            <span class="t-card-title">幸運課堂大輪盤</span>
            <span class="t-card-desc">轉動音效・對應語音・抽過刪除模式</span>
          </div>
        </a>

        <a class="t-card-btn" id="m-link-manual" href="#" target="_blank">
          <div class="t-card-icon" style="background:#fef3c7;">📖</div>
          <div>
            <span class="t-card-title">教學使用說明書</span>
            <span class="t-card-desc">單元教學目標、期程與操作指引</span>
          </div>
        </a>
      </div>

      <div class="modal-bottom-bar">
        <button class="nav-adj-btn" id="m-prev-btn" onclick="stepModalUnit(-1)">◀ 上一單元</button>
        <a class="launch-full-btn" id="m-link-site" href="#" target="_blank">
          <span>🚀 進入此單元完整互動教學網站</span>
          <span>立即前往 →</span>
        </a>
        <button class="nav-adj-btn" id="m-next-btn" onclick="stepModalUnit(1)">下一單元 ▶</button>
      </div>
    </div>
  </div>
</div>

<script>
// 權威 240 站 × 10 大領域島 × 三學習階段完整資料（由 產出島嶼總入口.py 自動注入）
const DOMAINS_DATA = __DOMAINS_DATA__;
const DEFAULT_DOMAIN_ID = "__DEFAULT_DOMAIN_ID__";

const DOMAIN_MAP = {};
const UNIT_MAP = {};
const ALL_UNITS_FLAT = [];

DOMAINS_DATA.forEach(d => {
  DOMAIN_MAP[d.id] = d;
  ["1", "2", "3"].forEach(st => {
    (d.stages[st] || []).forEach(u => {
      if (!UNIT_MAP[u.uid]) {
        UNIT_MAP[u.uid] = u;
        ALL_UNITS_FLAT.push(u);
      }
    });
  });
});

// 狀態管理
let currentMode = "world"; // "world" or domainId
let currentStageFilter = "all"; // "all", "1", "2", "3"
let displayView = "3d"; // "3d" or "list"
let showAll30Pins = false;
let activeModalUnitList = [];
let activeModalIndex = 0;

// ==========================================
// Three.js 3D 黏土微縮沙盤引擎
// ==========================================
let scene, camera, renderer, worldGroup, labelsLayer;
let isDragging = false, dragMoved = false, prevPointer = { x: 0, y: 0 };
let spherical = { radius: 42, theta: 0.68, phi: 1.02 };
let targetLook = new THREE.Vector3(0, 0, 0);
let currentLook = new THREE.Vector3(0, 0, 0);
let autoTour = false;
let todState = 0; // 0: day, 1: sunset, 2: night
let hemiLight, sunLight, backLight, seaMesh;
const pinItems = [];
const spinningMeshes = [];

const matPool = {};
function mat(hex, emissive = 0x000000) {
  const key = hex + "_" + emissive;
  if (!matPool[key]) {
    matPool[key] = new THREE.MeshLambertMaterial({
      color: new THREE.Color(hex),
      emissive: new THREE.Color(emissive),
      flatShading: true
    });
  }
  return matPool[key];
}

function box(w, h, d, color, x = 0, y = 0, z = 0, em = 0x000000) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(color, em));
  m.position.set(x, y + h / 2, z);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
function cyl(rt, rb, h, color, x = 0, y = 0, z = 0, seg = 8, em = 0x000000) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), mat(color, em));
  m.position.set(x, y + h / 2, z);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
function cone(r, h, color, x = 0, y = 0, z = 0, seg = 6) {
  const m = new THREE.Mesh(new THREE.ConeGeometry(r, h, seg), mat(color));
  m.position.set(x, y + h / 2, z);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
function ball(r, color, x = 0, y = 0, z = 0, seg = 8) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(r, seg, seg), mat(color));
  m.position.set(x, y, z);
  m.castShadow = true;
  return m;
}

// 帶彩色邊框與厚實土層的立體六角地塊（對齊參考圖的精緻鑲邊六角島）
function createHexPlatform(radius, height, topHex, trimHex, dirtHex, x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);

  // 底層岩石與泥土斷面
  const cliff = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.98, radius * 0.82, height, 6), mat(dirtHex));
  cliff.position.y = height / 2 - 0.25;
  cliff.castShadow = true; cliff.receiveShadow = true;
  g.add(cliff);

  // 彩色外框鑲邊 (Trim Rim)
  const rim = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.03, radius * 1.01, 0.34, 6), mat(trimHex));
  rim.position.y = height - 0.32;
  rim.castShadow = true; rim.receiveShadow = true;
  g.add(rim);

  // 頂層草皮／鋪面
  const top = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.96, radius * 0.96, 0.26, 6), mat(topHex));
  top.position.y = height - 0.18;
  top.receiveShadow = true;
  g.add(top);

  return { group: g, topY: height - 0.05 };
}

function createTree(x, y, z, scale = 1, type = 0) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  g.add(cyl(0.1 * scale, 0.14 * scale, 0.55 * scale, "#795548", 0, 0, 0, 5));
  if (type % 2 === 0) {
    // 針葉松樹
    g.add(cone(0.65 * scale, 0.95 * scale, "#2e7d32", 0, 0.38 * scale, 0, 6));
    g.add(cone(0.5 * scale, 0.8 * scale, "#43a047", 0, 0.85 * scale, 0, 6));
    g.add(cone(0.34 * scale, 0.6 * scale, "#66bb6a", 0, 1.3 * scale, 0, 6));
  } else {
    // 圓球繪本樹
    g.add(ball(0.56 * scale, "#66bb6a", 0, 0.82 * scale, 0, 7));
    g.add(ball(0.38 * scale, "#81c784", 0.24 * scale, 1.05 * scale, 0.12 * scale, 6));
  }
  return g;
}

function createMascot(x, y, z, bodyColor, hatColor) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  g.add(cyl(0.28, 0.32, 0.52, bodyColor, 0, 0, 0, 7));
  g.add(ball(0.32, "#ffe0b2", 0, 0.72, 0, 8));
  g.add(cone(0.26, 0.32, hatColor, 0, 0.96, 0, 6));
  // 耳朵或小手
  g.add(ball(0.1, bodyColor, -0.32, 0.35, 0, 5));
  g.add(ball(0.1, bodyColor, 0.32, 0.35, 0, 5));
  return g;
}

function createStreetLamp(x, y, z) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  g.add(cyl(0.05, 0.07, 1.35, "#546e7a", 0, 0, 0, 6));
  const bulb = ball(0.18, "#fff59d", 0, 1.42, 0, 6);
  bulb.material = mat("#fff59d", 0xfbc02d);
  g.add(bulb);
  return g;
}

function createBench(x, y, z, rotY = 0) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  g.rotation.y = rotY;
  g.add(box(0.85, 0.18, 0.32, "#8d6e63", 0, 0.08, 0));
  g.add(box(0.85, 0.25, 0.08, "#6d4c41", 0, 0.22, -0.12));
  return g;
}

// 建立跨海連接道路／景觀大橋（含路面、兩側護欄、橋墩與路燈）
function createRoadBridge(x1, z1, r1, x2, z2, r2, yHeight = 1.95) {
  const dx = x2 - x1;
  const dz = z2 - z1;
  const fullDist = Math.hypot(dx, dz);
  const ux = dx / fullDist;
  const uz = dz / fullDist;

  // 從兩島邊緣內縮一點點開始架橋，確保視覺無縫銜接
  const startX = x1 + ux * (r1 * 0.86);
  const startZ = z1 + uz * (r1 * 0.86);
  const endX = x2 - ux * (r2 * 0.86);
  const endZ = z2 - uz * (r2 * 0.86);

  const midX = (startX + endX) * 0.5;
  const midZ = (startZ + endZ) * 0.5;
  const len = Math.max(1.2, Math.hypot(endX - startX, endZ - startZ));
  const angle = Math.atan2(dz, dx);

  const g = new THREE.Group();
  g.position.set(midX, 0, midZ);
  g.rotation.y = -angle;

  // 主路面與兩側木質護欄邊條
  g.add(box(len, 0.22, 1.35, "#f5ebe0", 0, yHeight - 0.18, 0));
  g.add(box(len, 0.34, 0.14, "#8d6e63", 0, yHeight - 0.12, -0.68));
  g.add(box(len, 0.34, 0.14, "#8d6e63", 0, yHeight - 0.12, 0.68));

  // 路面中線石磚點綴與護欄木樁、橋墩
  const stepCount = Math.max(2, Math.floor(len / 2.6));
  for (let i = 1; i < stepCount; i++) {
    const px = -len / 2 + (len / stepCount) * i;
    // 兩側木樁
    g.add(box(0.18, 0.55, 0.18, "#6d4c41", px, yHeight - 0.05, -0.68));
    g.add(box(0.18, 0.55, 0.18, "#6d4c41", px, yHeight - 0.05, 0.68));
    // 水中橋墩
    if (i % 2 === 1) {
      g.add(cyl(0.22, 0.28, yHeight, "#a1887f", px, 0, -0.45, 6));
      g.add(cyl(0.22, 0.28, yHeight, "#a1887f", px, 0, 0.45, 6));
    }
  }

  // 橋中央路燈
  if (len > 4.5) {
    g.add(createStreetLamp(0, yHeight, -0.58));
  }

  return g;
}

// 多樣化微縮建築生成器（讓 30 個單元建築造型豐富緊湊）
function createUnitBuilding(x, y, z, styleIdx, roofColor, wallColor = "#ffffff") {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  const kind = styleIdx % 5;

  if (kind === 0) {
    // 經典繪本斜頂小屋
    g.add(box(1.45, 1.05, 1.3, wallColor, 0, 0, 0));
    const r = cone(1.18, 0.85, roofColor, 0, 1.05, 0, 4);
    r.rotation.y = Math.PI / 4;
    g.add(r);
    g.add(box(0.32, 0.52, 0.05, "#795548", 0, 0, 0.66));
    g.add(box(0.32, 0.32, 0.05, "#fff9c4", 0.4, 0.38, 0.66, 0xfdd835));
  } else if (kind === 1) {
    // 雙層小鐘樓學堂
    g.add(box(1.5, 0.95, 1.25, wallColor, 0, 0, 0));
    g.add(box(0.85, 0.75, 0.85, wallColor, 0, 0.95, 0));
    const r = cone(0.75, 0.7, roofColor, 0, 1.7, 0, 4);
    r.rotation.y = Math.PI / 4;
    g.add(r);
    g.add(ball(0.18, "#ffd54f", 0, 1.32, 0.45, 6));
  } else if (kind === 2) {
    // 荷蘭小風車工坊
    g.add(cyl(0.62, 0.78, 1.45, wallColor, 0, 0, 0, 8));
    g.add(cone(0.75, 0.65, roofColor, 0, 1.45, 0, 8));
    const blades = new THREE.Group();
    blades.position.set(0, 1.15, 0.72);
    blades.add(box(1.5, 0.14, 0.04, "#5d4037", 0, -0.07, 0));
    blades.add(box(0.14, 1.5, 0.04, "#5d4037", 0, -0.75, 0));
    g.add(blades);
    spinningMeshes.push(blades);
  } else if (kind === 3) {
    // 希臘柱小涼亭／視覺館
    g.add(box(1.55, 0.2, 1.35, "#eceff1", 0, 0, 0));
    [[-0.55, -0.45], [0.55, -0.45], [-0.55, 0.45], [0.55, 0.45]].forEach(([px, pz]) => {
      g.add(cyl(0.1, 0.1, 0.95, wallColor, px, 0.2, pz, 6));
    });
    const r = cone(1.22, 0.7, roofColor, 0, 1.15, 0, 4);
    r.rotation.y = Math.PI / 4;
    g.add(r);
  } else {
    // 圓頂天文／圓塔屋
    g.add(cyl(0.72, 0.75, 1.05, wallColor, 0, 0, 0, 10));
    g.add(ball(0.72, roofColor, 0, 1.05, 0, 10));
    g.add(box(0.34, 0.5, 0.1, "#5d4037", 0, 0, 0.72));
  }
  return g;
}

// 各領域專屬中央主題地標 (Domain Landmark Centerpiece)
function createDomainMonument(type, primaryColor, trimColor, yBase) {
  const g = new THREE.Group();
  g.position.set(0, yBase, 0);

  // 圓形石砌底座與紅旗
  g.add(cyl(2.2, 2.4, 0.22, "#e2e8f0", 0, 0, 0, 12));
  g.add(cyl(0.06, 0.06, 2.8, "#94a3b8", -1.5, 0.2, -1.0, 6));
  g.add(box(0.75, 0.45, 0.04, "#ef4444", -1.12, 2.45, -1.0));

  if (type === "lighthouse_whale") {
    // 水池＋小白鯨＋紅白燈塔
    g.add(cyl(1.65, 1.7, 0.15, "#38bdf8", 0, 0.18, 0, 14));
    const whale = ball(0.62, "#0284c7", 0.35, 0.65, 0.2, 10);
    whale.scale.set(1.35, 0.85, 1.0);
    g.add(whale);
    g.add(cyl(0.55, 0.75, 2.5, "#ffffff", -0.65, 0.2, -0.3, 8));
    g.add(cyl(0.62, 0.62, 0.45, "#ef4444", -0.65, 1.6, -0.3, 8));
    g.add(cone(0.68, 0.65, "#ef4444", -0.65, 2.7, -0.3, 8));
  } else if (type === "gym_rainbow") {
    // 彩虹階梯與平衡木館
    g.add(box(1.8, 0.4, 1.1, "#ef5350", 0, 0.2, 0));
    g.add(box(1.4, 0.4, 0.9, "#ffca28", 0, 0.6, 0));
    g.add(box(1.0, 0.4, 0.7, "#42a5f5", 0, 1.0, 0));
    g.add(ball(0.48, "#ab47bc", 0, 1.75, 0, 10));
  } else if (type === "book_tower") {
    // 敞開的立體巨型繪本書台
    g.add(box(1.9, 0.35, 1.3, "#d97706", 0, 0.2, 0));
    const pageL = box(0.85, 0.15, 1.15, "#fffbeb", -0.44, 0.6, 0);
    pageL.rotation.z = 0.22;
    const pageR = box(0.85, 0.15, 1.15, "#fffbeb", 0.44, 0.6, 0);
    pageR.rotation.z = -0.22;
    g.add(pageL, pageR);
    g.add(cyl(0.38, 0.45, 1.9, primaryColor, 0, 0.5, -0.65, 8));
    g.add(cone(0.52, 0.65, trimColor, 0, 2.4, -0.65, 8));
  } else if (type === "clock_pyramid") {
    // 幾何金字塔與時鐘塔
    g.add(cone(1.15, 1.7, "#f59e0b", -0.45, 0.2, 0.2, 4));
    g.add(box(0.95, 2.2, 0.95, primaryColor, 0.55, 0.2, -0.25));
    g.add(ball(0.34, "#fef08a", 0.55, 1.85, 0.26, 8));
    g.add(cone(0.75, 0.75, trimColor, 0.55, 2.4, -0.25, 4));
  } else if (type === "ferris_camp") {
    // 彩色摩天輪地標
    g.add(box(0.2, 1.8, 0.2, "#475569", -0.35, 0.2, 0));
    g.add(box(0.2, 1.8, 0.2, "#475569", 0.35, 0.2, 0));
    const wheel = new THREE.Mesh(new THREE.TorusGeometry(1.1, 0.09, 6, 16), mat(primaryColor));
    wheel.position.set(0, 1.95, 0);
    g.add(wheel);
    spinningMeshes.push(wheel);
  } else {
    // 精緻圓頂主題城堡地標
    g.add(box(1.75, 1.1, 1.45, "#ffffff", 0, 0.2, 0));
    g.add(cyl(0.68, 0.75, 1.2, primaryColor, 0, 1.3, 0, 10));
    g.add(cone(0.88, 0.85, trimColor, 0, 2.5, 0, 10));
  }

  return g;
}

function clearThreeWorld() {
  if (worldGroup) {
    scene.remove(worldGroup);
  }
  worldGroup = new THREE.Group();
  scene.add(worldGroup);
  labelsLayer.innerHTML = "";
  pinItems.length = 0;
  spinningMeshes.length = 0;
}

function add3DPin(htmlContent, worldVec, extraClass, onClickFn, isAlwaysVisible = true) {
  const el = document.createElement("div");
  el.className = "label-pin " + (extraClass || "");
  el.innerHTML = htmlContent;
  el.onclick = (e) => {
    e.stopPropagation();
    if (!dragMoved && onClickFn) onClickFn();
  };
  labelsLayer.appendChild(el);
  pinItems.push({ el, pos: worldVec, always: isAlwaysVisible });
}

// ==========================================
// 場景一：🌊 10 大領域群島大世界 (World Archipelago)
// ==========================================
function buildWorldArchipelagoScene() {
  clearThreeWorld();

  // 中央總廣場島
  const centerR = 4.8;
  const centerHex = createHexPlatform(centerR, 2.35, "#fdfbf7", "#38bdf8", "#8d6e63", 0, 0);
  worldGroup.add(centerHex.group);
  worldGroup.add(createDomainMonument("book_tower", "#0284c7", "#38bdf8", centerHex.topY));
  worldGroup.add(createTree(-2.8, centerHex.topY, 1.6, 1.1, 0));
  worldGroup.add(createTree(2.8, centerHex.topY, -1.5, 1.0, 1));
  worldGroup.add(createMascot(1.8, centerHex.topY, 2.0, "#0284c7", "#fde047"));

  add3DPin(
    `<div class="label-pill pill-center"><div class="pin-dot"></div><span class="pin-title">🏫 特教教材共學總廣場</span><span class="pin-badge" style="background:rgba(255,255,255,0.22);color:#fff;">240 站</span></div>`,
    new THREE.Vector3(0, centerHex.topY + 3.5, 0),
    "",
    () => resetCamera(),
    true
  );

  // 10 座領域島嶼大幅拉開空間距離（遍布整個畫面視野，不擠在中央，並以跨海道路橋樑彼此相連）
  const coords = [
    { x: -17.5, z: -9.5,  h: 2.15, r: 4.0, bridgeFrom: -1 }, // 0: 特需生活管理島（內環左前）
    { x: 0.0,   z: -18.5, h: 2.20, r: 4.0, bridgeFrom: -1 }, // 1: 功能性動作島（內環正北）
    { x: 17.5,  z: -9.5,  h: 2.15, r: 4.0, bridgeFrom: -1 }, // 2: 語文繪本島（內環右前）
    { x: 16.5,  z: 9.5,   h: 2.10, r: 4.0, bridgeFrom: -1 }, // 3: 健體活力島（內環右後）
    { x: -16.5, z: 9.5,   h: 2.10, r: 4.0, bridgeFrom: -1 }, // 4: 數學邏輯島（內環左後）
    { x: -32.5, z: -1.0,  h: 2.00, r: 3.9, bridgeFrom: 0  }, // 5: 自然探索島（外環極左）
    { x: -14.5, z: -25.5, h: 2.05, r: 3.9, bridgeFrom: 1  }, // 6: 社會文化島（外環左北）
    { x: 14.5,  z: -25.5, h: 2.05, r: 3.9, bridgeFrom: 1  }, // 7: 綜合實踐島（外環右北）
    { x: 32.5,  z: -1.0,  h: 2.00, r: 3.9, bridgeFrom: 2  }, // 8: 藝術人文島（外環極右）
    { x: 0.0,   z: 20.5,  h: 2.05, r: 3.9, bridgeFrom: 4  }  // 9: 生活啟蒙島（外環正南）
  ];

  // 額外環狀聯絡道路（讓外環與內環形成四通八達的跨海公路網）
  const extraLinks = [
    [4, 5], [2, 7], [0, 6], [3, 8], [3, 9]
  ];

  DOMAINS_DATA.forEach((d, idx) => {
    const c = coords[idx];
    const plat = createHexPlatform(c.r, c.h, d.groundColor, d.trimColor, "#795548", c.x, c.z);
    worldGroup.add(plat.group);

    // 島內十字石板道路
    plat.group.add(box(c.r * 1.45, 0.06, 0.72, "#f5ebe0", 0, plat.topY, 0));
    plat.group.add(box(0.72, 0.06, c.r * 1.45, "#f5ebe0", 0, plat.topY, 0));

    // 島上精緻聚落（主地標＋兩棟小屋＋樹木＋吉祥物＋街燈，彼此保持清晰間距）
    const mainBld = createDomainMonument(d.landmarkType, d.color, d.trimColor, plat.topY);
    mainBld.scale.set(0.76, 0.76, 0.76);
    plat.group.add(mainBld);

    plat.group.add(createUnitBuilding(-1.85, plat.topY, 1.35, idx, d.color));
    plat.group.add(createUnitBuilding(1.85, plat.topY, 1.35, idx + 1, d.trimColor));
    plat.group.add(createTree(-2.25, plat.topY, -1.55, 0.95, idx));
    plat.group.add(createTree(2.25, plat.topY, -1.5, 0.9, idx + 1));
    plat.group.add(createMascot(0.0, plat.topY, 2.45, d.color, "#ffd54f"));
    plat.group.add(createStreetLamp(-1.25, plat.topY, 2.3));

    // 主跨海連接道路橋樑（內環連中央島，外環連內環島）
    if (c.bridgeFrom === -1) {
      worldGroup.add(createRoadBridge(0, 0, centerR, c.x, c.z, c.r, 1.95));
    } else {
      const p = coords[c.bridgeFrom];
      worldGroup.add(createRoadBridge(p.x, p.z, p.r, c.x, c.z, c.r, 1.9));
    }

    // 領域島浮動膠囊標籤
    add3DPin(
      `<div class="label-pill" style="border-color:${d.trimColor};">
        <span style="font-size:18px;">${d.icon}</span>
        <span class="pin-title">${d.islandName}</span>
        <span class="pin-badge">${d.ownCount}站</span>
      </div>`,
      new THREE.Vector3(c.x, plat.topY + 2.9, c.z),
      "",
      () => enterDomainIsland(d.id),
      true
    );
  });

  extraLinks.forEach(([iA, iB]) => {
    const a = coords[iA], b = coords[iB];
    worldGroup.add(createRoadBridge(a.x, a.z, a.r, b.x, b.z, b.r, 1.88));
  });

  // 海面小帆船點綴
  [[-26, 15], [26, 14.5], [-25, -18], [25, -18], [-8, 10], [9, -9]].forEach(([bx, bz], i) => {
    const boat = new THREE.Group();
    boat.position.set(bx, 0.1, bz);
    boat.rotation.y = i * 1.1;
    boat.add(box(1.4, 0.35, 0.8, "#ef4444", 0, 0, 0));
    boat.add(cone(0.52, 1.2, "#ffffff", 0, 0.35, 0, 3));
    worldGroup.add(boat);
  });
}

// ==========================================
// 場景二：🏝️ 單一領域獨立 3D 導覽島（對應三個學習階段）
// ==========================================
function buildDomainIslandScene(domainId) {
  clearThreeWorld();
  const d = DOMAIN_MAP[domainId];
  if (!d) return;

  // 1. 中央領域主題廣場 (獨立中央島，與三階段島嶼拉開寬闊海面距離並以跨海道路連接)
  const centerR = 4.4;
  const centerHex = createHexPlatform(centerR, 2.25, "#fdfbf7", d.trimColor, "#795548", 0, 0);
  worldGroup.add(centerHex.group);
  centerHex.group.add(box(centerR * 1.5, 0.06, 0.8, "#f5ebe0", 0, centerHex.topY, 0));
  centerHex.group.add(box(0.8, 0.06, centerR * 1.5, "#f5ebe0", 0, centerHex.topY, 0));
  worldGroup.add(createDomainMonument(d.landmarkType, d.color, d.trimColor, centerHex.topY));
  worldGroup.add(createBench(-1.8, centerHex.topY, 1.65, 0.5));
  worldGroup.add(createBench(1.8, centerHex.topY, 1.65, -0.5));
  worldGroup.add(createStreetLamp(-2.2, centerHex.topY, 0.25));
  worldGroup.add(createStreetLamp(2.2, centerHex.topY, 0.25));
  worldGroup.add(createMascot(0, centerHex.topY, 2.4, d.color, "#fde047"));

  add3DPin(
    `<div class="label-pill pill-center">
      <span>${d.icon}</span>
      <span class="pin-title">${d.islandName}共學廣場</span>
    </div>`,
    new THREE.Vector3(0, centerHex.topY + 3.3, 0),
    "",
    () => selectStage("all"),
    true
  );

  // 三個學習階段分島配置（大幅拉開島嶼間距，藉由跨海景觀道路與橋樑連接，畫面清晰不擁擠）
  const stageConfigs = [
    {
      stage: "1",
      title: "🌱 第一階段：啟蒙村",
      topColor: "#e8f5e9",
      trimColor: "#43a047",
      roofA: "#ef5350",
      roofB: "#66bb6a",
      hexA: { x: -16.5, z: -7.5, r: 4.5, h: 2.30 },
      hexB: { x: -30.5, z: -2.0, r: 4.5, h: 2.45 },
      hdrPos: new THREE.Vector3(-23.5, 5.8, -6.2),
      hdrClass: "pill-s1-hdr"
    },
    {
      stage: "2",
      title: "🌿 第二階段：實踐鎮",
      topColor: "#e3f2fd",
      trimColor: "#1e88e5",
      roofA: "#1e88e5",
      roofB: "#ffa726",
      hexA: { x: 16.5, z: -7.5, r: 4.5, h: 2.30 },
      hexB: { x: 30.5, z: -2.0, r: 4.5, h: 2.45 },
      hdrPos: new THREE.Vector3(23.5, 5.8, -6.2),
      hdrClass: "pill-s2-hdr"
    },
    {
      stage: "3",
      title: "🌳 第三階段：進階城",
      topColor: "#fff3e0",
      trimColor: "#fb8c00",
      roofA: "#ab47bc",
      roofB: "#fb8c00",
      hexA: { x: -10.5, z: 16.5, r: 4.5, h: 2.10 },
      hexB: { x: 10.5,  z: 16.5, r: 4.5, h: 2.20 },
      hdrPos: new THREE.Vector3(0, 5.5, 19.5),
      hdrClass: "pill-s3-hdr"
    }
  ];

  // 每個六角島上的 5 個單元建築位置（隨島嶼放大與道路鋪設，拉開建築彼此間距）
  const localSlots = [
    { dx: -2.10, dz: -1.75 },
    { dx: 2.10,  dz: -1.75 },
    { dx: 0.0,   dz: 0.05 },
    { dx: -2.10, dz: 1.85 },
    { dx: 2.10,  dz: 1.85 }
  ];

  stageConfigs.forEach(sc => {
    const units = d.stages[sc.stage] || [];
    const pA = createHexPlatform(sc.hexA.r, sc.hexA.h, sc.topColor, sc.trimColor, "#795548", sc.hexA.x, sc.hexA.z);
    const pB = createHexPlatform(sc.hexB.r, sc.hexB.h, sc.topColor, sc.trimColor, "#6d4c41", sc.hexB.x, sc.hexB.z);
    worldGroup.add(pA.group, pB.group);

    // 島內十字石板路（連接五棟單元小屋與跨海大橋）
    pA.group.add(box(sc.hexA.r * 1.55, 0.06, 0.72, "#f5ebe0", 0, pA.topY, 0));
    pA.group.add(box(0.72, 0.06, sc.hexA.r * 1.55, "#f5ebe0", 0, pA.topY, 0));
    pB.group.add(box(sc.hexB.r * 1.55, 0.06, 0.72, "#f5ebe0", 0, pB.topY, 0));
    pB.group.add(box(0.72, 0.06, sc.hexB.r * 1.55, "#f5ebe0", 0, pB.topY, 0));

    // 1. 連接中央廣場島 (0,0) 至該階段上學期島 (hexA) 的跨海景觀道路
    worldGroup.add(createRoadBridge(0, 0, centerR, sc.hexA.x, sc.hexA.z, sc.hexA.r, 1.98));

    // 若為第三階段，也從中央廣場島連接一條對稱跨海道路至 hexB
    if (sc.stage === "3") {
      worldGroup.add(createRoadBridge(0, 0, centerR, sc.hexB.x, sc.hexB.z, sc.hexB.r, 1.98));
    }

    // 2. 連接上學期島 (hexA) 與下學期島 (hexB) 的跨海景觀道路
    worldGroup.add(createRoadBridge(sc.hexA.x, sc.hexA.z, sc.hexA.r, sc.hexB.x, sc.hexB.z, sc.hexB.r, 2.05));

    // 階段聚落主標題膠囊
    add3DPin(
      `<div class="label-pill pill-stage-header ${sc.hdrClass}">
        <span class="pin-title">${sc.title}</span>
        <span class="pin-badge">${units.length} 單元</span>
      </div>`,
      sc.hdrPos,
      `stage-hdr-${sc.stage}`,
      () => selectStage(sc.stage),
      true
    );

    // 擺放該階段的 10 個單元立體建築（前 5 個上學期在 hexA，後 5 個下學期在 hexB）
    units.forEach((u, idx) => {
      const isSecondHalf = idx >= 5;
      const hex = isSecondHalf ? sc.hexB : sc.hexA;
      const topY = isSecondHalf ? pB.topY : pA.topY;
      const slot = localSlots[idx % 5];
      const wx = hex.x + slot.dx;
      const wz = hex.z + slot.dz;

      const roofColor = isSecondHalf ? sc.roofB : sc.roofA;
      const bld = createUnitBuilding(wx, topY, wz, idx, roofColor);
      bld.scale.set(0.74, 0.74, 0.74);
      worldGroup.add(bld);

      // 全島總覽時預設顯示每學期前 2 個代表單元標籤；點進該階段或開啟「全部標籤」時 10 個全開
      const isFeatured = (idx % 5 === 0) || (idx % 5 === 1);
      add3DPin(
        `<div class="label-pill">
          <div class="pin-dot"></div>
          <span class="pin-title">${u.name}</span>
          <span class="pin-badge">${u.sem}U${u.u}</span>
        </div>`,
        new THREE.Vector3(wx, topY + 1.95, wz),
        `stage-${sc.stage} unit-pin`,
        () => openUnitModal(u.uid),
        isFeatured
      );
    });

    // 聚落裝飾（小樹、街燈、小吉祥物）
    worldGroup.add(createTree(sc.hexA.x - 3.1, pA.topY, sc.hexA.z, 0.9, 0));
    worldGroup.add(createTree(sc.hexB.x + 3.1, pB.topY, sc.hexB.z - 0.5, 0.95, 1));
    worldGroup.add(createMascot(sc.hexA.x, pA.topY, sc.hexA.z + 2.8, sc.trimColor, "#ffd54f"));
    worldGroup.add(createStreetLamp(sc.hexB.x, pB.topY, sc.hexB.z - 2.8));
  });

  // 海面玩具紅帆船
  [[-22, 10], [22, 10], [0, -15]].forEach(([bx, bz], i) => {
    const boat = new THREE.Group();
    boat.position.set(bx, 0.1, bz);
    boat.rotation.y = -0.4 + i * 0.9;
    boat.add(box(1.4, 0.35, 0.8, "#e53935", 0, 0, 0));
    boat.add(cone(0.52, 1.2, "#ffffff", 0, 0.35, 0, 3));
    worldGroup.add(boat);
  });
}

// ==========================================
// 導覽切換與 UI 連動
// ==========================================
function renderDomainBar() {
  const bar = document.getElementById("domain-bar");
  let html = `
    <button class="domain-chip ${currentMode === 'world' ? 'active' : ''}" onclick="enterWorldView()">
      <span>🌊</span>
      <span>10 大領域群島總覽</span>
      <span class="chip-count">240站</span>
    </button>
  `;
  DOMAINS_DATA.forEach(d => {
    const active = currentMode === d.id ? "active" : "";
    html += `
      <button class="domain-chip ${active}" onclick="enterDomainIsland('${d.id}')">
        <span>${d.icon}</span>
        <span>${d.islandName}</span>
        <span class="chip-count">${d.ownCount}</span>
      </button>
    `;
  });
  bar.innerHTML = html;
}

function enterWorldView(pushHash = true) {
  currentMode = "world";
  currentStageFilter = "all";
  if (pushHash) history.replaceState(null, "", "#world");

  document.getElementById("btn-back-world").style.display = "none";
  document.getElementById("stage-switcher").style.display = "none";
  document.getElementById("unit-dock").classList.remove("visible");
  document.getElementById("btn-all-pins").style.display = "none";

  document.getElementById("top-logo").innerText = "🏝️";
  document.getElementById("top-title").innerText = "高雄特教國小部｜3D 領域群島總入口";
  document.getElementById("top-subtitle").innerText = "10 大領域島嶼 × 三個學習階段 × 240 個互動單元";

  document.getElementById("banner-title").innerText = "🌊 特教學習大世界（10 大領域群島）";
  document.getElementById("banner-desc").innerText = "點擊海面上任一座領域島嶼，即可進入該領域的「第一、二、三學習階段」立體教材聚落！";
  document.getElementById("banner-note").style.display = "none";

  renderDomainBar();
  buildWorldArchipelagoScene();
  targetLook.set(0, 0, -2.5);
  spherical.radius = 56;
  spherical.theta = 0.08;
  spherical.phi = 0.96;

  if (displayView === "list") renderListView();
}

function enterDomainIsland(domainId, pushHash = true) {
  const d = DOMAIN_MAP[domainId];
  if (!d) return;
  currentMode = domainId;
  currentStageFilter = "all";
  if (pushHash) history.replaceState(null, "", `#domain=${domainId}`);

  document.getElementById("btn-back-world").style.display = "inline-flex";
  document.getElementById("stage-switcher").style.display = "flex";
  document.getElementById("unit-dock").classList.add("visible");
  document.getElementById("btn-all-pins").style.display = "flex";

  document.getElementById("top-logo").innerText = d.icon;
  document.getElementById("top-title").innerText = `${d.islandName}｜三個學習階段導覽`;
  document.getElementById("top-subtitle").innerText = d.themeDesc;

  document.getElementById("banner-title").innerText = `${d.icon} ${d.islandName}`;
  document.getElementById("banner-desc").innerText = d.themeDesc;
  const noteEl = document.getElementById("banner-note");
  if (d.stage1Note) {
    noteEl.innerText = "💡 " + d.stage1Note;
    noteEl.style.display = "block";
  } else {
    noteEl.style.display = "none";
  }

  renderDomainBar();
  buildDomainIslandScene(domainId);
  selectStage("all");

  if (displayView === "list") renderListView();
}

function selectStage(stage) {
  currentStageFilter = stage;
  document.querySelectorAll(".stage-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.stage === stage);
  });

  if (stage === "all") {
    targetLook.set(0, 0, 2.0);
    spherical.radius = 50;
    spherical.theta = 0.0;
    spherical.phi = 0.98;
  } else if (stage === "1") {
    targetLook.set(-23.0, 2.0, -4.8);
    spherical.radius = 27;
    spherical.theta = 0.48;
    spherical.phi = 0.96;
  } else if (stage === "2") {
    targetLook.set(23.0, 2.0, -4.8);
    spherical.radius = 27;
    spherical.theta = -0.48;
    spherical.phi = 0.96;
  } else if (stage === "3") {
    targetLook.set(0, 2.0, 16.5);
    spherical.radius = 27;
    spherical.theta = 0.05;
    spherical.phi = 0.96;
  }

  renderQuickDock();
}

function renderQuickDock() {
  if (currentMode === "world") return;
  const d = DOMAIN_MAP[currentMode];
  const dockList = document.getElementById("dock-list");
  const dockTitle = document.getElementById("dock-title");
  const dockCount = document.getElementById("dock-count");

  let units = [];
  if (currentStageFilter === "all") {
    units = [...(d.stages["1"] || []), ...(d.stages["2"] || []), ...(d.stages["3"] || [])];
    dockTitle.innerText = `📍 ${d.islandName}・全部階段單元快速點選：`;
  } else {
    units = d.stages[currentStageFilter] || [];
    const stNames = { "1": "🌱 第一階段（啟蒙村）", "2": "🌿 第二階段（實踐鎮）", "3": "🌳 第三階段（進階城）" };
    dockTitle.innerText = `📍 ${stNames[currentStageFilter]} 單元清單：`;
  }
  dockCount.innerText = `共 ${units.length} 單元`;

  dockList.innerHTML = units.map(u => `
    <button class="dock-unit-btn s${u.stage}" onclick="openUnitModal(${u.uid})">
      <span style="color:var(--text-muted);font-size:12px;">${u.sem}U${u.u}</span>
      <span>${u.name}</span>
    </button>
  `).join("");
}

function toggleShowAllPins() {
  showAll30Pins = !showAll30Pins;
  document.getElementById("btn-all-pins").classList.toggle("active", showAll30Pins);
}

// ==========================================
// 🎁 教材寶箱視窗 (Option A)
// ==========================================
function openUnitModal(uid) {
  const u = UNIT_MAP[uid];
  if (!u) return;

  // 建立同領域的上下單元切換序列
  if (currentMode !== "world" && DOMAIN_MAP[currentMode]) {
    const d = DOMAIN_MAP[currentMode];
    activeModalUnitList = [...(d.stages["1"] || []), ...(d.stages["2"] || []), ...(d.stages["3"] || [])];
  } else {
    activeModalUnitList = ALL_UNITS_FLAT;
  }
  activeModalIndex = activeModalUnitList.findIndex(item => item.uid === uid);

  document.getElementById("m-cover").src = u.cover;
  document.getElementById("m-domain-badge").innerText = u.origDomain;

  const stLabel = u.stage === 1 ? "🌱 第一階段" : u.stage === 2 ? "🌿 第二階段" : "🌳 第三階段";
  const stBadge = document.getElementById("m-stage-badge");
  stBadge.innerText = `${stLabel}・${u.sem} 第 ${u.u} 單元`;
  stBadge.className = `m-badge m-badge-s${u.stage}`;

  document.getElementById("m-title").innerText = u.name;

  document.getElementById("m-link-ppt").href = `${u.url}#teaching`;
  document.getElementById("m-link-video").href = `${u.url}#videos`;
  document.getElementById("m-link-quiz").href = `${u.url}#quizzes`;
  document.getElementById("m-link-cards").href = `${u.url}#flashcards`;
  document.getElementById("m-link-wheel").href = `${u.url}#teaching`;
  document.getElementById("m-link-manual").href = u.manual;
  document.getElementById("m-link-site").href = u.url;

  document.getElementById("treasure-modal").classList.add("open");
}

function stepModalUnit(dir) {
  if (!activeModalUnitList.length) return;
  activeModalIndex = (activeModalIndex + dir + activeModalUnitList.length) % activeModalUnitList.length;
  openUnitModal(activeModalUnitList[activeModalIndex].uid);
}

function closeModal() {
  document.getElementById("treasure-modal").classList.remove("open");
}

// ==========================================
// 📋 領域 × 三階段清單模式
// ==========================================
function toggleDisplayMode() {
  const stage3d = document.getElementById("stage-3d");
  const listView = document.getElementById("list-view");
  const icon = document.getElementById("view-mode-icon");
  const text = document.getElementById("view-mode-text");

  if (displayView === "3d") {
    displayView = "list";
    stage3d.style.display = "none";
    listView.style.display = "block";
    icon.innerText = "🏝️";
    text.innerText = "返回 3D 島嶼";
    renderListView();
  } else {
    displayView = "3d";
    stage3d.style.display = "block";
    listView.style.display = "none";
    icon.innerText = "📋";
    text.innerText = "領域清單模式";
    onResize();
  }
}

function renderListView() {
  const container = document.getElementById("list-container");
  const targetDomains = currentMode === "world" ? DOMAINS_DATA : [DOMAIN_MAP[currentMode]];

  container.innerHTML = targetDomains.map(d => {
    const stagesHtml = ["1", "2", "3"].map(st => {
      const units = d.stages[st] || [];
      if (!units.length) return "";
      const stTitle = st === "1" ? "🌱 第一學習階段（基礎啟蒙）" : st === "2" ? "🌿 第二學習階段（日常實踐）" : "🌳 第三學習階段（進階挑戰）";
      const stColor = st === "1" ? "var(--s1-color)" : st === "2" ? "var(--s2-color)" : "var(--s3-color)";
      const note = (st === "1" && d.stage1Note) ? `<span style="font-size:13px;color:#b45309;">（${d.stage1Note}）</span>` : "";

      const cards = units.map(u => `
        <div class="unit-visual-card" onclick="openUnitModal(${u.uid})">
          <img class="unit-card-thumb" src="${u.cover}" alt="${u.name}" loading="lazy">
          <div class="unit-card-body">
            <span class="unit-card-sem">${u.origDomain}｜${u.sem} 第 ${u.u} 單元</span>
            <span class="unit-card-name">${u.name}</span>
          </div>
        </div>
      `).join("");

      return `
        <div class="list-stage-block">
          <div class="list-stage-title" style="color:${stColor};">
            <span>${stTitle} ${note}</span>
            <span style="font-size:15px;color:var(--text-muted);">共 ${units.length} 單元</span>
          </div>
          <div class="unit-cards-grid">${cards}</div>
        </div>
      `;
    }).join("");

    return `
      <div class="list-domain-header">
        <div>
          <h2 style="font-size:26px;font-weight:900;">${d.icon} ${d.islandName}</h2>
          <p style="color:var(--text-muted);font-weight:700;margin-top:4px;">${d.themeDesc}</p>
        </div>
        <button class="icon-pill-btn primary-toggle" onclick="displayView='3d';document.getElementById('stage-3d').style.display='block';document.getElementById('list-view').style.display='none';document.getElementById('view-mode-icon').innerText='📋';document.getElementById('view-mode-text').innerText='領域清單模式';enterDomainIsland('${d.id}');onResize();">
          🏝️ 進入此領域 3D 島嶼
        </button>
      </div>
      ${stagesHtml}
    `;
  }).join("<hr style='margin:40px 0;border:none;border-top:3px dashed #cbd5e1;'>");
}

// ==========================================
// 🔍 全域 240 單元即時搜尋
// ==========================================
function setupSearch() {
  const input = document.getElementById("unit-search");
  const dropdown = document.getElementById("search-results");

  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    if (!q) {
      dropdown.classList.remove("open");
      return;
    }
    const matches = ALL_UNITS_FLAT.filter(u =>
      u.name.toLowerCase().includes(q) ||
      u.origDomain.toLowerCase().includes(q) ||
      u.sem.includes(q)
    ).slice(0, 15);

    if (!matches.length) {
      dropdown.innerHTML = `<div style="padding:12px;color:var(--text-muted);font-weight:700;">找不到符合「${q}」的單元</div>`;
    } else {
      dropdown.innerHTML = matches.map(u => `
        <div class="search-item" onclick="openUnitModal(${u.uid});document.getElementById('search-results').classList.remove('open');">
          <div>
            <div class="search-item-title">${u.name}</div>
            <div class="search-item-meta">${u.origDomain}｜第${u.stage}階段・${u.sem} 第 ${u.u} 單元</div>
          </div>
          <span style="color:#0284c7;font-weight:800;">開啟 →</span>
        </div>
      `).join("");
    }
    dropdown.classList.add("open");
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-box")) {
      dropdown.classList.remove("open");
    }
  });
}

// ==========================================
// Three.js 初始化與動畫迴圈
// ==========================================
function initThreeEngine() {
  const stageEl = document.getElementById("stage-3d");
  const canvas = document.getElementById("canvas-3d");
  labelsLayer = document.getElementById("labels-layer");

  scene = new THREE.Scene();
  scene.background = new THREE.Color("#e6f2f5");

  camera = new THREE.PerspectiveCamera(38, stageEl.clientWidth / stageEl.clientHeight, 0.5, 300);

  renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(stageEl.clientWidth, stageEl.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  hemiLight = new THREE.HemisphereLight(0xffffff, 0xcbe4ec, 0.72);
  scene.add(hemiLight);

  sunLight = new THREE.DirectionalLight(0xfffbeb, 0.92);
  sunLight.position.set(34, 55, 32);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.width = 2048;
  sunLight.shadow.mapSize.height = 2048;
  sunLight.shadow.camera.near = 10;
  sunLight.shadow.camera.far = 150;
  const d = 46;
  sunLight.shadow.camera.left = -d;
  sunLight.shadow.camera.right = d;
  sunLight.shadow.camera.top = d;
  sunLight.shadow.camera.bottom = -d;
  sunLight.shadow.bias = -0.0005;
  scene.add(sunLight);

  backLight = new THREE.DirectionalLight(0xbae6fd, 0.32);
  backLight.position.set(-28, 22, -24);
  scene.add(backLight);

  // 海平面
  seaMesh = new THREE.Mesh(
    new THREE.PlaneGeometry(360, 360, 1, 1),
    new THREE.MeshLambertMaterial({ color: 0xbae6fd, transparent: true, opacity: 0.55 })
  );
  seaMesh.rotation.x = -Math.PI / 2;
  seaMesh.position.y = -0.15;
  seaMesh.receiveShadow = true;
  scene.add(seaMesh);

  // 滑鼠與觸控事件（左鍵旋轉視角、右鍵或按住 Shift 拖曳平移畫面、滾輪縮放）
  let isPanning = false;
  stageEl.addEventListener("contextmenu", e => e.preventDefault());
  stageEl.addEventListener("pointerdown", e => {
    isDragging = true;
    isPanning = (e.button === 2 || e.shiftKey);
    dragMoved = false;
    autoTour = false;
    document.getElementById("btn-tour").classList.remove("active");
    prevPointer = { x: e.clientX, y: e.clientY };
  });
  window.addEventListener("pointermove", e => {
    if (!isDragging) return;
    const dx = e.clientX - prevPointer.x;
    const dy = e.clientY - prevPointer.y;
    if (Math.hypot(dx, dy) > 4) dragMoved = true;
    prevPointer = { x: e.clientX, y: e.clientY };
    if (isPanning || e.shiftKey) {
      const panSpeed = spherical.radius * 0.0014;
      const cosT = Math.cos(spherical.theta);
      const sinT = Math.sin(spherical.theta);
      targetLook.x -= (dx * cosT - dy * sinT) * panSpeed;
      targetLook.z -= (-dx * sinT - dy * cosT) * panSpeed;
    } else {
      spherical.theta -= dx * 0.0065;
      spherical.phi = Math.max(0.32, Math.min(1.38, spherical.phi - dy * 0.0065));
    }
  });
  window.addEventListener("pointerup", () => { isDragging = false; isPanning = false; });
  stageEl.addEventListener("wheel", e => {
    spherical.radius = Math.max(14, Math.min(92, spherical.radius + e.deltaY * 0.032));
  }, { passive: true });
  window.addEventListener("resize", onResize);

  // 根據初始 Hash 或預設領域載入
  applyRouteFromHash();
  window.addEventListener("hashchange", applyRouteFromHash);

  animateLoop();
}

function applyRouteFromHash() {
  const h = location.hash.replace(/^#/, "");
  if (h.startsWith("domain=")) {
    const domId = h.split("=")[1];
    if (DOMAIN_MAP[domId]) {
      enterDomainIsland(domId, false);
      return;
    }
  }
  if (DEFAULT_DOMAIN_ID && DOMAIN_MAP[DEFAULT_DOMAIN_ID] && !h) {
    enterDomainIsland(DEFAULT_DOMAIN_ID, false);
    return;
  }
  enterWorldView(false);
}

function onResize() {
  const stageEl = document.getElementById("stage-3d");
  if (!stageEl || stageEl.clientWidth === 0) return;
  camera.aspect = stageEl.clientWidth / stageEl.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(stageEl.clientWidth, stageEl.clientHeight);
}

function resetCamera() {
  if (currentMode === "world") {
    targetLook.set(0, 0, -2.5);
    spherical.radius = 56;
    spherical.theta = 0.08;
    spherical.phi = 0.96;
  } else {
    selectStage("all");
  }
}

function toggleTour() {
  autoTour = !autoTour;
  document.getElementById("btn-tour").classList.toggle("active", autoTour);
}

function cycleTimeOfDay() {
  todState = (todState + 1) % 3;
  const btn = document.getElementById("btn-tod");
  if (todState === 0) {
    btn.innerText = "☀️ 時段";
    scene.background.set("#e6f2f5");
    seaMesh.material.color.set("#bae6fd");
    hemiLight.color.setHex(0xffffff);
    sunLight.color.setHex(0xfffbeb);
    sunLight.intensity = 0.92;
  } else if (todState === 1) {
    btn.innerText = "🌅 夕陽";
    scene.background.set("#ffedd5");
    seaMesh.material.color.set("#fdba74");
    hemiLight.color.setHex(0xfed7aa);
    sunLight.color.setHex(0xf97316);
    sunLight.intensity = 1.05;
  } else {
    btn.innerText = "🌙 星夜";
    scene.background.set("#0f172a");
    seaMesh.material.color.set("#1e293b");
    hemiLight.color.setHex(0x334155);
    sunLight.color.setHex(0x38bdf8);
    sunLight.intensity = 0.48;
  }
}

function updateLabelsProjection() {
  const stageEl = document.getElementById("stage-3d");
  const w = stageEl.clientWidth;
  const h = stageEl.clientHeight;

  pinItems.forEach(item => {
    // 在領域島內根據階段篩選決定顯示邏輯
    if (currentMode !== "world" && item.el.classList.contains("unit-pin")) {
      const belongStage = item.el.classList.contains("stage-1") ? "1" :
                          item.el.classList.contains("stage-2") ? "2" : "3";
      if (currentStageFilter === "all") {
        if (!item.always && !showAll30Pins) {
          item.el.style.display = "none";
          return;
        }
        item.el.style.opacity = "1";
      } else {
        if (belongStage !== currentStageFilter) {
          item.el.style.display = "none";
          return;
        }
        item.el.style.opacity = "1";
      }
    }

    const v = item.pos.clone();
    if (worldGroup) v.y += worldGroup.position.y;
    v.project(camera);

    if (v.z > 1) {
      item.el.style.display = "none";
      return;
    }

    item.el.style.display = "block";
    const x = (v.x * 0.5 + 0.5) * w;
    const y = (-(v.y * 0.5) + 0.5) * h;
    item.el.style.left = `${x}px`;
    item.el.style.top = `${y}px`;
    item.el.style.zIndex = String(Math.floor((1 - v.z) * 100));
  });
}

function animateLoop() {
  requestAnimationFrame(animateLoop);

  if (autoTour) {
    spherical.theta += 0.0038;
  }

  currentLook.lerp(targetLook, 0.08);
  const cx = spherical.radius * Math.sin(spherical.phi) * Math.sin(spherical.theta);
  const cy = spherical.radius * Math.cos(spherical.phi);
  const cz = spherical.radius * Math.sin(spherical.phi) * Math.cos(spherical.theta);
  camera.position.set(cx + currentLook.x, cy + currentLook.y, cz + currentLook.z);
  camera.lookAt(currentLook);

  const t = Date.now() * 0.0016;
  if (worldGroup) {
    worldGroup.position.y = Math.sin(t) * 0.14;
  }
  spinningMeshes.forEach(m => { m.rotation.z += 0.015; });

  renderer.render(scene, camera);
  updateLabelsProjection();
}

window.addEventListener("keydown", e => {
  if (e.key === "Escape") closeModal();
});

window.addEventListener("DOMContentLoaded", () => {
  setupSearch();
  initThreeEngine();
});
</script>
</body>
</html>
"""


def main():
    update_classic_index()
    all_units = load_all_240_units()
    domains_data = build_domains_payload(all_units)

    json_str = json.dumps(domains_data, ensure_ascii=False)

    # 1. 產出總入口 index.html (預設進入 10 大領域群島大世界)
    hub_html = (
        HTML_TEMPLATE
        .replace("__DOMAINS_DATA__", json_str)
        .replace("__DEFAULT_DOMAIN_ID__", "")
    )
    hub_index_path = os.path.join(ROOT, "index.html")
    open(hub_index_path, "w", encoding="utf-8").write(hub_html)
    print(f"✅ 已寫入 3D 領域群島總入口：{hub_index_path}（10 大領域島、240 單元）")

    # 2. 產出特需生活管理島直達頁 island-lifeskill.html（預設直接進入 selfcare 島，且可返回群島總覽）
    life_html = (
        HTML_TEMPLATE
        .replace("__DOMAINS_DATA__", json_str)
        .replace("__DEFAULT_DOMAIN_ID__", "selfcare")
    )
    life_path = os.path.join(ROOT, "island-lifeskill.html")
    open(life_path, "w", encoding="utf-8").write(life_html)
    print(f"✅ 已同步更新特需生活管理島直達頁：{life_path}")

    if os.path.isdir(PROTO_DIR):
        proto_index = os.path.join(PROTO_DIR, "index.html")
        open(proto_index, "w", encoding="utf-8").write(life_html)
        print(f"✅ 已同步更新本機原型資料夾：{proto_index}")


if __name__ == "__main__":
    main()
