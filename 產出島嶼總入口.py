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

# 10 大領域島設定（每座島具備專屬地標、獨立地貌造型、專屬三階段聚落名稱與世界觀精神）
DOMAIN_CONFIG = [
    {
        "id": "selfcare",
        "name": "特需生活管理",
        "islandName": "特需生活管理島",
        "islandShape": "crescent_bay",
        "islandTitle": "自立生活港灣",
        "islandStory": "自立生活港灣。在潔牙燈塔與晨光衣帽風車下，學會穿鞋襪、自己刷牙洗臉、打掃環境，把每一天過得神氣又乾淨！",
        "icon": "🏠",
        "color": "#1565c0",
        "trimColor": "#42a5f5",
        "groundColor": "#e3f2fd",
        "themeDesc": "衣食住行、穿脫洗漱、清潔打掃與自我保護",
        "landmarkType": "lighthouse_whale",
        "sourceDomains": ["特需生活管理"],
        "shareStage1Daily": False,
        "stageTitles": {
            "1": "🌱 第一階段：自理啟蒙村（飲食・穿衣・如廁）",
            "2": "🌿 第二階段：整潔實踐鎮（鞋襪・護牙・回收）",
            "3": "🌳 第三階段：獨立生活城（防災・交通・健康）"
        },
        "stagePalettes": {
            "1": {"top": "#e3f2fd", "trim": "#29b6f6", "roofA": "#ef5350", "roofB": "#26a69a"},
            "2": {"top": "#e0f7fa", "trim": "#00acc1", "roofA": "#1e88e5", "roofB": "#ffa726"},
            "3": {"top": "#e8eaf6", "trim": "#3949ab", "roofA": "#5c6bc0", "roofB": "#ec407a"}
        }
    },
    {
        "id": "motor",
        "name": "特需功能性動作訓練",
        "islandName": "特需動作訓練島",
        "islandShape": "stepped_terrace",
        "islandTitle": "躍動階梯之巔",
        "islandStory": "躍動階梯之巔。踩上彩虹平衡木、走過階梯跳石，小手抓握有力、雙腳踩得穩健，每一步都充滿自立力量！",
        "icon": "🤸",
        "color": "#4f5bd5",
        "trimColor": "#7986cb",
        "groundColor": "#e8eaf6",
        "themeDesc": "上肢精細操作、下肢平衡移動、姿勢控制與雙手協調",
        "landmarkType": "gym_rainbow",
        "sourceDomains": ["特需功能性動作訓練"],
        "shareStage1Daily": False,
        "stageTitles": {
            "1": "🌱 第一階段：感統啟蒙村（小手抓握・雙腳站走）",
            "2": "🌿 第二階段：協調實踐鎮（手指合作・動作變身）",
            "3": "🌳 第三階段：靈巧動作城（上下肢綜合・生活獨立）"
        },
        "stagePalettes": {
            "1": {"top": "#ede7f6", "trim": "#7e57c2", "roofA": "#ab47bc", "roofB": "#42a5f5"},
            "2": {"top": "#e8eaf6", "trim": "#5c6bc0", "roofA": "#5c6bc0", "roofB": "#ff7043"},
            "3": {"top": "#f3e5f5", "trim": "#8e24aa", "roofA": "#7b1fa2", "roofB": "#26c6da"}
        }
    },
    {
        "id": "chinese",
        "name": "語文",
        "islandName": "語文繪本島",
        "islandShape": "open_book",
        "islandTitle": "故事書卷之森",
        "islandStory": "故事書卷之森。翻開海面上浮現的巨型繪本書卷，在魔法羽毛筆鐘樓下聽故事、讀句子，勇敢說出心裡話！",
        "icon": "📖",
        "color": "#0284c7",
        "trimColor": "#38bdf8",
        "groundColor": "#f0f9ff",
        "themeDesc": "語文識字、繪本閱讀、溝通表達與生活應用",
        "landmarkType": "book_tower",
        "sourceDomains": ["語文"],
        "shareStage1Daily": False,
        "stageTitles": {
            "1": "🌱 第一階段：語文啟蒙村（認識名字・日常指物）",
            "2": "🌿 第二階段：生活閱讀鎮（童話寓言・生活對話）",
            "3": "🌳 第三階段：閱讀素養城（客閩多元・社會閱讀）"
        },
        "stagePalettes": {
            "1": {"top": "#f0f9ff", "trim": "#38bdf8", "roofA": "#0284c7", "roofB": "#f59e0b"},
            "2": {"top": "#e0f2fe", "trim": "#0ea5e9", "roofA": "#0369a1", "roofB": "#10b981"},
            "3": {"top": "#ede9fe", "trim": "#8b5cf6", "roofA": "#6d28d9", "roofB": "#f43f5e"}
        }
    },
    {
        "id": "math",
        "name": "數學",
        "islandName": "生活數學島",
        "islandShape": "crystal_square",
        "islandTitle": "幾何時空花園",
        "islandStory": "幾何時空花園。在幾何時鐘高塔與天秤金幣前，數數量、比大小、看時間、學購物，生活有條理又有秩序！",
        "icon": "📐",
        "color": "#ea580c",
        "trimColor": "#fb923c",
        "groundColor": "#fff7ed",
        "themeDesc": "數與量、幾何形狀、生活計量、時鐘與金錢購物",
        "landmarkType": "clock_pyramid",
        "sourceDomains": ["數學"],
        "shareStage1Daily": False,
        "stageTitles": {
            "1": "🌱 第一階段：數感啟蒙村（數數比大小・基本形狀）",
            "2": "🌿 第二階段：生活計量鎮（錢幣購物・時鐘看時間）",
            "3": "🌳 第三階段：實用數學城（加減運算・複合測量）"
        },
        "stagePalettes": {
            "1": {"top": "#fff7ed", "trim": "#fb923c", "roofA": "#ea580c", "roofB": "#0284c7"},
            "2": {"top": "#fef3c7", "trim": "#f59e0b", "roofA": "#d97706", "roofB": "#8b5cf6"},
            "3": {"top": "#ffedd5", "trim": "#f97316", "roofA": "#c2410c", "roofB": "#10b981"}
        }
    },
    {
        "id": "pe",
        "name": "健體",
        "islandName": "健體活力島",
        "islandShape": "stadium_oval",
        "islandTitle": "聖火守護之島",
        "islandStory": "聖火守護之島。沿著運動場跑道奔跑，聖火高塔指引方向，認識身體、看懂紅綠燈過馬路，健康又有活力！",
        "icon": "🏃",
        "color": "#d32f2f",
        "trimColor": "#ef5350",
        "groundColor": "#ffebee",
        "themeDesc": "健康體適能、球類運動遊戲、安全防護與衛生保健",
        "landmarkType": "stadium_torch",
        "sourceDomains": ["健體", "健康與體育"],
        "shareStage1Daily": False,
        "stageTitles": {
            "1": "🌱 第一階段：活力啟蒙村（認識身體・基本滾跑）",
            "2": "🌿 第二階段：運動實踐鎮（拍球接球・體能挑戰）",
            "3": "🌳 第三階段：健康防護城（急救自護・團隊遊戲）"
        },
        "stagePalettes": {
            "1": {"top": "#ffebee", "trim": "#e57373", "roofA": "#d32f2f", "roofB": "#ffb300"},
            "2": {"top": "#fbe9e7", "trim": "#ff8a65", "roofA": "#d84315", "roofB": "#1e88e5"},
            "3": {"top": "#ede7f6", "trim": "#9575cd", "roofA": "#512da8", "roofB": "#43a047"}
        }
    },
    {
        "id": "nature",
        "name": "自然",
        "islandName": "自然探險島",
        "islandShape": "nature_spiral",
        "islandTitle": "四季觀星之島",
        "islandStory": "四季觀星之島。轉動生態大風車、探訪綠意溫室花房，看四季天氣、摸摸花草小動物，大自然是神奇的好朋友！",
        "icon": "🌱",
        "color": "#2e7d32",
        "trimColor": "#81c784",
        "groundColor": "#e8f5e9",
        "themeDesc": "動植物生態、天氣變化、奇妙磁力與科學探索",
        "landmarkType": "windmill_greenhouse",
        "sourceDomains": ["自然"],
        "shareStage1Daily": True,
        "stageTitles": {
            "1": "🌱 第一階段：自然啟蒙村（大樹花香・水的遊戲）",
            "2": "🌿 第二階段：生態實踐鎮（植物動物・磁鐵水資源）",
            "3": "🌳 第三階段：科學探索城（水溶液熱學・燃燒消防）"
        },
        "stagePalettes": {
            "1": {"top": "#e8f5e9", "trim": "#66bb6a", "roofA": "#43a047", "roofB": "#fdd835"},
            "2": {"top": "#f1f8e9", "trim": "#7cb342", "roofA": "#2e7d32", "roofB": "#29b6f6"},
            "3": {"top": "#e0f2f1", "trim": "#26a69a", "roofA": "#00695c", "roofB": "#ef5350"}
        }
    },
    {
        "id": "society",
        "name": "社會",
        "islandName": "社會生活島",
        "islandShape": "town_blocks",
        "islandTitle": "社區同心市鎮",
        "islandStory": "社區同心市鎮。繞過世界地球儀噴泉、搭乘溫馨小公車，認識鄰舍、遵守班規與交通禮貌，大家同心快樂生活！",
        "icon": "🏮",
        "color": "#c0562e",
        "trimColor": "#e57373",
        "groundColor": "#ffebee",
        "themeDesc": "家庭學校、社區資源、交通旅遊與多元文化",
        "landmarkType": "gate_town",
        "sourceDomains": ["社會"],
        "shareStage1Daily": True,
        "stageTitles": {
            "1": "🌱 第一階段：家園啟蒙村（新學校・親愛家人）",
            "2": "🌿 第二階段：社區實踐鎮（班規禮貌・輪流合作）",
            "3": "🌳 第三階段：文化交通城（火車機場・節慶職業）"
        },
        "stagePalettes": {
            "1": {"top": "#ffebee", "trim": "#ef5350", "roofA": "#d32f2f", "roofB": "#ffa000"},
            "2": {"top": "#fbe9e7", "trim": "#ff8a65", "roofA": "#c62828", "roofB": "#5c6bc0"},
            "3": {"top": "#fff8e1", "trim": "#ffca28", "roofA": "#b71c1c", "roofB": "#00897b"}
        }
    },
    {
        "id": "life",
        "name": "綜合",
        "islandName": "綜合活動島",
        "islandShape": "treasure_isles",
        "islandTitle": "巧手百寶工坊",
        "islandStory": "巧手百寶工坊。圍在童軍營火帳篷旁，一起玩桌遊、輪流排隊、動手串珠與垃圾分類，學習當生活小創客！",
        "icon": "🌏",
        "color": "#00838f",
        "trimColor": "#4dd0e1",
        "groundColor": "#e0f7fa",
        "themeDesc": "桌遊輪流、人際互動、生活美感與環境保護",
        "landmarkType": "ferris_camp",
        "sourceDomains": ["綜合"],
        "shareStage1Daily": True,
        "stageTitles": {
            "1": "🌱 第一階段：共遊啟蒙村（玩具聲音・快樂一夏）",
            "2": "🌿 第二階段：互動實踐鎮（串珠桌遊・輪流表達）",
            "3": "🌳 第三階段：多元永續城（客閩原民・海洋防疫）"
        },
        "stagePalettes": {
            "1": {"top": "#e0f7fa", "trim": "#26c6da", "roofA": "#0097a7", "roofB": "#ec407a"},
            "2": {"top": "#e0f2f1", "trim": "#26a69a", "roofA": "#00838f", "roofB": "#ab47bc"},
            "3": {"top": "#e8f5e9", "trim": "#4caf50", "roofA": "#00695c", "roofB": "#ffa726"}
        }
    },
    {
        "id": "arts",
        "name": "藝術與人文",
        "islandName": "藝術創想島",
        "islandShape": "artist_palette",
        "islandTitle": "彩虹調色海礁",
        "islandStory": "彩虹調色海礁。巨型木畫架立在調色盤天池邊，踏上琴鍵階梯步道，用繽紛色彩與旋律唱出快樂心情！",
        "icon": "🎨",
        "color": "#8e24aa",
        "trimColor": "#ba68c8",
        "groundColor": "#f3e5f5",
        "themeDesc": "色彩造型、音樂律動、視覺美感與創意手作",
        "landmarkType": "palette_pavilion",
        "sourceDomains": ["藝術", "藝文"],
        "shareStage1Daily": True,
        "stageTitles": {
            "1": "🌱 第一階段：感官啟蒙村（聲音世界・色彩探索）",
            "2": "🌿 第二階段：創意實踐鎮（鈴鼓沙鈴・彩筆剪貼）",
            "3": "🌳 第三階段：展演藝術城（醒獅手搖鈴・再生藝術）"
        },
        "stagePalettes": {
            "1": {"top": "#fce4ec", "trim": "#f06292", "roofA": "#ec407a", "roofB": "#ab47bc"},
            "2": {"top": "#f3e5f5", "trim": "#ba68c8", "roofA": "#8e24aa", "roofB": "#29b6f6"},
            "3": {"top": "#ede7f6", "trim": "#9575cd", "roofA": "#6a1b9a", "roofB": "#ffb300"}
        }
    },
    {
        "id": "daily",
        "name": "生活課程",
        "islandName": "生活課程啟蒙島",
        "islandShape": "sprout_petal",
        "islandTitle": "萌芽探險新星",
        "islandStory": "萌芽探險新星。揹起立體彩色小書包、溜下向日葵滑梯，不怕生、常微笑，國小新生活充滿奇妙與樂趣！",
        "icon": "🎒",
        "color": "#d81b60",
        "trimColor": "#f06292",
        "groundColor": "#fce4ec",
        "themeDesc": "第一學習階段跨領域統整：校園探索、四季自然與生活體驗",
        "landmarkType": "schoolbag_park",
        "sourceDomains": ["生活"],
        "shareStage1Daily": False,
        "stageTitles": {
            "1": "🌱 第一階段：生活體驗村（新學校・玩具・家人・水遊戲）",
            "2": "🌿 第二階段銜接：自然與社會探索",
            "3": "🌳 第三階段銜接：綜合與藝文創想"
        },
        "stagePalettes": {
            "1": {"top": "#fce4ec", "trim": "#f06292", "roofA": "#d81b60", "roofB": "#ffb300"},
            "2": {"top": "#fff8e1", "trim": "#ffd54f", "roofA": "#f57c00", "roofB": "#43a047"},
            "3": {"top": "#e1f5fe", "trim": "#4fc3f7", "roofA": "#0288d1", "roofB": "#ab47bc"}
        }
    }
]


def classify_unit_attributes(name: str, orig_domain: str):
    """根據單元名稱與領域，自動賦予專屬 3D 模型類別 (propType)、代表圖示 (topicEmoji) 與屬性標籤 (attrTag)。"""
    n = name

    # 1. 潔牙洗漱與身體清潔
    if any(k in n for k in ["護牙", "洗洗", "清潔基本功"]):
        return "tooth_clean", "🦷", "潔牙洗漱"
    if any(k in n for k in ["廁所", "如廁"]):
        return "tooth_clean", "🚽", "如廁自理"

    # 2. 衣物鞋襪穿脫與儀容
    if any(k in n for k in ["衣", "鞋", "襪", "服裝", "穿脫"]):
        return "clothes_shoe", "👕", "穿脫儀容"

    # 3. 掃地、垃圾分類與資源回收
    if any(k in n for k in ["掃地", "垃圾", "回收", "整潔"]):
        return "recycle_bin", "♻️", "打掃回收"

    # 4. 交通工具、車站機場港口與號誌
    if any(k in n for k in ["交通", "號誌", "火車", "機場", "港口", "馬車", "運輸"]):
        return "traffic_car", "🚦", "交通運輸"

    # 5. 飲食、用餐与食品營養
    if any(k in n for k in ["食物", "用餐", "飲食", "食品"]):
        return "food_health", "🍱", "健康飲食"

    # 6. 樂器演奏、唱歌跳舞與音樂
    if any(k in n for k in ["鈴鼓", "沙鈴", "手搖鈴", "醒獅鼓", "唱唱跳跳", "音樂", "交響樂", "聲音"]):
        return "music_drum", "🥁", "音樂律動"

    # 7. 繪畫、剪貼、拼貼與視覺美感
    if any(k in n for k in ["彩色筆", "蠟筆", "顏料", "撕貼", "剪貼", "拼貼", "再生藝術", "美感", "故宮"]):
        return "art_palette", "🎨", "視覺創作"

    # 8. 串珠、桌遊與玩具遊戲
    if any(k in n for k in ["串珠", "桌遊", "玩具", "尋寶", "遊戲規則"]):
        return "game_bead_fest", "🎲", "桌遊串珠"

    # 9. 節慶、文化與民俗
    if any(k in n for k in ["新年", "除夕", "月圓", "聖誕", "端午", "龍舟", "生日", "客閩", "原住民", "福爾摩沙", "臺灣"]):
        return "game_bead_fest", "🏮", "節慶文化"

    # 10. 磁鐵、燃燒、消防、水與科學實驗
    if any(k in n for k in ["磁鐵", "燃燒", "消防", "水溶液", "溶解", "熱對物質", "水魔法", "水資源", "水的遊戲"]):
        return "science_lab", "🧲", "科學實驗"

    # 11. 植物、花卉、森林與四季天氣
    if any(k in n for k in ["植物", "花", "大樹", "森林", "天氣", "一夏", "海洋"]):
        return "nature_plant", "🌻", "生態自然"

    # 12. 動物與昆蟲
    if any(k in n for k in ["動物", "蝶", "蚊蟲"]):
        return "animal_zoo", "🐾", "動物探索"

    # 13. 幾何形狀、立體形體與空間
    if any(k in n for k in ["形狀", "圖形", "扇形", "長方體", "柱體", "錐體", "球體", "立體形體", "角", "邊長"]):
        return "math_shape", "📐", "幾何形體"

    # 14. 數字、時間、重量、容量與計算機
    if any(k in n for k in ["的數", "綜合練習", "位數", "時間", "重量", "容量", "測量", "計算機", "長短", "多少", "順序", "分類", "列表"]):
        return "math_clock_num", "⏰", "數與量測"

    # 15. 上肢、小手、手指與抓握
    if any(k in n for k in ["上肢", "你的手", "小手", "手指", "抓握", "巧手", "手部", "手腳並用"]):
        return "hand_grip", "✋", "上肢精細"

    # 16. 下肢、雙腳、走路、平衡與姿勢
    if any(k in n for k in ["下肢", "你的腳", "雙腳", "走路", "向前走", "平衡", "姿勢", "站立架", "動作變身", "移動技巧", "協調", "生活獨立"]):
        return "foot_balance", "🦶", "平衡移動"

    # 17. 球類、賽跑、持拍與運動體能
    if any(k in n for k in ["玩球", "足下", "持拍", "賽跑", "走走跑跑", "跳一跳", "軸心運動", "運動"]):
        return "sport_ball", "⚽", "球類體能"

    # 18. 安全防護、危機警報與防疫衛教
    if any(k in n for k in ["安全", "危險", "危機", "警報", "病魔", "防疫", "疾病", "健康情報", "自我保護", "拒絕", "勇敢說不", "青春期", "男生女生", "身體"]):
        return "safety_med", "🛡️", "安全衛教"

    # 19. 語文故事、人際家庭與校園探索
    if orig_domain == "語文" or any(k in n for k in ["故事", "閱讀", "作家", "語文", "想像", "傳話"]):
        return "book_story", "📖", "繪本閱讀"

    return "book_story", "🏫", "校園人際"



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
                prop_type, topic_emoji, attr_tag = classify_unit_attributes(u["名"], orig_domain)
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
                    "manual": manual,
                    "propType": prop_type,
                    "topicEmoji": topic_emoji,
                    "attrTag": attr_tag
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

        # 統計該領域所有單元的屬性標籤與代表單元（供群島總覽與領域島屬性切換使用）
        all_domain_units = s1 + s2 + s3
        attr_counts = {}
        for u in all_domain_units:
            tag = u["attrTag"]
            if tag not in attr_counts:
                attr_counts[tag] = {"tag": tag, "emoji": u["topicEmoji"], "count": 0}
            attr_counts[tag]["count"] += 1
        attr_summary = sorted(attr_counts.values(), key=lambda x: -x["count"])

        # 挑選 3 個最具代表性的不同屬性單元，顯示在群島大世界的領域島周圍小屋上
        featured_units = []
        seen_tags = set()
        for u in own_units:
            if u["attrTag"] not in seen_tags:
                featured_units.append(u)
                seen_tags.add(u["attrTag"])
            if len(featured_units) >= 3:
                break
        while len(featured_units) < 3 and len(own_units) > len(featured_units):
            featured_units.append(own_units[len(featured_units) * 2 % len(own_units)])

        domains_data.append({
            "id": cfg["id"],
            "name": cfg["name"],
            "islandName": cfg["islandName"],
            "islandShape": cfg.get("islandShape", "hex"),
            "islandTitle": cfg.get("islandTitle", cfg["islandName"]),
            "islandStory": cfg.get("islandStory", cfg["themeDesc"]),
            "icon": cfg["icon"],
            "color": cfg["color"],
            "trimColor": cfg["trimColor"],
            "groundColor": cfg["groundColor"],
            "themeDesc": cfg["themeDesc"],
            "landmarkType": cfg["landmarkType"],
            "ownCount": own_count,
            "stage1Note": stage1_note,
            "stageTitles": cfg["stageTitles"],
            "stagePalettes": cfg["stagePalettes"],
            "attrSummary": attr_summary,
            "featuredUnits": featured_units,
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

/* 繪本手作水彩紙紋質感覆蓋層 (Tactile Watercolor Paper Grain Overlay) */
#stage-3d::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 6;
  opacity: 0.16;
  mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='paperGrain'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23paperGrain)' opacity='0.5'/%3E%3C/svg%3E");
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
.pin-attr-tag {
  font-size: 11px;
  font-weight: 800;
  color: #0369a1;
  background: #e0f2fe;
  padding: 1px 7px;
  border-radius: 8px;
}
.pin-badge {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  background: #f1f5f9;
  padding: 1px 6px;
  border-radius: 8px;
}

.pill-world-sub {
  padding: 4px 10px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.93);
  border: 1.5px solid #cbd5e1;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
  gap: 5px;
}
.pill-world-sub .pin-title {
  font-size: 12px;
  font-weight: 800;
}
.pill-world-sub::after {
  border-width: 5px 5px 0 5px;
  bottom: -5px;
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
  max-width: 470px;
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
.banner-attr-bar {
  margin-top: 9px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.attr-chip {
  border: 1.5px solid #cbd5e1;
  background: #f8fafc;
  color: #334155;
  font-family: inherit;
  font-size: 12px;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.16s;
}
.attr-chip:hover {
  border-color: #0284c7;
  background: #e0f2fe;
}
.attr-chip.active {
  background: #0284c7;
  color: #fff;
  border-color: #0284c7;
  box-shadow: 0 3px 8px rgba(2, 132, 199, 0.25);
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

/* ── 希望學園與校訓專屬樣式 ── */
.pill-hope-school {
  background: linear-gradient(135deg, rgba(225, 29, 72, 0.95), rgba(245, 158, 11, 0.95)) !important;
  border: 2px solid rgba(255, 255, 255, 0.85) !important;
  box-shadow: 0 8px 24px rgba(225, 29, 72, 0.45) !important;
  color: #ffffff !important;
  font-weight: 700 !important;
}
.pill-hope-school .pin-title {
  color: #ffffff !important;
  font-size: 14px !important;
  font-weight: 900 !important;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
.pill-hope-school .pin-badge {
  background: rgba(255, 255, 255, 0.28) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.4) !important;
  font-weight: 700 !important;
}

.icon-pill-btn.hope-btn {
  background: linear-gradient(135deg, #fff1f2, #fef3c7);
  border-color: #f59e0b;
  color: #b45309;
  font-weight: 700;
}
.icon-pill-btn.hope-btn:hover {
  background: linear-gradient(135deg, #ffe4e6, #fde68a);
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(245, 158, 11, 0.28);
}

.icon-pill-btn.tour-btn {
  background: linear-gradient(135deg, #f0fdf4, #e0f2fe);
  border-color: #0284c7;
  color: #0369a1;
  font-weight: 700;
}
.icon-pill-btn.tour-btn:hover {
  background: linear-gradient(135deg, #dcfce7, #bae6fd);
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.28);
}

/* 希望學園專屬彈窗 */
.hope-card {
  max-width: 680px !important;
  background: #ffffff !important;
  border-radius: 24px !important;
  border: 2px solid #f59e0b !important;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.35) !important;
  padding: 28px !important;
}
.hope-card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 2px dashed #f1f5f9;
  padding-bottom: 16px;
  margin-bottom: 16px;
}
.hope-card-icon {
  font-size: 42px;
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: linear-gradient(135deg, #fef3c7, #ffe4e6);
  border: 2px solid #fbbf24;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.hope-card-title {
  font-size: 24px;
  font-weight: 900;
  color: #1e293b;
  line-height: 1.25;
}
.hope-motto-tag {
  display: inline-block;
  margin-top: 6px;
  background: linear-gradient(135deg, #e11d48, #f59e0b);
  color: #ffffff;
  font-weight: 800;
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 999px;
  box-shadow: 0 2px 8px rgba(225, 29, 72, 0.3);
}
.hope-card-intro {
  font-size: 15px;
  line-height: 1.7;
  color: #334155;
  background: #fdfbf7;
  border: 1.5px solid #fde68a;
  border-radius: 14px;
  padding: 14px 18px;
  margin-bottom: 18px;
}
.hope-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 22px;
}
.hope-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 13.5px;
  line-height: 1.55;
  color: #475569;
  background: #f8fafc;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
}
.hope-item-icon {
  font-size: 18px;
  flex-shrink: 0;
  margin-top: 1px;
}
.hope-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  border-top: 1px solid #f1f5f9;
  padding-top: 18px;
}
.hope-btn-tour {
  flex: 1.2;
  min-width: 180px;
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: #ffffff;
  border: none;
  font-size: 14.5px;
  font-weight: 800;
  padding: 12px 18px;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);
  transition: all 0.2s;
}
.hope-btn-tour:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45);
}
.hope-btn-classic {
  text-decoration: none;
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
  font-size: 13.5px;
  font-weight: 700;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.hope-btn-classic:hover { background: #e2e8f0; color: #1e293b; }
.hope-btn-start {
  background: linear-gradient(135deg, #e11d48, #f59e0b);
  color: #ffffff;
  border: none;
  font-size: 14.5px;
  font-weight: 800;
  padding: 12px 20px;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(225, 29, 72, 0.35);
}
.hope-btn-start:hover { transform: translateY(-2px); }

/* 白鯨巡航浮動故事列 */
.tour-bar {
  position: fixed;
  left: 50%;
  bottom: 24px;
  transform: translateX(-50%) translateY(120%);
  width: min(720px, calc(100vw - 32px));
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(14px);
  border: 2px solid #38bdf8;
  border-radius: 20px;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.28);
  padding: 16px 22px;
  z-index: 210;
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.35s;
  opacity: 0;
  pointer-events: none;
}
.tour-bar.visible {
  transform: translateX(-50%) translateY(0);
  opacity: 1;
  pointer-events: auto;
}
.tour-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}
.tour-badge {
  background: #e0f2fe;
  color: #0369a1;
  font-size: 12px;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid #7dd3fc;
}
.tour-title {
  font-size: 17px;
  font-weight: 900;
  color: #0f172a;
  flex: 1;
}
.tour-close {
  background: transparent;
  border: none;
  font-size: 22px;
  color: #64748b;
  cursor: pointer;
  padding: 0 4px;
}
.tour-desc {
  font-size: 14.5px;
  line-height: 1.6;
  color: #334155;
  margin-bottom: 14px;
  background: #f8fafc;
  padding: 10px 14px;
  border-radius: 12px;
  border-left: 4px solid #0284c7;
}
.tour-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.tour-btn-nav {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
  font-size: 13.5px;
  font-weight: 700;
  padding: 8px 16px;
  border-radius: 10px;
  cursor: pointer;
}
.tour-btn-nav:hover { background: #e2e8f0; }
.tour-btn-go {
  background: linear-gradient(135deg, #0284c7, #2563eb);
  color: #ffffff;
  border: none;
  font-size: 14px;
  font-weight: 800;
  padding: 8px 20px;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
}
.tour-btn-go:hover { transform: translateY(-1.5px); }

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
      <h1 id="top-title">🏫 希望學園・3D 特教群島總入口</h1>
      <p id="top-subtitle">校訓：快樂活潑，自立自強 ｜ 10 大領域島嶼 × 240 個互動單元</p>
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

    <button class="icon-pill-btn hope-btn" onclick="openHopeSchoolModal()" title="查看希望學園校訓與全島導覽"><span style="font-size:16px;">🏫</span><span>希望學園</span></button>
    <button class="icon-pill-btn tour-btn" id="btn-whale-tour" onclick="startWhaleGuidedTour()" title="跟著白鯨巡航導覽"><span style="font-size:16px;">🐋</span><span>白鯨導覽</span></button>
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

  <!-- 左上角當前島嶼資訊卡（含領域專屬屬性快速切換列） -->
  <div class="island-info-banner" id="island-banner">
    <div class="banner-title" id="banner-title">🌊 特教學習大世界（10 大領域群島）</div>
    <div class="banner-desc" id="banner-desc">點擊任一領域島嶼，即可進入該領域的「第一、二、三學習階段」立體教材村落！</div>
    <div class="banner-note" id="banner-note"></div>
    <div class="banner-attr-bar" id="banner-attrs"></div>
  </div>

  <!-- 右下角鏡頭控制 -->
  <div class="cam-controls">
    <button class="cam-btn" id="btn-all-pins" onclick="toggleShowAllPins()" title="切換顯示全部單元標籤／精選標籤">🏷️</button>
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
          <span class="m-badge" id="m-attr-badge" style="background:#e0f2fe;color:#0369a1;">👕 穿脫儀容</span>
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

<!-- 白鯨巡航浮動故事列 -->
<div class="tour-bar" id="tour-bar">
  <div class="tour-header">
    <div class="tour-badge" id="tour-step-tag">站點 1 / 11</div>
    <div class="tour-title" id="tour-title">🏫 第一站：希望學園（群島核心）</div>
    <button class="tour-close" onclick="stopWhaleTour()" title="關閉巡航導覽">&times;</button>
  </div>
  <div class="tour-desc" id="tour-desc">「這裡是大家學習成長的基地營。校訓是『快樂活潑，自立自強』。跟著白鯨領航員，準備出發上課囉！」</div>
  <div class="tour-footer">
    <button class="tour-btn-nav" onclick="prevTourStep()">⬅ 上一站</button>
    <button class="tour-btn-go" id="tour-btn-go" onclick="visitCurrentTourIsland()">🚀 進入該島上課</button>
    <button class="tour-btn-nav" onclick="nextTourStep()">下一站 ➔</button>
  </div>
</div>

<!-- 希望學園校訓與導覽視窗 -->
<div class="modal-backdrop" id="modal-hope-school" onclick="if(event.target===this)closeHopeSchoolModal()">
  <div class="hope-card" onclick="event.stopPropagation()">
    <button class="modal-close-btn" onclick="closeHopeSchoolModal()">&times;</button>
    <div class="hope-card-header">
      <div class="hope-card-icon">🏫</div>
      <div>
        <h2 class="hope-card-title">希望學園（Hope Academy）</h2>
        <div class="hope-motto-tag">校訓：快樂活潑，自立自強</div>
      </div>
    </div>
    <div class="hope-card-intro">
      「大家在希望學園上課，一起學習、一起快樂成長。<br>
      穿過 10 條跨海木橋，每座主題島都有一套精心設計的生活自立技能。<br>
      帶著<strong>快樂活潑</strong>的心情出發，帶著<strong>自立自強</strong>的本領回來！」
    </div>
    <div class="hope-grid">
      <div class="hope-item">
        <span class="hope-item-icon">🔔</span>
        <div class="hope-item-text"><strong>希望之鐘・主校舍</strong>：每天早晨敲響希望鐘聲，引領孩子開啟自立生活的充實學習。</div>
      </div>
      <div class="hope-item">
        <span class="hope-item-icon">🪨</span>
        <div class="hope-item-text"><strong>校訓石碑</strong>：刻寫「快樂活潑，自立自強」，是陪伴孩子一生前行、不怕挫折的座右銘。</div>
      </div>
      <div class="hope-item">
        <span class="hope-item-icon">🚩</span>
        <div class="hope-item-text"><strong>晨光操場與彩虹旗台</strong>：升起藍天白鯨校旗，大家一起做伸展操、充滿朝氣。</div>
      </div>
      <div class="hope-item">
        <span class="hope-item-icon">🐋</span>
        <div class="hope-item-text"><strong>白鯨啟航碼頭</strong>：10 條跨海木橋通往 10 大主題島，白鯨領航員噴出彩虹水花為孩子加油守護。</div>
      </div>
      <div class="hope-item">
        <span class="hope-item-icon">🌟</span>
        <div class="hope-item-text"><strong>240 站自立學習寶庫</strong>：涵蓋食衣住行、動作訓練、認知溝通與社會適應三大階段完整教材。</div>
      </div>
    </div>
    <div class="hope-actions">
      <button class="hope-btn-tour" onclick="startWhaleGuidedTour(0); closeHopeSchoolModal();">🐋 跟著白鯨巡航導覽</button>
      <a class="hope-btn-classic" href="index_classic.html">🗂️ 舊版學期制總入口</a>
      <button class="hope-btn-start" onclick="closeHopeSchoolModal()">踏上木橋出發上課 ➔</button>
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
      emissive: new THREE.Color(emissive)
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
// 經典立體六角地塊（供領域三階段村落島使用）
function createHexPlatform(radius, height, topHex, trimHex, dirtHex, x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);

  const cliff = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.98, radius * 0.82, height, 6), mat(dirtHex));
  cliff.position.y = height / 2 - 0.25;
  cliff.castShadow = true; cliff.receiveShadow = true;
  g.add(cliff);

  const rim = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.03, radius * 1.01, 0.34, 6), mat(trimHex));
  rim.position.y = height - 0.32;
  rim.castShadow = true; rim.receiveShadow = true;
  g.add(rim);

  const top = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.96, radius * 0.96, 0.26, 6), mat(topHex));
  top.position.y = height - 0.18;
  top.receiveShadow = true;
  g.add(top);

  return { group: g, topY: height - 0.05 };
}

// ================= 繪本手作風立體微縮造景元素（純真小雛菊、石板碎屑、研討木書桌、師生人偶） =================
function createDaisy(scale = 1.0, petalColor = "#ffffff") {
  const g = new THREE.Group();
  // 細嫩花莖
  g.add(cyl(0.015 * scale, 0.015 * scale, 0.28 * scale, "#4ade80", 0, 0, 0, 4));
  // 純白／柔彩花瓣十字
  const p1 = box(0.18 * scale, 0.02, 0.05 * scale, petalColor, 0, 0.28 * scale, 0);
  const p2 = box(0.05 * scale, 0.02, 0.18 * scale, petalColor, 0, 0.28 * scale, 0);
  const p3 = box(0.14 * scale, 0.02, 0.04 * scale, petalColor, 0, 0.28 * scale, 0);
  p3.rotation.y = Math.PI / 4;
  const p4 = box(0.04 * scale, 0.02, 0.14 * scale, petalColor, 0, 0.28 * scale, 0);
  p4.rotation.y = Math.PI / 4;
  g.add(p1, p2, p3, p4);
  // 金黃花蕊
  g.add(ball(0.042 * scale, "#facc15", 0, 0.3 * scale, 0, 6));
  return g;
}

function createDaisyCluster(x, y, z, count = 3, spread = 0.35) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  const colors = ["#ffffff", "#ffffff", "#fef08a", "#fed7aa", "#fce7f3"];
  for (let i = 0; i < count; i++) {
    const ang = (i / count) * Math.PI * 2 + (i * 0.37);
    const r = (0.2 + (i % 3) * 0.3) * spread;
    const dx = Math.cos(ang) * r;
    const dz = Math.sin(ang) * r;
    const d = createDaisy(0.85 + (i % 2) * 0.25, colors[i % colors.length]);
    d.position.set(dx, 0, dz);
    d.rotation.y = (i * 1.1) % Math.PI;
    g.add(d);
  }
  return g;
}

function createPebbleScatter(x, y, z, count = 6, spread = 0.55) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  const pebbleColors = ["#e2e8f0", "#cbd5e1", "#f8fafc", "#f1f5f9", "#e0e7ff", "#fef3c7"];
  for (let i = 0; i < count; i++) {
    const ang = (i / count) * Math.PI * 2 + (i * 0.45);
    const r = (0.15 + ((i * 7) % 10) / 10.0 * 0.85) * spread;
    const px = Math.cos(ang) * r;
    const pz = Math.sin(ang) * r;
    const psize = 0.08 + (i % 3) * 0.04;
    const segs = 5 + (i % 2);
    const col = pebbleColors[i % pebbleColors.length];
    const pebble = cyl(psize, psize * 1.1, 0.025, col, px, 0.01, pz, segs);
    pebble.rotation.y = i * 0.8;
    g.add(pebble);
  }
  return g;
}

// 戶外研討木書桌（暖木長桌、彩色典籍疊、發光筆電、溫熱咖啡杯、鵝頸檯燈、小圓椅）
function createOutdoorStudyCorner(x, y, z, rotY = 0) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  g.rotation.y = rotY;

  // 1. 暖木桌體
  const top = box(1.25, 0.08, 0.76, "#d97706", 0, 0.72, 0); // 暖琥珀木桌面
  const apron = box(1.15, 0.06, 0.68, "#b45309", 0, 0.66, 0); // 桌裙
  g.add(top, apron);
  [-0.52, 0.52].forEach(lx => {
    [-0.28, 0.28].forEach(lz => {
      g.add(cyl(0.04, 0.04, 0.72, "#b45309", lx, 0, lz, 6)); // 桌腳
    });
  });

  // 木椅（桌後靠背椅）
  g.add(box(0.48, 0.06, 0.42, "#d97706", 0, 0.45, -0.52));
  [-0.2, 0.2].forEach(sx => {
    [-0.68, -0.36].forEach(sz => {
      g.add(cyl(0.03, 0.03, 0.45, "#b45309", sx, 0, sz, 6));
    });
  });
  g.add(box(0.48, 0.28, 0.04, "#b45309", 0, 0.62, -0.7));

  // 2. 左側彩色典籍疊（紅、綠、藍、黃四冊書，白紙內頁清晰可見）
  g.add(box(0.36, 0.07, 0.26, "#dc2626", -0.38, 0.76, 0.06)); // 紅皮大書
  g.add(box(0.34, 0.05, 0.24, "#f8fafc", -0.38, 0.76, 0.06)); // 內頁
  const book2 = box(0.34, 0.065, 0.25, "#16a34a", -0.37, 0.83, 0.07); // 翠綠書
  book2.rotation.y = 0.08;
  g.add(book2);
  const book3 = box(0.32, 0.06, 0.24, "#2563eb", -0.39, 0.895, 0.05); // 寶藍書
  book3.rotation.y = -0.06;
  g.add(book3);
  g.add(box(0.3, 0.05, 0.22, "#f59e0b", -0.38, 0.955, 0.06)); // 暖金手冊

  // 3. 中央發光筆電（深灰機身、微傾螢幕、亮藍發光自體發光螢幕）
  g.add(box(0.44, 0.025, 0.32, "#334155", 0.06, 0.76, 0.08)); // 底座鍵盤
  g.add(box(0.38, 0.005, 0.18, "#1e293b", 0.06, 0.78, 0.12));
  g.add(box(0.12, 0.005, 0.08, "#475569", 0.06, 0.78, 0.01)); // 觸控板
  // 螢幕上蓋（微傾 15 度）
  const lid = box(0.44, 0.32, 0.02, "#475569", 0.06, 0.91, -0.06);
  lid.rotation.x = -0.22;
  const screen = box(0.39, 0.27, 0.015, "#38bdf8", 0.06, 0.92, -0.05, 0x0284c7);
  screen.rotation.x = -0.22;
  g.add(lid, screen);

  // 4. 右前溫熱咖啡杯（亮橘馬克杯、熱咖啡深褐表面、杯把）
  g.add(cyl(0.065, 0.06, 0.12, "#ea580c", 0.38, 0.76, 0.15, 8));
  g.add(cyl(0.055, 0.055, 0.02, "#451a03", 0.38, 0.86, 0.15, 8));
  g.add(box(0.02, 0.06, 0.04, "#ea580c", 0.44, 0.81, 0.15));

  // 5. 右後鵝頸金屬檯燈（暖黃燈罩、溫馨燈泡自發光）
  g.add(cyl(0.08, 0.09, 0.03, "#f59e0b", 0.42, 0.76, -0.2, 8)); // 燈座
  g.add(cyl(0.02, 0.02, 0.28, "#d97706", 0.42, 0.85, -0.2, 6)); // 燈桿
  const lampHead = cone(0.12, 0.16, "#fbbf24", 0.32, 0.98, -0.12, 8);
  lampHead.rotation.z = 0.55;
  lampHead.rotation.x = -0.35;
  g.add(lampHead);
  g.add(ball(0.05, "#fef08a", 0.32, 0.95, -0.12, 6));

  return g;
}

// 繪本風導師人偶（深藍八面斗篷／披肩、純白立領與手腕、親切膚色頭部、桃紅腮紅、深藍傾斜畫家貝雷帽）
function createStorybookTeacher(x, y, z, rotY = 0) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  g.rotation.y = rotY;

  // 雙腳鞋履與深色長褲
  [-0.12, 0.12].forEach(lx => {
    g.add(cyl(0.09, 0.09, 0.12, "#0f172a", lx, 0, 0, 8));
    g.add(cyl(0.07, 0.07, 0.3, "#1e293b", lx, 0.1, 0, 6));
  });

  // 經典深藍八面立體斗篷 (Low-poly flat-shaded poncho)
  const poncho = cone(0.46, 0.96, "#2563eb", 0, 0.35, 0, 8);
  g.add(poncho);

  // 純白立領與手腕袖口
  g.add(cyl(0.18, 0.22, 0.07, "#f8fafc", 0, 1.28, 0, 8));
  g.add(ball(0.08, "#f8fafc", -0.28, 0.78, 0.14, 6));
  g.add(ball(0.08, "#f8fafc", 0.28, 0.78, 0.14, 6));

  // 親切膚色頭部
  g.add(ball(0.25, "#fed7aa", 0, 1.48, 0, 10));
  // 雙眼
  g.add(ball(0.036, "#0f172a", -0.085, 1.5, 0.22, 6));
  g.add(ball(0.036, "#0f172a", 0.085, 1.5, 0.22, 6));
  // 溫暖桃粉腮紅
  g.add(ball(0.042, "#fda4af", -0.14, 1.43, 0.19, 6));
  g.add(ball(0.042, "#fda4af", 0.14, 1.43, 0.19, 6));

  // 帥氣傾斜深藍畫家貝雷帽 (Chic Artist Beret)
  const beretRim = cyl(0.28, 0.24, 0.08, "#1e293b", 0.03, 1.66, -0.02, 10);
  beretRim.rotation.z = -0.2;
  const beretTop = ball(0.3, "#0f172a", 0.04, 1.72, -0.03, 10);
  beretTop.scale.set(1.15, 0.42, 1.15);
  beretTop.rotation.z = -0.2;
  const stalk = cyl(0.02, 0.02, 0.06, "#1e293b", 0.04, 1.86, -0.03, 4);
  g.add(beretRim, beretTop, stalk);

  return g;
}

// 繪本風特教學童／小王子人偶（暖褐靴子、翠綠八面斗篷外套、金黃飄逸長圍巾、金色刺蝟短髮、開朗笑顏）
function createStorybookStudent(x, y, z, rotY = 0) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  g.rotation.y = rotY;

  // 暖褐小皮靴
  [-0.1, 0.1].forEach(lx => {
    g.add(cyl(0.08, 0.08, 0.1, "#78350f", lx, 0, 0, 8));
  });

  // 翠綠八面立體斗篷外套
  const tunic = cone(0.42, 0.84, "#15803d", 0, 0.28, 0, 8);
  g.add(tunic);
  // 皮帶
  g.add(cyl(0.28, 0.28, 0.06, "#b45309", 0, 0.5, 0, 8));

  // 金黃飄逸小王子圍巾（領圈＋飄逸長圍巾尾翼）
  g.add(cyl(0.22, 0.22, 0.08, "#facc15", 0, 1.1, 0, 8));
  const scarfTail1 = box(0.12, 0.36, 0.04, "#eab308", -0.22, 1.0, -0.15);
  scarfTail1.rotation.z = 0.45;
  scarfTail1.rotation.x = -0.25;
  const scarfTail2 = box(0.1, 0.28, 0.04, "#facc15", 0.18, 0.98, -0.18);
  scarfTail2.rotation.z = -0.35;
  g.add(scarfTail1, scarfTail2);

  // 圓圓可愛臉蛋
  g.add(ball(0.22, "#fed7aa", 0, 1.3, 0, 10));
  // 雙眼與開朗笑容
  g.add(ball(0.035, "#0f172a", -0.075, 1.32, 0.19, 6));
  g.add(ball(0.035, "#0f172a", 0.075, 1.32, 0.19, 6));
  g.add(box(0.06, 0.02, 0.01, "#b91c1c", 0, 1.23, 0.21));
  // 桃紅腮紅
  g.add(ball(0.038, "#fda4af", -0.12, 1.27, 0.17, 6));
  g.add(ball(0.038, "#fda4af", 0.12, 1.27, 0.17, 6));

  // 亮黃小王子刺蝟金髮
  g.add(ball(0.24, "#fde047", 0, 1.38, -0.02, 10));
  g.add(cone(0.12, 0.26, "#eab308", 0, 1.58, 0, 5));
  g.add(cone(0.08, 0.18, "#eab308", -0.12, 1.5, 0, 4));
  g.add(cone(0.08, 0.18, "#eab308", 0.12, 1.5, 0, 4));

  // 雙手捧著的學習筆記冊
  const note = box(0.22, 0.15, 0.02, "#ffffff", 0, 0.78, 0.28);
  note.rotation.x = -0.4;
  g.add(note);

  return g;
}

// 🏫 中央希望學園專屬島嶼基座（寬闊圓形 16 邊心靈港灣台地、前方親水碼頭與白鯨停泊水灣）
function buildHopeSchoolCenter(radius, height, x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);

  // 主台地岩壁（16邊圓形）
  const cliff = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.05, radius * 0.92, height, 16), mat("#6d4c41"));
  cliff.position.y = height / 2 - 0.25;
  cliff.castShadow = true; cliff.receiveShadow = true;
  g.add(cliff);

  // 暖金鑲邊護欄
  const rim = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.08, radius * 1.05, 0.38, 16), mat("#f59e0b"));
  rim.position.y = height - 0.32;
  rim.castShadow = true; rim.receiveShadow = true;
  g.add(rim);

  // 頂層綠意草坪
  const top = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.02, radius * 1.02, 0.28, 16), mat("#fdfbf7"));
  top.position.y = height - 0.18;
  top.receiveShadow = true;
  g.add(top);

  // 前方延伸親水木棧碼頭（白鯨啟航處）
  const dock = box(radius * 0.88, 0.22, 1.35, "#8d6e63", 0, height - 0.08, radius * 0.72);
  g.add(dock);
  [-radius * 0.36, 0, radius * 0.36].forEach(px => {
    g.add(cyl(0.12, 0.12, 0.75, "#5d4037", px, height + 0.15, radius * 0.85, 6));
  });

  // 島內十字石板大道
  g.add(box(radius * 1.55, 0.06, 0.85, "#f1f5f9", 0, height - 0.04, 0));
  g.add(box(0.85, 0.06, radius * 1.55, "#f1f5f9", 0, height - 0.04, 0));

  return { group: g, topY: height - 0.05 };
}

// 🏫 希望學園核心 3D 建築群（主校舍、希望之鐘樓、校訓石碑、晨光旗台、守護白鯨）
function createHopeSchoolMonument(yBase) {
  const g = new THREE.Group();
  g.position.set(0, yBase, 0);

  // 1. 學園主校舍（象牙暖白兩層建築，磚紅雙斜屋頂）
  const mainBld = box(3.6, 1.95, 2.2, "#fdfbf7", 0, 0.975, -0.6);
  g.add(mainBld);

  // 左右側翼教室
  const wingL = box(1.5, 1.55, 1.9, "#fdfbf7", -2.1, 0.775, -0.6);
  const wingR = box(1.5, 1.55, 1.9, "#fdfbf7", 2.1, 0.775, -0.6);
  g.add(wingL, wingR);

  // 主屋頂（溫馨磚紅）
  const roofMain = cone(2.5, 1.15, "#c2410c", 0, 2.55, -0.6, 4);
  roofMain.rotation.y = Math.PI / 4;
  roofMain.scale.set(1.2, 0.85, 0.88);
  g.add(roofMain);

  const roofL = cone(1.25, 0.85, "#b91c1c", -2.1, 1.95, -0.6, 4);
  roofL.rotation.y = Math.PI / 4;
  const roofR = cone(1.25, 0.85, "#b91c1c", 2.1, 1.95, -0.6, 4);
  roofR.rotation.y = Math.PI / 4;
  g.add(roofL, roofR);

  // 正門入口柱廊
  g.add(box(1.7, 0.2, 0.9, "#f1f5f9", 0, 0.1, 0.85)); // 門階
  g.add(cyl(0.12, 0.12, 1.45, "#ffffff", -0.65, 0.8, 0.85, 8)); // 柱L
  g.add(cyl(0.12, 0.12, 1.45, "#ffffff", 0.65, 0.8, 0.85, 8)); // 柱R
  g.add(box(1.7, 0.25, 0.9, "#e2e8f0", 0, 1.55, 0.85)); // 柱頂山牆

  // 教室發光窗戶（上下排）
  [-1.1, -0.4, 0.4, 1.1].forEach(wx => {
    g.add(box(0.38, 0.52, 0.05, "#38bdf8", wx, 1.35, 0.52));
    g.add(box(0.38, 0.52, 0.05, "#fde047", wx, 0.6, 0.52));
  });

  // 2. 中央希望之鐘樓（金黃鐘塔頂端＋希望之鐘）
  const tower = cyl(0.72, 0.82, 2.3, "#f8fafc", 0, 2.65, -0.6, 8);
  g.add(tower);
  // 鐘樓鏤空閣
  g.add(box(0.48, 0.72, 1.5, "#1e293b", 0, 2.85, -0.6));
  // 金色希望之鐘
  const bell = ball(0.32, "#f59e0b", 0, 2.8, -0.6, 8);
  bell.scale.set(1.0, 1.3, 1.0);
  g.add(bell);
  // 尖頂與金色風向球
  const towerRoof = cone(0.88, 1.35, "#f59e0b", 0, 4.45, -0.6, 8);
  g.add(towerRoof);
  g.add(ball(0.18, "#fbbf24", 0, 5.25, -0.6, 8));

  // 3. 校門口：校訓石碑（玉白底座＋金色牌匾「快樂活潑，自立自強」銘文）
  const stoneBase = box(1.85, 0.32, 0.72, "#475569", 0, 0.16, 1.85);
  const stoneBody = box(1.65, 0.82, 0.25, "#f8fafc", 0, 0.68, 1.85);

  // 繪製校訓金字銘文牌匾紋理
  const mottoCanvas = document.createElement("canvas");
  mottoCanvas.width = 512; mottoCanvas.height = 192;
  const mctx = mottoCanvas.getContext("2d");
  mctx.fillStyle = "#f59e0b";
  mctx.fillRect(0, 0, 512, 192);
  mctx.strokeStyle = "#92400e";
  mctx.lineWidth = 10;
  mctx.strokeRect(5, 5, 502, 182);
  mctx.fillStyle = "#ffffff";
  mctx.font = "900 36px 'Noto Sans TC', sans-serif";
  mctx.textAlign = "center";
  mctx.textBaseline = "middle";
  mctx.fillText("快樂活潑・自立自強", 256, 96);
  const mottoTex = new THREE.CanvasTexture(mottoCanvas);
  const plaqueMat = new THREE.MeshLambertMaterial({ map: mottoTex });
  const plaque = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.65, 0.06), plaqueMat);
  plaque.position.set(0, 0.68, 1.98);
  g.add(stoneBase, stoneBody, plaque);
  // 兩側路燈
  g.add(createStreetLamp(-1.25, 0, 1.85));
  g.add(createStreetLamp(1.25, 0, 1.85));

  // 4. 晨光操場升旗台
  g.add(cyl(0.06, 0.06, 3.6, "#94a3b8", -2.8, 0.1, 1.3, 6)); // 旗桿
  const flag = box(0.95, 0.58, 0.04, "#0284c7", -2.3, 3.25, 1.3); // 旗幟
  flag.rotation.y = 0.15;
  g.add(flag);

  // 5. 碼頭守護白鯨（溫柔的白鯨領航員）
  const whaleG = new THREE.Group();
  whaleG.position.set(2.45, 0.1, 1.35);
  whaleG.rotation.y = -0.52;
  const whaleBody = ball(0.78, "#ffffff", 0, 0.38, 0, 12);
  whaleBody.scale.set(1.45, 0.85, 0.95);
  const whaleFinL = box(0.45, 0.08, 0.22, "#e2e8f0", -0.15, 0.32, 0.78);
  whaleFinL.rotation.y = 0.45;
  const whaleFinR = box(0.45, 0.08, 0.22, "#e2e8f0", -0.15, 0.32, -0.78);
  whaleFinR.rotation.y = -0.45;
  const whaleTail = cone(0.38, 0.72, "#ffffff", -1.05, 0.46, 0, 6);
  whaleTail.rotation.z = Math.PI / 2.3;
  whaleG.add(whaleBody, whaleFinL, whaleFinR, whaleTail);
  // 白鯨彩虹水花光環
  whaleG.add(ball(0.16, "#38bdf8", 0.48, 1.05, 0, 6));
  whaleG.add(ball(0.11, "#7dd3fc", 0.56, 1.38, 0.05, 6));
  whaleG.add(ball(0.07, "#bae6fd", 0.62, 1.62, -0.05, 6));
  g.add(whaleG);

  // 6. 陪伴校舍的綠樹
  g.add(createTree(-3.3, 0, -1.9, 1.2, 0));
  g.add(createTree(3.3, 0, -1.9, 1.2, 1));
  g.add(createTree(-3.0, 0, 2.1, 0.95, 2));

  // 7. 繪本風戶外研討木書桌（研討長桌、彩色典籍疊、發光筆電、溫熱咖啡杯、鵝頸檯燈、小圓椅）
  g.add(createOutdoorStudyCorner(-2.25, 0, 2.05, 0.45));

  // 8. 師生親切共學人偶（導師：深藍斗篷＋畫家貝雷帽；特教學童／小王子：翠綠斗篷＋金黃飄逸圍巾與閃亮金髮）
  g.add(createStorybookTeacher(-1.65, 0, 1.85, -0.95));
  g.add(createStorybookStudent(-1.45, 0, 2.55, 2.35));

  // 9. 地坪手作石板碎屑與小雛菊純真花叢（散落於前庭綠意草坪、校訓石碑旁與親水碼頭周邊）
  g.add(createPebbleScatter(-1.3, 0, 1.45, 8, 0.65));
  g.add(createPebbleScatter(0.0, 0, 2.35, 7, 0.7));
  g.add(createPebbleScatter(1.2, 0, 1.85, 6, 0.55));
  g.add(createDaisyCluster(-2.6, 0, 1.8, 5, 0.5));
  g.add(createDaisyCluster(-1.9, 0, 2.5, 4, 0.4));
  g.add(createDaisyCluster(1.4, 0, 2.4, 5, 0.5));
  g.add(createDaisyCluster(2.8, 0, 1.9, 4, 0.4));
  g.add(createDaisyCluster(-3.2, 0, 0.8, 4, 0.4));
  g.add(createDaisyCluster(3.1, 0, 0.8, 4, 0.4));

  return g;
}

// 🏝️ 10 大領域專屬獨立地貌島嶼建造器（每座島具備獨特輪廓、水灣、階梯與地貌造型）
function createDomainIslandPlatform(radius, height, topHex, trimHex, dirtHex, x, z, shapeType = "hex") {
  const g = new THREE.Group();
  g.position.set(x, 0, z);

  if (shapeType === "crescent_bay") {
    // 🏠 特需生活管理島：掌心海灣形（弧形高地圍繞碧藍內灣池與小棧橋）
    const cliff = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.05, radius * 0.88, height, 14), mat(dirtHex));
    cliff.position.y = height / 2 - 0.25;
    cliff.castShadow = true; cliff.receiveShadow = true;
    g.add(cliff);

    const rim = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.08, radius * 1.05, 0.34, 14), mat(trimHex));
    rim.position.y = height - 0.32;
    g.add(rim);

    const top = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.02, radius * 1.02, 0.26, 14), mat(topHex));
    top.position.y = height - 0.18;
    g.add(top);

    // 前方碧藍掌心水灣（內嵌式水池）
    const covePool = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.48, radius * 0.48, 0.12, 12), mat("#38bdf8"));
    covePool.position.set(0, height - 0.08, radius * 0.35);
    g.add(covePool);
    // 弧形碼頭棧板
    const dock = box(radius * 0.65, 0.14, 0.45, "#8d6e63", 0, height - 0.04, radius * 0.62);
    g.add(dock);

  } else if (shapeType === "stepped_terrace") {
    // 🤸 特需動作訓練島：雙層階梯台地（高低雙層山丘、攀登石階）
    const cliff = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.0, radius * 0.82, height, 8), mat(dirtHex));
    cliff.position.y = height / 2 - 0.25;
    cliff.castShadow = true; cliff.receiveShadow = true;
    g.add(cliff);

    const rim = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.04, radius * 1.02, 0.34, 8), mat(trimHex));
    rim.position.y = height - 0.32;
    g.add(rim);

    const top = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.98, radius * 0.98, 0.26, 8), mat(topHex));
    top.position.y = height - 0.18;
    g.add(top);

    // 第二層躍動高台（右後方突起山丘）
    const highHill = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.45, radius * 0.52, 0.65, 8), mat(topHex));
    highHill.position.set(radius * 0.32, height + 0.18, -radius * 0.25);
    g.add(highHill);
    // 攀登三級跳石階梯
    for (let i = 0; i < 3; i++) {
      const step = box(0.72, 0.16, 0.38, "#d7ccc8", radius * 0.12 + i * 0.12, height + i * 0.15, -radius * 0.15 + i * 0.12);
      g.add(step);
    }

  } else if (shapeType === "open_book") {
    // 📖 語文繪本島：精裝展開繪本書卷（兩翼微揚厚書台地）
    const cliff = new THREE.Mesh(new THREE.BoxGeometry(radius * 1.85, height, radius * 1.45), mat(dirtHex));
    cliff.position.y = height / 2 - 0.25;
    cliff.castShadow = true; cliff.receiveShadow = true;
    g.add(cliff);

    // 書脊中線石路
    g.add(box(0.42, height + 0.1, radius * 1.5, "#4a3b32", 0, height / 2 - 0.15, 0));

    // 左書頁台地
    const pageL = box(radius * 0.88, 0.3, radius * 1.35, topHex, -radius * 0.46, height - 0.12, 0);
    pageL.rotation.z = 0.08;
    // 右書頁台地
    const pageR = box(radius * 0.88, 0.3, radius * 1.35, topHex, radius * 0.46, height - 0.12, 0);
    pageR.rotation.z = -0.08;
    g.add(pageL, pageR);

    // 金色書頁滾邊
    g.add(box(radius * 1.88, 0.12, 0.15, trimHex, 0, height - 0.22, radius * 0.68));

  } else if (shapeType === "crystal_square") {
    // 📐 數學邏輯島：八角幾何同心階梯
    const cliff = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.98, radius * 0.82, height, 8), mat(dirtHex));
    cliff.position.y = height / 2 - 0.25;
    cliff.castShadow = true; cliff.receiveShadow = true;
    g.add(cliff);

    const rim = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.05, radius * 1.02, 0.34, 8), mat(trimHex));
    rim.position.y = height - 0.32;
    g.add(rim);

    const top = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.96, radius * 0.96, 0.26, 8), mat(topHex));
    top.position.y = height - 0.18;
    g.add(top);

    // 幾何同心方形石板拼圖
    g.add(box(radius * 0.88, 0.05, radius * 0.88, "#fef08a", 0, height - 0.04, 0));
    g.add(box(radius * 0.48, 0.08, radius * 0.48, "#f59e0b", 0, height - 0.02, 0));

  } else if (shapeType === "stadium_oval") {
    // 🏃 健體活力島：橢圓形運動場跑道島
    const cliff = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.02, radius * 0.84, height, 16), mat(dirtHex));
    cliff.position.y = height / 2 - 0.25;
    cliff.scale.set(1.22, 1, 0.92);
    g.add(cliff);

    // 外圈深紅色 PU 跑道環
    const track = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.15, radius * 1.12, 0.28, 16), mat("#d32f2f"));
    track.position.y = height - 0.25;
    track.scale.set(1.22, 1, 0.92);
    g.add(track);

    // 中央草坪
    const top = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.85, radius * 0.85, 0.32, 16), mat(topHex));
    top.position.y = height - 0.16;
    top.scale.set(1.22, 1, 0.92);
    g.add(top);

  } else if (shapeType === "nature_spiral") {
    // 🌱 自然探險島：相切雙圓螺旋貝殼階梯
    const cliffA = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.85, radius * 0.72, height, 12), mat(dirtHex));
    cliffA.position.set(-radius * 0.15, height / 2 - 0.25, 0);
    g.add(cliffA);

    const cliffB = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.55, radius * 0.48, height + 0.38, 10), mat("#5d4037"));
    cliffB.position.set(radius * 0.52, (height + 0.38) / 2 - 0.25, -radius * 0.2);
    g.add(cliffB);

    const topA = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.82, radius * 0.82, 0.26, 12), mat(topHex));
    topA.position.set(-radius * 0.15, height - 0.18, 0);
    g.add(topA);

    const topB = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.52, radius * 0.52, 0.26, 10), mat("#a5d6a7"));
    topB.position.set(radius * 0.52, height + 0.24, -radius * 0.2);
    g.add(topB);

  } else if (shapeType === "town_blocks") {
    // 🏮 社會生活島：四方街區十字城鎮
    const cliff = new THREE.Mesh(new THREE.BoxGeometry(radius * 1.65, height, radius * 1.65), mat(dirtHex));
    cliff.position.y = height / 2 - 0.25;
    g.add(cliff);

    const top = new THREE.Mesh(new THREE.BoxGeometry(radius * 1.62, 0.26, radius * 1.62), mat(topHex));
    top.position.y = height - 0.18;
    g.add(top);

    // 十字深灰柏油馬路與斑馬線
    g.add(box(radius * 1.64, 0.06, 0.95, "#475569", 0, height - 0.04, 0));
    g.add(box(0.95, 0.06, radius * 1.64, "#475569", 0, height - 0.04, 0));

  } else if (shapeType === "treasure_isles") {
    // 🌏 綜合活動島：主島伴隨雙浮游小島礁
    const cliff = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.92, radius * 0.78, height, 7), mat(dirtHex));
    cliff.position.y = height / 2 - 0.25;
    g.add(cliff);

    const top = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.88, radius * 0.88, 0.26, 7), mat(topHex));
    top.position.y = height - 0.18;
    g.add(top);

    // 小子島 1（東北小島）
    const sub1 = new THREE.Mesh(new THREE.CylinderGeometry(1.25, 0.95, height * 0.75, 6), mat(dirtHex));
    sub1.position.set(radius * 0.95, height * 0.75 / 2 - 0.25, -radius * 0.55);
    const subTop1 = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 0.2, 6), mat(trimHex));
    subTop1.position.set(radius * 0.95, height * 0.75 - 0.15, -radius * 0.55);
    g.add(sub1, subTop1);

    // 連接子島的小木棧道
    const footBridge = box(1.35, 0.12, 0.42, "#8d6e63", radius * 0.65, height * 0.75 - 0.05, -radius * 0.35);
    footBridge.rotation.y = -0.52;
    g.add(footBridge);

  } else if (shapeType === "artist_palette") {
    // 🎨 藝術創想島：流線型調色盤橢圓附拇指天池
    const cliff = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.15, radius * 0.95, height, 16), mat(dirtHex));
    cliff.position.y = height / 2 - 0.25;
    cliff.scale.set(1.25, 1, 0.95);
    g.add(cliff);

    const top = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.12, radius * 1.12, 0.26, 16), mat(topHex));
    top.position.y = height - 0.18;
    top.scale.set(1.25, 1, 0.95);
    g.add(top);

    // 調色盤拇指孔（圓形內嵌海蝕池）
    const thumbHole = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.32, radius * 0.32, 0.22, 12), mat("#38bdf8"));
    thumbHole.position.set(-radius * 0.65, height - 0.08, 0);
    g.add(thumbHole);

    // 調色盤邊緣彩色顏料色滴（紅黃綠藍）
    const paintColors = ["#ef4444", "#eab308", "#22c55e", "#3b82f6", "#a855f7"];
    paintColors.forEach((pcol, pi) => {
      const ang = (pi / paintColors.length) * Math.PI * 0.85 - 0.35;
      const px = Math.cos(ang) * (radius * 0.85);
      const pz = Math.sin(ang) * (radius * 0.7);
      const dollop = ball(0.24, pcol, px, height - 0.02, pz, 6);
      dollop.scale.set(1.2, 0.35, 1.2);
      g.add(dollop);
    });

  } else if (shapeType === "sprout_petal") {
    // 🎒 生活課程啟蒙島：三葉嫩芽花瓣圓潤台地
    const cliff = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.0, radius * 0.85, height, 16), mat(dirtHex));
    cliff.position.y = height / 2 - 0.25;
    g.add(cliff);

    const top = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.98, radius * 0.98, 0.26, 16), mat(topHex));
    top.position.y = height - 0.18;
    g.add(top);

    // 三片展開的花瓣小草丘
    for (let pi = 0; pi < 3; pi++) {
      const pang = (pi / 3) * Math.PI * 2;
      const pet = ball(radius * 0.45, "#fbcfe8", Math.cos(pang) * radius * 0.42, height - 0.08, Math.sin(pang) * radius * 0.42, 8);
      pet.scale.set(1.1, 0.22, 1.1);
      g.add(pet);
    }

  } else {
    // 預設經典六角島
    const cliff = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.98, radius * 0.82, height, 6), mat(dirtHex));
    cliff.position.y = height / 2 - 0.25;
    cliff.castShadow = true; cliff.receiveShadow = true;
    g.add(cliff);

    const rim = new THREE.Mesh(new THREE.CylinderGeometry(radius * 1.03, radius * 1.01, 0.34, 6), mat(trimHex));
    rim.position.y = height - 0.32;
    g.add(rim);

    const top = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.96, radius * 0.96, 0.26, 6), mat(topHex));
    top.position.y = height - 0.18;
    g.add(top);
  }

  return { group: g, topY: height - 0.05 };
}

let currentAttrFilter = "all"; // 領域島內依單元屬性篩選 ("all" 或 attrTag)

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

// 依 10 大領域切換專屬植被與地貌樹種（讓每座領域島一眼看出不同生態與主題氛圍）
function createDomainFoliage(domainId, x, y, z, scale = 1, idx = 0) {
  const g = new THREE.Group();
  g.position.set(x, y, z);

  if (domainId === "selfcare") {
    // 水藍潔淨泡泡樹＆薄荷圓球樹
    g.add(cyl(0.1 * scale, 0.13 * scale, 0.52 * scale, "#8d6e63", 0, 0, 0, 6));
    g.add(ball(0.52 * scale, idx % 2 === 0 ? "#4dd0e1" : "#81c784", 0, 0.82 * scale, 0, 8));
    g.add(ball(0.34 * scale, "#e0f7fa", 0.26 * scale, 1.12 * scale, 0.15 * scale, 7));
    g.add(ball(0.22 * scale, "#ffffff", -0.22 * scale, 1.25 * scale, -0.1 * scale, 6));
  } else if (domainId === "motor") {
    // 感統彈跳彩球樹（三色活力圓球串）
    g.add(cyl(0.09 * scale, 0.12 * scale, 0.5 * scale, "#5c6bc0", 0, 0, 0, 6));
    g.add(ball(0.48 * scale, "#ab47bc", 0, 0.72 * scale, 0, 8));
    g.add(ball(0.38 * scale, "#ffca28", 0.12 * scale, 1.2 * scale, 0, 8));
    g.add(ball(0.28 * scale, "#29b6f6", -0.1 * scale, 1.58 * scale, 0, 8));
  } else if (domainId === "chinese") {
    // 金秋銀杏書香樹（結著紅蘋果果實）
    g.add(cyl(0.11 * scale, 0.15 * scale, 0.58 * scale, "#6d4c41", 0, 0, 0, 6));
    g.add(ball(0.58 * scale, "#ffb300", 0, 0.86 * scale, 0, 7));
    g.add(ball(0.42 * scale, "#ffd54f", 0.25 * scale, 1.1 * scale, 0.14 * scale, 7));
    g.add(ball(0.14 * scale, "#e53935", -0.32 * scale, 0.92 * scale, 0.28 * scale, 6));
  } else if (domainId === "math") {
    // 幾何積木樹（正方體樹冠與金字塔樹冠）
    g.add(cyl(0.1 * scale, 0.13 * scale, 0.55 * scale, "#546e7a", 0, 0, 0, 6));
    if (idx % 2 === 0) {
      g.add(box(0.85 * scale, 0.85 * scale, 0.85 * scale, "#29b6f6", 0, 0.52 * scale, 0));
      g.add(box(0.55 * scale, 0.55 * scale, 0.55 * scale, "#ffca28", 0.22 * scale, 1.15 * scale, 0.15 * scale));
    } else {
      g.add(cone(0.68 * scale, 1.15 * scale, "#26a69a", 0, 0.5 * scale, 0, 4));
    }
  } else if (domainId === "pe") {
    // 陽光運動棕櫚椰子樹
    g.add(cyl(0.09 * scale, 0.15 * scale, 1.15 * scale, "#8d6e63", 0, 0, 0, 6));
    for (let a = 0; a < 5; a++) {
      const leaf = box(0.75 * scale, 0.1 * scale, 0.28 * scale, "#66bb6a", Math.cos(a * 1.25) * 0.35 * scale, 1.12 * scale, Math.sin(a * 1.25) * 0.35 * scale);
      leaf.rotation.y = -a * 1.25;
      g.add(leaf);
    }
    g.add(ball(0.14 * scale, "#fb8c00", 0.12 * scale, 1.02 * scale, 0.12 * scale, 6));
  } else if (domainId === "nature") {
    // 巨型向日葵＆生態雨林大樹
    if (idx % 2 === 0) {
      g.add(cyl(0.08 * scale, 0.1 * scale, 0.85 * scale, "#43a047", 0, 0, 0, 6));
      g.add(cyl(0.48 * scale, 0.48 * scale, 0.14 * scale, "#fdd835", 0, 0.85 * scale, 0, 10));
      g.add(cyl(0.24 * scale, 0.24 * scale, 0.18 * scale, "#5d4037", 0, 0.86 * scale, 0, 8));
    } else {
      return createTree(x, y, z, scale * 1.12, 0);
    }
  } else if (domainId === "society") {
    // 台灣紅燈籠櫻花樹
    g.add(cyl(0.11 * scale, 0.15 * scale, 0.58 * scale, "#5d4037", 0, 0, 0, 6));
    g.add(ball(0.58 * scale, "#f48fb1", 0, 0.86 * scale, 0, 7));
    g.add(ball(0.4 * scale, "#f8bbd0", 0.24 * scale, 1.1 * scale, 0.12 * scale, 7));
    g.add(ball(0.16 * scale, "#d32f2f", -0.35 * scale, 0.62 * scale, 0.22 * scale, 6));
  } else if (domainId === "arts") {
    // 粉紫馬卡龍調色樹
    g.add(cyl(0.1 * scale, 0.13 * scale, 0.55 * scale, "#795548", 0, 0, 0, 6));
    g.add(ball(0.54 * scale, "#ce93d8", 0, 0.82 * scale, 0, 8));
    g.add(ball(0.38 * scale, "#f48fb1", 0.24 * scale, 1.12 * scale, 0.15 * scale, 7));
    g.add(ball(0.3 * scale, "#fff59d", -0.2 * scale, 1.18 * scale, -0.12 * scale, 7));
  } else {
    return createTree(x, y, z, scale, idx);
  }
  return g;
}

// 依單元名稱與屬性 (propType) 自動建立 18 種立體微縮主題標誌（直接擺在該單元建築旁或屋頂前！）
function createUnitTopicProp(propType, x = 0, y = 0, z = 0, scale = 1) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  g.scale.set(scale, scale, scale);

  if (propType === "tooth_clean") {
    // 🦷 立體大白牙齒＋水藍潔淨泡泡
    g.add(cyl(0.38, 0.42, 0.14, "#f48fb1", 0, 0, 0, 8));
    g.add(box(0.46, 0.52, 0.36, "#ffffff", 0, 0.14, 0));
    g.add(ball(0.24, "#ffffff", -0.14, 0.66, 0, 7));
    g.add(ball(0.24, "#ffffff", 0.14, 0.66, 0, 7));
    g.add(ball(0.18, "#4dd0e1", 0.32, 0.45, 0.2, 6));
  } else if (propType === "clothes_shoe") {
    // 👕 迷你彩色T恤展示架＋小紅鞋
    g.add(cyl(0.06, 0.08, 0.75, "#8d6e63", 0, 0, 0, 6));
    g.add(box(0.52, 0.48, 0.22, "#29b6f6", 0, 0.32, 0));
    g.add(box(0.82, 0.18, 0.2, "#4fc3f7", 0, 0.58, 0));
    g.add(box(0.28, 0.18, 0.38, "#ef5350", 0.35, 0, 0.25));
  } else if (propType === "recycle_bin") {
    // ♻️ 藍綠黃三色分類回收桶組
    g.add(cyl(0.18, 0.14, 0.48, "#1e88e5", -0.34, 0, 0, 7));
    g.add(cyl(0.18, 0.14, 0.48, "#43a047", 0, 0, 0, 7));
    g.add(cyl(0.18, 0.14, 0.48, "#fdd835", 0.34, 0, 0, 7));
  } else if (propType === "traffic_car") {
    // 🚦 立體紅綠燈號誌桿＋迷你小車
    g.add(cyl(0.05, 0.06, 0.95, "#37474f", -0.25, 0, 0, 6));
    g.add(box(0.24, 0.56, 0.18, "#263238", -0.25, 0.55, 0));
    g.add(ball(0.07, "#ef5350", -0.25, 0.98, 0.1, 6));
    g.add(ball(0.07, "#ffee58", -0.25, 0.82, 0.1, 6));
    g.add(ball(0.07, "#66bb6a", -0.25, 0.66, 0.1, 6));
    g.add(box(0.48, 0.28, 0.34, "#ff7043", 0.22, 0.06, 0.15));
  } else if (propType === "food_health") {
    // 🍱 美味餐盤＋紅蘋果與橘胡蘿蔔
    g.add(cyl(0.45, 0.4, 0.1, "#ffffff", 0, 0, 0, 10));
    g.add(ball(0.22, "#e53935", -0.12, 0.24, 0, 8));
    g.add(cone(0.14, 0.42, "#fb8c00", 0.18, 0.1, 0.08, 6));
  } else if (propType === "hand_grip") {
    // ✋ 彩色疊疊樂精細積木塔＋抓握環
    g.add(box(0.42, 0.24, 0.42, "#ef5350", 0, 0, 0));
    g.add(box(0.34, 0.24, 0.34, "#ffca28", 0, 0.24, 0));
    g.add(box(0.26, 0.24, 0.26, "#29b6f6", 0, 0.48, 0));
  } else if (propType === "foot_balance") {
    // 🦶 感統平衡木＋紅白跨欄架
    g.add(box(0.85, 0.14, 0.24, "#ffb74d", 0, 0.16, 0));
    g.add(box(0.14, 0.16, 0.24, "#8d6e63", -0.32, 0, 0));
    g.add(box(0.14, 0.16, 0.24, "#8d6e63", 0.32, 0, 0));
    g.add(ball(0.22, "#ab47bc", 0, 0.48, 0, 8));
  } else if (propType === "book_story") {
    // 📖 立體敞開故事繪本台
    g.add(box(0.65, 0.14, 0.48, "#8d6e63", 0, 0, 0));
    g.add(box(0.56, 0.12, 0.42, "#fff9c4", 0, 0.14, 0));
    g.add(cone(0.2, 0.45, "#ffb300", 0, 0.26, 0, 5));
  } else if (propType === "nature_plant") {
    // 🌻 盛開向日葵花盆與綠芽
    g.add(cyl(0.26, 0.2, 0.32, "#bf360c", 0, 0, 0, 7));
    g.add(cyl(0.05, 0.05, 0.45, "#43a047", 0, 0.32, 0, 6));
    g.add(ball(0.25, "#fdd835", 0, 0.78, 0, 8));
  } else if (propType === "animal_zoo") {
    // 🐾 可愛立體小動物雕像
    g.add(ball(0.28, "#ffb74d", 0, 0.26, 0, 8));
    g.add(ball(0.22, "#ffe082", 0, 0.56, 0.1, 8));
    g.add(cone(0.1, 0.22, "#f57c00", -0.14, 0.72, 0.1, 5));
    g.add(cone(0.1, 0.22, "#f57c00", 0.14, 0.72, 0.1, 5));
  } else if (propType === "science_lab") {
    // 🧲 紅藍雙極磁鐵＋實驗燒瓶
    g.add(box(0.16, 0.55, 0.16, "#e53935", -0.18, 0, 0));
    g.add(box(0.16, 0.55, 0.16, "#1e88e5", 0.18, 0, 0));
    g.add(box(0.52, 0.16, 0.16, "#eceff1", 0, 0.52, 0));
  } else if (propType === "math_shape") {
    // 📐 金字塔＋正方體＋圓球幾何組
    g.add(cone(0.32, 0.55, "#ffb300", -0.18, 0, 0, 4));
    g.add(box(0.34, 0.34, 0.34, "#29b6f6", 0.22, 0, 0.1));
    g.add(ball(0.2, "#ec407a", 0.05, 0.52, -0.1, 8));
  } else if (propType === "math_clock_num") {
    // ⏰ 立體黃金時鐘座
    g.add(cyl(0.34, 0.34, 0.14, "#0288d1", 0, 0.35, 0, 10));
    g.add(ball(0.26, "#fff9c4", 0, 0.38, 0.08, 8));
    g.add(box(0.45, 0.16, 0.26, "#fbc02d", 0, 0, 0));
  } else if (propType === "sport_ball") {
    // ⚽ 運動球類與迷你球門
    g.add(ball(0.26, "#ff7043", -0.15, 0.26, 0, 8));
    g.add(ball(0.22, "#ffffff", 0.22, 0.22, 0.12, 8));
  } else if (propType === "safety_med") {
    // 🛡️ 紅十字健康安全盾牌座
    g.add(box(0.52, 0.58, 0.16, "#ffffff", 0, 0.08, 0));
    g.add(box(0.34, 0.12, 0.2, "#e53935", 0, 0.31, 0));
    g.add(box(0.12, 0.34, 0.2, "#e53935", 0, 0.2, 0));
  } else if (propType === "music_drum") {
    // 🥁 立體紅金擊樂鼓座
    g.add(cyl(0.34, 0.34, 0.38, "#e53935", 0, 0, 0, 10));
    g.add(cyl(0.36, 0.36, 0.08, "#fff8e1", 0, 0.38, 0, 10));
    g.add(ball(0.14, "#ffd54f", 0, 0.62, 0, 6));
  } else if (propType === "art_palette") {
    // 🎨 立體三色大蠟筆與調色台
    g.add(cyl(0.1, 0.1, 0.55, "#ef5350", -0.22, 0, 0, 6));
    g.add(cone(0.1, 0.2, "#ef5350", -0.22, 0.55, 0, 6));
    g.add(cyl(0.1, 0.1, 0.62, "#ffca28", 0, 0, 0, 6));
    g.add(cone(0.1, 0.2, "#ffca28", 0, 0.62, 0, 6));
    g.add(cyl(0.1, 0.1, 0.5, "#ab47bc", 0.22, 0, 0, 6));
    g.add(cone(0.1, 0.2, "#ab47bc", 0.22, 0.5, 0, 6));
  } else {
    // 🎲 桌遊大骰子與紅燈籠串珠
    g.add(box(0.42, 0.42, 0.42, "#ffffff", -0.12, 0, 0));
    g.add(ball(0.08, "#e53935", -0.12, 0.22, 0.22, 6));
    g.add(ball(0.22, "#ef5350", 0.24, 0.52, 0, 8));
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

// 多樣化微縮建築生成器（除建築本體外，可根據該單元的 propType 在庭院前擺放專屬立體主題道具！）
function createUnitBuilding(x, y, z, styleIdx, roofColor, wallColor = "#ffffff", propType = "") {
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

  // 若有傳入單元專屬 propType，於建築右前方庭院擺放該單元的立體微縮模型！
  if (propType) {
    g.add(createUnitTopicProp(propType, 0.92, 0.02, 0.68, 0.95));
  }
  return g;
}

// 10 大領域專屬中央主題地標 (全部 10 種領域地標皆獨立建模，造型鮮明不重複)
function createDomainMonument(type, primaryColor, trimColor, yBase) {
  const g = new THREE.Group();
  g.position.set(0, yBase, 0);

  // 圓形石砌底座與紅旗
  g.add(cyl(2.2, 2.4, 0.22, "#e2e8f0", 0, 0, 0, 12));
  g.add(cyl(0.06, 0.06, 2.8, "#94a3b8", -1.5, 0.2, -1.0, 6));
  g.add(box(0.75, 0.45, 0.04, "#ef4444", -1.12, 2.45, -1.0));

  if (type === "lighthouse_whale") {
    // 🏠 特需生活管理島：繪本風紅白暖光燈塔（圓形投射暖光錐＋圓斑光暈）＋水池小白鯨＋大牙齒＋共學石板與小雛菊
    g.add(cyl(1.65, 1.7, 0.15, "#38bdf8", 0, 0.18, 0, 14));
    const whale = ball(0.62, "#0284c7", 0.35, 0.65, 0.2, 10);
    whale.scale.set(1.35, 0.85, 1.0);
    g.add(whale);

    // 階梯石砌底座與拱門木門
    g.add(cyl(1.35, 1.55, 0.45, "#78350f", -0.85, 0.2, -0.3, 10));
    g.add(box(0.38, 0.65, 0.08, "#451a03", -0.85, 0.38, 0.55));

    // 雙色紅白塔身（立體多段筒身）
    g.add(cyl(0.92, 1.2, 1.2, "#fef3c7", -0.85, 0.65, -0.3, 10)); // 下層暖白石磚
    g.add(cyl(0.86, 0.94, 0.7, "#dc2626", -0.85, 1.45, -0.3, 10)); // 中層活力磚紅
    g.add(cyl(0.8, 0.86, 0.55, "#fef3c7", -0.85, 2.0, -0.3, 10));  // 上層暖白石磚

    // 觀景平台露台與金屬護欄
    g.add(cyl(1.15, 1.15, 0.15, "#78350f", -0.85, 2.45, -0.3, 12));
    g.add(cyl(1.12, 1.12, 0.22, "#1e293b", -0.85, 2.6, -0.3, 12));

    // 發光燈室（金黃溫暖發光內核）
    g.add(cyl(0.68, 0.68, 0.7, "#fef08a", -0.85, 2.62, -0.3, 8, 0xfef08a));

    // 磚紅八角錐尖頂與黃金風向球
    g.add(cone(1.08, 0.85, "#dc2626", -0.85, 3.32, -0.3, 8));
    g.add(ball(0.18, "#f59e0b", -0.85, 4.22, -0.3, 8));

    // 🌟 燈塔暖光投射光錐（半透明加法混色發光光束，朝向地面光斑投射）
    const beamLength = 4.2;
    const beamGeom = new THREE.ConeGeometry(1.65, beamLength, 20, 1, true);
    beamGeom.translate(0, -beamLength / 2, 0);
    const beamMat = new THREE.MeshBasicMaterial({
      color: 0xfef08a,
      transparent: true,
      opacity: 0.36,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
      depthWrite: false
    });
    const beam = new THREE.Mesh(beamGeom, beamMat);
    beam.position.set(-0.85, 2.92, -0.3);
    beam.lookAt(1.15, 0.24, 1.25);
    beam.rotateX(-Math.PI / 2);
    g.add(beam);

    // 🌟 地面溫暖圓形光斑（暖黃光暈圓形光灘）
    const puddleGeom = new THREE.CircleGeometry(1.35, 24);
    const puddleMat = new THREE.MeshBasicMaterial({
      color: 0xfef08a,
      transparent: true,
      opacity: 0.45,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const puddle = new THREE.Mesh(puddleGeom, puddleMat);
    puddle.rotation.x = -Math.PI / 2;
    puddle.position.set(1.15, 0.24, 1.25);
    g.add(puddle);

    // 光斑旁休憩閱讀長椅與翻開的書本
    g.add(createBench(1.15, 0.22, 1.85, 0.2));
    g.add(box(0.24, 0.04, 0.18, "#ffffff", 1.15, 0.62, 1.85));

    // 散落小雛菊與石板碎屑
    g.add(createDaisyCluster(0.3, 0.22, 1.6, 4, 0.35));
    g.add(createDaisyCluster(1.9, 0.22, 1.2, 4, 0.35));
    g.add(createPebbleScatter(1.15, 0.22, 0.8, 6, 0.45));

    // 單元代表道具：潔白健康牙齒
    g.add(createUnitTopicProp("tooth_clean", 0.95, 0.22, -0.55, 1.2));
  } else if (type === "gym_rainbow") {
    // 🤸 特需動作訓練島：彩虹階梯與感統平衡木館＋大龍球
    g.add(box(1.9, 0.42, 1.2, "#ef5350", 0, 0.2, 0));
    g.add(box(1.45, 0.42, 0.95, "#ffca28", 0, 0.62, 0));
    g.add(box(1.05, 0.42, 0.75, "#42a5f5", 0, 1.04, 0));
    g.add(ball(0.56, "#ab47bc", 0, 1.88, 0, 10));
    g.add(box(2.2, 0.16, 0.32, "#26a69a", 0, 0.35, 1.15));
  } else if (type === "book_tower") {
    // 📖 語文溝通島：敞開的立體巨型繪本書台＋魔法鵝毛筆尖鐘塔
    g.add(box(1.95, 0.35, 1.35, "#d97706", 0, 0.2, 0));
    const pageL = box(0.88, 0.16, 1.18, "#fffbeb", -0.45, 0.6, 0);
    pageL.rotation.z = 0.22;
    const pageR = box(0.88, 0.16, 1.18, "#fffbeb", 0.45, 0.6, 0);
    pageR.rotation.z = -0.22;
    g.add(pageL, pageR);
    g.add(cyl(0.4, 0.48, 1.95, primaryColor, 0, 0.5, -0.65, 8));
    g.add(cone(0.55, 0.72, trimColor, 0, 2.45, -0.65, 8));
  } else if (type === "clock_pyramid") {
    // 📐 生活數學島：黃金幾何金字塔＋時鐘高塔＋算盤立柱
    g.add(cone(1.2, 1.8, "#f59e0b", -0.48, 0.2, 0.22, 4));
    g.add(box(0.98, 2.3, 0.98, primaryColor, 0.58, 0.2, -0.25));
    g.add(ball(0.36, "#fef08a", 0.58, 1.9, 0.28, 8));
    g.add(cone(0.78, 0.8, trimColor, 0.58, 2.5, -0.25, 4));
  } else if (type === "stadium_torch") {
    // 🏃 健康與體育島：奧運聖火高塔＋紅白PU跑道競技館＋頒獎台
    g.add(cyl(1.75, 1.85, 0.35, "#ef5350", 0, 0.2, 0, 12));
    g.add(cyl(1.3, 1.35, 0.35, "#ffffff", 0, 0.55, 0, 12));
    g.add(cyl(0.35, 0.55, 1.85, "#ffd54f", 0, 0.9, -0.35, 8));
    g.add(cone(0.52, 0.95, "#ff5722", 0, 2.75, -0.35, 7));
    g.add(ball(0.35, "#ffca28", 0.65, 1.15, 0.55, 8));
  } else if (type === "windmill_greenhouse") {
    // 🌱 自然探險島：轉動生態大風車＋翠綠玻璃溫室＋U型大磁鐵
    g.add(box(1.55, 1.05, 1.25, "#a5d6a7", 0.45, 0.2, 0.15));
    g.add(cyl(0.62, 0.62, 1.25, "#81c784", 0.45, 1.25, 0.15, 8));
    g.add(cyl(0.45, 0.62, 2.2, "#ffffff", -0.65, 0.2, -0.35, 8));
    g.add(cone(0.58, 0.65, "#2e7d32", -0.65, 2.4, -0.35, 8));
    const blades = new THREE.Group();
    blades.position.set(-0.65, 1.85, 0.22);
    blades.add(box(1.9, 0.16, 0.05, "#43a047", 0, 0, 0));
    blades.add(box(0.16, 1.9, 0.05, "#43a047", 0, 0, 0));
    g.add(blades);
    spinningMeshes.push(blades);
    g.add(createUnitTopicProp("science_lab", 0.85, 0.22, 0.95, 1.15));
  } else if (type === "gate_town") {
    // 🏮 社會生活島：台灣紅磚古城門樓（燕尾飛簷）＋雙側紅燈籠＋紅綠燈
    g.add(box(0.55, 1.45, 0.95, "#c62828", -0.72, 0.2, 0));
    g.add(box(0.55, 1.45, 0.95, "#c62828", 0.72, 0.2, 0));
    g.add(box(2.15, 0.55, 1.15, "#b71c1c", 0, 1.45, 0));
    const roof = cone(1.65, 0.85, "#ffb300", 0, 2.0, 0, 4);
    roof.rotation.y = Math.PI / 4;
    g.add(roof);
    g.add(ball(0.24, "#ef5350", -0.95, 1.35, 0.6, 8));
    g.add(ball(0.24, "#ef5350", 0.95, 1.35, 0.6, 8));
  } else if (type === "ferris_camp") {
    // 🌏 綜合活動島：彩色摩天輪＋童軍露營三角帳篷與營火
    g.add(box(0.2, 1.9, 0.2, "#475569", -0.35, 0.2, -0.2));
    g.add(box(0.2, 1.9, 0.2, "#475569", 0.35, 0.2, -0.2));
    const wheel = new THREE.Mesh(new THREE.TorusGeometry(1.15, 0.1, 6, 16), mat(primaryColor));
    wheel.position.set(0, 2.05, -0.2);
    g.add(wheel);
    spinningMeshes.push(wheel);
    g.add(cone(0.72, 1.05, "#ffa726", 0.75, 0.2, 0.65, 4));
  } else if (type === "palette_pavilion") {
    // 🎨 藝術創想島：七彩調色盤音樂館＋三支巨型彩色畫筆塔
    g.add(cyl(1.65, 1.75, 0.32, "#ce93d8", 0, 0.2, 0, 12));
    g.add(cyl(0.95, 1.05, 1.1, "#ffffff", -0.25, 0.52, -0.15, 10));
    g.add(ball(0.98, "#8e24aa", -0.25, 1.62, -0.15, 10));
    g.add(createUnitTopicProp("art_palette", 0.85, 0.52, 0.45, 1.45));
  } else {
    // 🎒 生活課程啟蒙島：巨型立體紅黃小書包樂園＋公園溜滑梯
    g.add(box(1.45, 1.55, 1.05, "#d81b60", -0.25, 0.2, 0));
    g.add(box(1.52, 0.75, 1.12, "#ffca28", -0.25, 1.15, 0.05));
    g.add(box(0.95, 0.55, 0.35, "#f06292", -0.25, 0.35, 0.55));
    const slide = box(0.45, 1.45, 0.18, "#29b6f6", 0.95, 0.2, 0.35);
    slide.rotation.z = -0.55;
    g.add(slide);
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

function add3DPin(htmlContent, worldVec, extraClass, onClickFn, isAlwaysVisible = true, attrTag = "") {
  const el = document.createElement("div");
  el.className = "label-pin " + (extraClass || "");
  if (attrTag) el.dataset.attr = attrTag;
  el.innerHTML = htmlContent;
  el.onclick = (e) => {
    e.stopPropagation();
    if (!dragMoved && onClickFn) onClickFn();
  };
  labelsLayer.appendChild(el);
  pinItems.push({ el, pos: worldVec, always: isAlwaysVisible, attrTag });
}

// ==========================================
// 場景一：🌊 10 大領域群島大世界 (World Archipelago)
// ==========================================
function buildWorldArchipelagoScene() {
  clearThreeWorld();

  // 🏫 中央核心：希望學園島（校訓：快樂活潑，自立自強）
  const centerR = 5.2;
  const centerHex = buildHopeSchoolCenter(centerR, 2.35, 0, 0);
  worldGroup.add(centerHex.group);

  // 建造希望學園 3D 建築群
  const hopeMonument = createHopeSchoolMonument(centerHex.topY);
  worldGroup.add(hopeMonument);

  // 希望學園 3D 標籤（點擊聚焦並展開學園導覽）
  add3DPin(
    `<div class="label-pill pill-center pill-hope-school">
      <div class="pin-dot"></div>
      <span class="pin-title">🏫 希望學園（群島核心）</span>
      <span class="pin-badge">校訓：快樂活潑，自立自強</span>
    </div>`,
    new THREE.Vector3(0, centerHex.topY + 4.8, 0),
    "hope-pin",
    () => focusHopeSchool(),
    true
  );

  // 10 座領域島嶼大幅拉開空間距離，依各自專屬地貌 (islandShape) 獨立造型建造
  const coords = [
    { x: -17.5, z: -9.5,  h: 2.15, r: 4.2, bridgeFrom: -1 }, // 0: 特需生活管理島（內環左前・自立生活港灣）
    { x: 0.0,   z: -18.5, h: 2.20, r: 4.2, bridgeFrom: -1 }, // 1: 功能性動作島（內環正北・躍動階梯之巔）
    { x: 17.5,  z: -9.5,  h: 2.15, r: 4.2, bridgeFrom: -1 }, // 2: 語文繪本島（內環右前・故事書卷之森）
    { x: 16.5,  z: 9.5,   h: 2.10, r: 4.2, bridgeFrom: -1 }, // 3: 數學邏輯島（內環右後・幾何時空花園）
    { x: -16.5, z: 9.5,   h: 2.10, r: 4.2, bridgeFrom: -1 }, // 4: 健體活力島（內環左後・聖火守護之島）
    { x: -32.5, z: -1.0,  h: 2.00, r: 4.1, bridgeFrom: 0  }, // 5: 自然探索島（外環極左・四季觀星之島）
    { x: -14.5, z: -25.5, h: 2.05, r: 4.1, bridgeFrom: 1  }, // 6: 社會文化島（外環左北・社區同心市鎮）
    { x: 14.5,  z: -25.5, h: 2.05, r: 4.1, bridgeFrom: 1  }, // 7: 綜合實踐島（外環右北・巧手百寶工坊）
    { x: 32.5,  z: -1.0,  h: 2.00, r: 4.1, bridgeFrom: 2  }, // 8: 藝術人文島（外環極右・彩虹調色海礁）
    { x: 0.0,   z: 20.5,  h: 2.05, r: 4.1, bridgeFrom: 4  }  // 9: 生活啟蒙島（外環正南・萌芽探險新星）
  ];

  // 額外環狀聯絡道路（讓外環與內環形成四通八達的跨海公路網）
  const extraLinks = [
    [4, 5], [2, 7], [0, 6], [3, 8], [3, 9]
  ];

  const subBldOffsets = [
    { dx: -1.95, dz: 1.45 },
    { dx: 1.95,  dz: 1.45 },
    { dx: 0.0,   dz: -1.95 }
  ];

  DOMAINS_DATA.forEach((d, idx) => {
    const c = coords[idx];
    // 依該領域的專屬造型 (d.islandShape) 打造完全獨立的地貌外觀！
    const plat = createDomainIslandPlatform(c.r, c.h, d.groundColor, d.trimColor, "#795548", c.x, c.z, d.islandShape || "hex");
    worldGroup.add(plat.group);

    // 1. 該領域專屬中央地標
    const mainBld = createDomainMonument(d.landmarkType, d.color, d.trimColor, plat.topY);
    mainBld.scale.set(0.76, 0.76, 0.76);
    plat.group.add(mainBld);

    // 2. 依該領域的代表單元 (featuredUnits)，在島上擺放帶有「單元專屬 3D 主題道具」的微縮建築與單元小標籤！
    (d.featuredUnits || []).slice(0, 3).forEach((fu, fIdx) => {
      const off = subBldOffsets[fIdx];
      const roofCol = fIdx % 2 === 0 ? d.color : d.trimColor;
      const bld = createUnitBuilding(off.dx, plat.topY, off.dz, idx + fIdx, roofCol, "#ffffff", fu.propType);
      bld.scale.set(0.66, 0.66, 0.66);
      plat.group.add(bld);

      // 代表單元與屬性小膠囊（預設顯示前 2 個代表單元，按右下 🏷️ 可全開）
      add3DPin(
        `<div class="label-pill pill-world-sub" style="border-color:${d.trimColor};">
          <span>${fu.topicEmoji}</span>
          <span class="pin-title">${fu.name}</span>
          <span class="pin-attr-tag">${fu.attrTag}</span>
        </div>`,
        new THREE.Vector3(c.x + off.dx, plat.topY + 1.65, c.z + off.dz),
        "world-sub-pin",
        () => openUnitModal(fu.uid),
        fIdx === 0,
        fu.attrTag
      );
    });

    // 3. 該領域專屬植被樹種與吉祥物
    plat.group.add(createDomainFoliage(d.id, -2.35, plat.topY, -1.45, 0.95, 0));
    plat.group.add(createDomainFoliage(d.id, 2.35, plat.topY, -1.4, 0.9, 1));
    plat.group.add(createMascot(0.0, plat.topY, 2.55, d.color, "#ffd54f"));
    plat.group.add(createStreetLamp(-1.25, plat.topY, 2.4));
    plat.group.add(createDaisyCluster(-2.7, plat.topY, 0.8, 4, 0.45));
    plat.group.add(createDaisyCluster(2.6, plat.topY, 0.9, 4, 0.45));
    plat.group.add(createPebbleScatter(0.0, plat.topY, 1.85, 5, 0.45));

    // 主跨海連接道路橋樑（內環連希望學園島，外環連內環島）
    if (c.bridgeFrom === -1) {
      worldGroup.add(createRoadBridge(0, 0, centerR, c.x, c.z, c.r, 1.95));
    } else {
      const p = coords[c.bridgeFrom];
      worldGroup.add(createRoadBridge(p.x, p.z, p.r, c.x, c.z, c.r, 1.9));
    }

    // 領域島主標題膠囊（附該領域專屬稱號與屬性摘要）
    const topAttrs = (d.attrSummary || []).slice(0, 2).map(a => a.tag).join("・");
    add3DPin(
      `<div class="label-pill" style="border-color:${d.trimColor};">
        <span style="font-size:18px;">${d.icon}</span>
        <span class="pin-title">${d.islandName}</span>
        <span class="pin-attr-tag">${d.islandTitle || topAttrs}</span>
        <span class="pin-badge">${d.ownCount}站</span>
      </div>`,
      new THREE.Vector3(c.x, plat.topY + 3.05, c.z),
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
// 場景二：🏝️ 單一領域獨立 3D 導覽島（依領域切換專屬聚落名稱、專屬地貌色系、30 單元專屬 3D 道具與屬性標籤）
// ==========================================
function buildDomainIslandScene(domainId) {
  clearThreeWorld();
  const d = DOMAIN_MAP[domainId];
  if (!d) return;

  // 1. 中央領域主題廣場 (獨立中央島，擺放該領域專屬地標與代表屬性微縮道具)
  const centerR = 4.5;
  const centerHex = createHexPlatform(centerR, 2.25, d.groundColor, d.trimColor, "#795548", 0, 0);
  worldGroup.add(centerHex.group);
  centerHex.group.add(box(centerR * 1.5, 0.06, 0.8, "#f5ebe0", 0, centerHex.topY, 0));
  centerHex.group.add(box(0.8, 0.06, centerR * 1.5, "#f5ebe0", 0, centerHex.topY, 0));
  worldGroup.add(createDomainMonument(d.landmarkType, d.color, d.trimColor, centerHex.topY));
  worldGroup.add(createDomainFoliage(d.id, -2.5, centerHex.topY, -1.6, 1.0, 0));
  worldGroup.add(createDomainFoliage(d.id, 2.5, centerHex.topY, -1.6, 1.0, 1));
  worldGroup.add(createBench(-1.8, centerHex.topY, 1.65, 0.5));
  worldGroup.add(createBench(1.8, centerHex.topY, 1.65, -0.5));
  worldGroup.add(createStreetLamp(-2.2, centerHex.topY, 0.25));
  worldGroup.add(createStreetLamp(2.2, centerHex.topY, 0.25));
  worldGroup.add(createMascot(0, centerHex.topY, 2.45, d.color, "#fde047"));
  worldGroup.add(createDaisyCluster(-2.8, centerHex.topY, 1.2, 4, 0.45));
  worldGroup.add(createDaisyCluster(2.8, centerHex.topY, 1.2, 4, 0.45));
  worldGroup.add(createPebbleScatter(0, centerHex.topY, 1.4, 6, 0.5));

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

  const pal1 = (d.stagePalettes && d.stagePalettes["1"]) || { top: "#e8f5e9", trim: "#43a047", roofA: "#ef5350", roofB: "#66bb6a" };
  const pal2 = (d.stagePalettes && d.stagePalettes["2"]) || { top: "#e3f2fd", trim: "#1e88e5", roofA: "#1e88e5", roofB: "#ffa726" };
  const pal3 = (d.stagePalettes && d.stagePalettes["3"]) || { top: "#fff3e0", trim: "#fb8c00", roofA: "#ab47bc", roofB: "#fb8c00" };

  // 三個學習階段分島配置（自動套用該領域專屬的階段聚落名稱與主題色系）
  const stageConfigs = [
    {
      stage: "1",
      title: (d.stageTitles && d.stageTitles["1"]) || "🌱 第一階段：啟蒙村",
      topColor: pal1.top,
      trimColor: pal1.trim,
      roofA: pal1.roofA,
      roofB: pal1.roofB,
      hexA: { x: -16.5, z: -7.5, r: 4.6, h: 2.30 },
      hexB: { x: -30.5, z: -2.0, r: 4.6, h: 2.45 },
      hdrPos: new THREE.Vector3(-23.5, 5.8, -6.2),
      hdrClass: "pill-s1-hdr"
    },
    {
      stage: "2",
      title: (d.stageTitles && d.stageTitles["2"]) || "🌿 第二階段：實踐鎮",
      topColor: pal2.top,
      trimColor: pal2.trim,
      roofA: pal2.roofA,
      roofB: pal2.roofB,
      hexA: { x: 16.5, z: -7.5, r: 4.6, h: 2.30 },
      hexB: { x: 30.5, z: -2.0, r: 4.6, h: 2.45 },
      hdrPos: new THREE.Vector3(23.5, 5.8, -6.2),
      hdrClass: "pill-s2-hdr"
    },
    {
      stage: "3",
      title: (d.stageTitles && d.stageTitles["3"]) || "🌳 第三階段：進階城",
      topColor: pal3.top,
      trimColor: pal3.trim,
      roofA: pal3.roofA,
      roofB: pal3.roofB,
      hexA: { x: -10.5, z: 16.5, r: 4.6, h: 2.10 },
      hexB: { x: 10.5,  z: 16.5, r: 4.6, h: 2.20 },
      hdrPos: new THREE.Vector3(0, 5.5, 19.5),
      hdrClass: "pill-s3-hdr"
    }
  ];

  // 每個六角島上的 5 個單元建築位置（隨島嶼放大與道路鋪設，拉開建築彼此間距）
  const localSlots = [
    { dx: -2.15, dz: -1.80 },
    { dx: 2.15,  dz: -1.80 },
    { dx: 0.0,   dz: 0.05 },
    { dx: -2.15, dz: 1.90 },
    { dx: 2.15,  dz: 1.90 }
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

    // 擺放該階段的 10 個單元立體建築（每棟建築皆配備該單元專屬的 3D 主題微縮道具 u.propType 與單元屬性徽章！）
    units.forEach((u, idx) => {
      const isSecondHalf = idx >= 5;
      const hex = isSecondHalf ? sc.hexB : sc.hexA;
      const topY = isSecondHalf ? pB.topY : pA.topY;
      const slot = localSlots[idx % 5];
      const wx = hex.x + slot.dx;
      const wz = hex.z + slot.dz;

      const roofColor = isSecondHalf ? sc.roofB : sc.roofA;
      const bld = createUnitBuilding(wx, topY, wz, idx + u.uid, roofColor, "#ffffff", u.propType);
      bld.scale.set(0.74, 0.74, 0.74);
      worldGroup.add(bld);

      // 全島總覽時預設顯示每學期前 2 個代表單元標籤；點進該階段、點選屬性篩選或開啟「全部標籤」時自動展開
      const isFeatured = (idx % 5 === 0) || (idx % 5 === 1);
      add3DPin(
        `<div class="label-pill">
          <span>${u.topicEmoji || "🏠"}</span>
          <span class="pin-title">${u.name}</span>
          <span class="pin-attr-tag">${u.attrTag || ""}</span>
          <span class="pin-badge">${u.sem}U${u.u}</span>
        </div>`,
        new THREE.Vector3(wx, topY + 2.0, wz),
        `stage-${sc.stage} unit-pin`,
        () => openUnitModal(u.uid),
        isFeatured,
        u.attrTag || ""
      );
    });

    // 聚落裝飾（使用該領域專屬植被樹種、街燈、小吉祥物）
    worldGroup.add(createDomainFoliage(d.id, sc.hexA.x - 3.2, pA.topY, sc.hexA.z, 0.92, 0));
    worldGroup.add(createDomainFoliage(d.id, sc.hexB.x + 3.2, pB.topY, sc.hexB.z - 0.5, 0.96, 1));
    worldGroup.add(createMascot(sc.hexA.x, pA.topY, sc.hexA.z + 2.9, sc.trimColor, "#ffd54f"));
    worldGroup.add(createStreetLamp(sc.hexB.x, pB.topY, sc.hexB.z - 2.9));
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
// 導覽切換與 UI 連動（含領域專屬屬性篩選器）
// ==========================================
function renderDomainBar() {
  const bar = document.getElementById("domain-bar");
  let html = `
    <button class="domain-chip ${currentMode === 'world' ? 'active' : ''}" onclick="focusHopeSchool()" style="border-color:#f59e0b;">
      <span>🏫</span>
      <span>希望學園（群島核心）</span>
      <span class="chip-count" style="background:#f59e0b;color:#fff;">校訓：自立自強</span>
    </button>
    <button class="domain-chip" onclick="enterWorldView()">
      <span>🌊</span>
      <span>10 大領域全島</span>
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

function renderBannerAttrBar() {
  const attrBar = document.getElementById("banner-attrs");
  if (!attrBar) return;
  if (currentMode === "world") {
    attrBar.innerHTML = `
      <button class="attr-chip ${showAll30Pins ? 'active' : ''}" onclick="toggleShowAllPins()">
        🏷️ ${showAll30Pins ? '已展開各島代表單元與屬性' : '點此展開 10 島代表單元標籤'}
      </button>
    `;
    return;
  }
  const d = DOMAIN_MAP[currentMode];
  if (!d || !d.attrSummary) {
    attrBar.innerHTML = "";
    return;
  }
  let html = `
    <button class="attr-chip ${currentAttrFilter === 'all' ? 'active' : ''}" onclick="selectAttrFilter('all')">
      ✨ 全部屬性 (${(d.stages["1"]||[]).length + (d.stages["2"]||[]).length + (d.stages["3"]||[]).length})
    </button>
  `;
  d.attrSummary.forEach(a => {
    const active = currentAttrFilter === a.tag ? "active" : "";
    html += `
      <button class="attr-chip ${active}" onclick="selectAttrFilter('${a.tag}')">
        <span>${a.emoji}</span>
        <span>${a.tag} (${a.count})</span>
      </button>
    `;
  });
  attrBar.innerHTML = html;
}

function selectAttrFilter(tag) {
  currentAttrFilter = tag;
  renderBannerAttrBar();
  renderQuickDock();
}

function enterWorldView(pushHash = true) {
  currentMode = "world";
  currentStageFilter = "all";
  currentAttrFilter = "all";
  if (pushHash) history.replaceState(null, "", "#world");

  document.getElementById("btn-back-world").style.display = "none";
  document.getElementById("stage-switcher").style.display = "none";
  document.getElementById("unit-dock").classList.remove("visible");

  document.getElementById("top-logo").innerText = "🏝️";
  document.getElementById("top-title").innerText = "高雄特教國小部｜3D 領域群島總入口";
  document.getElementById("top-subtitle").innerText = "10 大領域島嶼 × 三個學習階段 × 240 個互動單元";

  document.getElementById("banner-title").innerText = "🌊 特教學習大世界（10 大領域群島）";
  document.getElementById("banner-desc").innerText = "每座島嶼皆有領域專屬地標、植被與代表單元小屋！點擊任一島嶼進入三個學習階段。";
  document.getElementById("banner-note").style.display = "none";

  renderDomainBar();
  renderBannerAttrBar();
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
  currentAttrFilter = "all";
  if (pushHash) history.replaceState(null, "", `#domain=${domainId}`);

  document.getElementById("btn-back-world").style.display = "inline-flex";
  document.getElementById("stage-switcher").style.display = "flex";
  document.getElementById("unit-dock").classList.add("visible");

  document.getElementById("top-logo").innerText = d.icon;
  document.getElementById("top-title").innerText = `${d.islandName}｜三個學習階段導覽`;
  document.getElementById("top-subtitle").innerText = d.themeDesc;

  document.getElementById("banner-title").innerText = `${d.icon} ${d.islandName}`;
  document.getElementById("banner-desc").innerText = d.themeDesc + "（可點下方屬性切換島上單元標籤）：";
  const noteEl = document.getElementById("banner-note");
  if (d.stage1Note) {
    noteEl.innerText = "💡 " + d.stage1Note;
    noteEl.style.display = "block";
  } else {
    noteEl.style.display = "none";
  }

  renderDomainBar();
  renderBannerAttrBar();
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
    dockTitle.innerText = `📍 ${d.islandName}・全部階段單元${currentAttrFilter !== 'all' ? '（屬性：' + currentAttrFilter + '）' : ''}：`;
  } else {
    units = d.stages[currentStageFilter] || [];
    const stNames = d.stageTitles || { "1": "🌱 第一階段", "2": "🌿 第二階段", "3": "🌳 第三階段" };
    dockTitle.innerText = `📍 ${stNames[currentStageFilter]} 單元清單：`;
  }

  if (currentAttrFilter !== "all") {
    units = units.filter(u => u.attrTag === currentAttrFilter);
  }
  dockCount.innerText = `共 ${units.length} 單元`;

  dockList.innerHTML = units.map(u => `
    <button class="dock-unit-btn s${u.stage}" onclick="openUnitModal(${u.uid})">
      <span>${u.topicEmoji || "🏠"}</span>
      <span style="color:var(--text-muted);font-size:12px;">${u.sem}U${u.u}</span>
      <span>${u.name}</span>
      <span class="pin-attr-tag">${u.attrTag || ""}</span>
    </button>
  `).join("");
}

function toggleShowAllPins() {
  showAll30Pins = !showAll30Pins;
  document.getElementById("btn-all-pins").classList.toggle("active", showAll30Pins);
  renderBannerAttrBar();
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

  const attrBadge = document.getElementById("m-attr-badge");
  if (attrBadge) {
    attrBadge.innerText = `${u.topicEmoji || "🏷️"} ${u.attrTag || "主題單元"}`;
  }

  document.getElementById("m-title").innerText = `${u.topicEmoji || ""} ${u.name}`;

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
    // 1. 群島大世界內：代表單元與屬性小膠囊切換邏輯
    if (currentMode === "world" && item.el.classList.contains("world-sub-pin")) {
      if (!item.always && !showAll30Pins) {
        item.el.style.display = "none";
        return;
      }
      item.el.style.opacity = "1";
    }

    // 2. 單一領域島內：根據階段篩選與「單元屬性篩選 (currentAttrFilter)」決定顯示邏輯
    if (currentMode !== "world" && item.el.classList.contains("unit-pin")) {
      const belongStage = item.el.classList.contains("stage-1") ? "1" :
                          item.el.classList.contains("stage-2") ? "2" : "3";

      if (currentAttrFilter !== "all") {
        // 若使用者點選了特定屬性（例如「🦷 潔牙洗漱」或「👕 穿脫儀容」），立即展開所有符合該屬性的單元標籤！
        if (item.attrTag !== currentAttrFilter) {
          item.el.style.display = "none";
          return;
        }
        if (currentStageFilter !== "all" && belongStage !== currentStageFilter) {
          item.el.style.display = "none";
          return;
        }
        item.el.style.opacity = "1";
      } else if (currentStageFilter === "all") {
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


// ================= 希望學園彈窗與白鯨巡航導覽系統 =================
function openHopeSchoolModal() {
  const m = document.getElementById("modal-hope-school");
  if (m) m.classList.add("visible");
}

function closeHopeSchoolModal(event) {
  if (event && event.target && !event.target.classList.contains("modal-backdrop") && !event.target.classList.contains("modal-close-btn") && !event.target.classList.contains("hope-btn-start")) {
    return;
  }
  const m = document.getElementById("modal-hope-school");
  if (m) m.classList.remove("visible");
}

function focusHopeSchool() {
  if (currentMode !== "world") {
    enterWorldView(false);
  }
  stopWhaleTour();
  targetLook.set(0, 1.8, 0);
  spherical.radius = 24;
  spherical.theta = 0.05;
  spherical.phi = 1.05;
  openHopeSchoolModal();
}

let tourActive = false;
let tourStep = 0;

const TOUR_STOPS = [
  {
    id: "hope_school",
    title: "🏫 第一站：希望學園（群島核心）",
    desc: "歡迎來到希望學園！這裡是大家上課與學習成長的基地營。校訓是「快樂活潑，自立自強」。前庭設有戶外研討木書桌、發光筆電與繪本風師生親切研讀，跟著白鯨領航員準備出發上課囉！",
    lookAt: [0, 1.8, 0],
    spherical: { radius: 24, theta: 0.05, phi: 1.05 },
    domainId: null
  },
  {
    id: "selfcare",
    title: "🏠 第二站：特需生活管理島（自立生活港灣）",
    desc: "在紅白暖光燈塔與金黃投射光束下，學會自己穿鞋襪、刷牙洗臉、打掃環境，把每一天過得神氣又乾淨！",
    lookAt: [-17.5, 2.1, -9.5],
    spherical: { radius: 18, theta: -0.65, phi: 1.02 },
    domainId: "selfcare"
  },
  {
    id: "motor",
    title: "🤸 第三站：特需動作訓練島（躍動階梯之巔）",
    desc: "踩上五彩平衡木、走過階梯跳石，小手抓握有力、雙腳踩得穩健，每一步都充滿自立力量！",
    lookAt: [0, 2.1, -18.5],
    spherical: { radius: 18, theta: 0.05, phi: 1.02 },
    domainId: "motor"
  },
  {
    id: "chinese",
    title: "📖 第四站：語文繪本島（故事書卷之森）",
    desc: "翻開海面上浮現的巨型繪本書卷，在魔法羽毛筆鐘樓下聽故事、讀句子，勇敢說出心裡話！",
    lookAt: [17.5, 2.1, -9.5],
    spherical: { radius: 18, theta: 0.65, phi: 1.02 },
    domainId: "chinese"
  },
  {
    id: "math",
    title: "📐 第五站：生活數學島（幾何時空花園）",
    desc: "在幾何時鐘高塔與天秤金幣前，數數量、比大小、看時間、學購物，生活有條理又有秩序！",
    lookAt: [16.5, 2.1, 9.5],
    spherical: { radius: 18, theta: 1.15, phi: 1.02 },
    domainId: "math"
  },
  {
    id: "pe",
    title: "🏃 第六站：健體活力島（聖火守護之島）",
    desc: "沿著運動場跑道奔跑，聖火高塔指引方向，認識身體、看懂紅綠燈過馬路，健康又有活力！",
    lookAt: [-16.5, 2.1, 9.5],
    spherical: { radius: 18, theta: -1.15, phi: 1.02 },
    domainId: "pe"
  },
  {
    id: "nature",
    title: "🌱 第七站：自然探險島（四季觀星之島）",
    desc: "轉動生態大風車、探訪綠意溫室花房，看四季天氣、摸摸花草小動物，大自然是神奇的好朋友！",
    lookAt: [-32.5, 2.0, -1.0],
    spherical: { radius: 18, theta: -1.45, phi: 1.02 },
    domainId: "nature"
  },
  {
    id: "society",
    title: "🏮 第八站：社會生活島（社區同心市鎮）",
    desc: "繞過世界地球儀噴泉、搭乘溫馨小公車，認識鄰舍、遵守班規與交通禮貌，大家同心快樂生活！",
    lookAt: [-14.5, 2.0, -25.5],
    spherical: { radius: 18, theta: -0.45, phi: 1.02 },
    domainId: "society"
  },
  {
    id: "life",
    title: "🌏 第九站：綜合活動島（巧手百寶工坊）",
    desc: "圍在童軍營火帳篷旁，一起玩桌遊、輪流排隊、動手串珠與垃圾分類，學習當生活小創客！",
    lookAt: [14.5, 2.0, -25.5],
    spherical: { radius: 18, theta: 0.45, phi: 1.02 },
    domainId: "life"
  },
  {
    id: "arts",
    title: "🎨 第十站：藝術創想島（彩虹調色海礁）",
    desc: "巨型木畫架立在調色盤天池邊，踏上琴鍵階梯步道，用繽紛色彩與旋律唱出快樂心情！",
    lookAt: [32.5, 2.0, -1.0],
    spherical: { radius: 18, theta: 1.45, phi: 1.02 },
    domainId: "arts"
  },
  {
    id: "daily",
    title: "🎒 第十一站：生活課程島（萌芽探險新星）",
    desc: "揹起立體彩色小書包、溜下向日葵滑梯，不怕生、常微笑，國小新生活充滿奇妙與樂趣！",
    lookAt: [0, 2.0, 20.5],
    spherical: { radius: 18, theta: 3.14, phi: 1.02 },
    domainId: "daily"
  }
];

function startWhaleGuidedTour(step = 0) {
  if (currentMode !== "world") {
    enterWorldView(false);
  }
  tourActive = true;
  tourStep = step;
  updateTourStep();
}

function updateTourStep() {
  const stop = TOUR_STOPS[tourStep];
  if (!stop) return;

  targetLook.set(stop.lookAt[0], stop.lookAt[1], stop.lookAt[2]);
  spherical.radius = stop.spherical.radius;
  spherical.theta = stop.spherical.theta;
  spherical.phi = stop.spherical.phi;

  const bar = document.getElementById("tour-bar");
  if (bar) {
    bar.classList.add("visible");
    document.getElementById("tour-step-tag").innerText = `站點 ${tourStep + 1} / ${TOUR_STOPS.length}`;
    document.getElementById("tour-title").innerText = stop.title;
    document.getElementById("tour-desc").innerText = stop.desc;
    const btnGo = document.getElementById("tour-btn-go");
    if (btnGo) {
      btnGo.style.display = stop.domainId ? "inline-flex" : "none";
      btnGo.innerText = stop.domainId ? `🚀 進入${stop.title.split("（")[0].replace(/.*站：/, "")}上課` : "";
    }
  }
}

function nextTourStep() {
  tourStep = (tourStep + 1) % TOUR_STOPS.length;
  updateTourStep();
}

function prevTourStep() {
  tourStep = (tourStep - 1 + TOUR_STOPS.length) % TOUR_STOPS.length;
  updateTourStep();
}

function stopWhaleTour() {
  tourActive = false;
  const bar = document.getElementById("tour-bar");
  if (bar) bar.classList.remove("visible");
  resetCamera();
}

function visitCurrentTourIsland() {
  const stop = TOUR_STOPS[tourStep];
  if (stop && stop.domainId) {
    stopWhaleTour();
    enterDomainIsland(stop.domainId);
  }
}

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
