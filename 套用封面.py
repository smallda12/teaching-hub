# -*- coding: utf-8 -*-
r"""把 `_covers_原圖\` 逐張校對通過的封面，壓成網頁用的 `covers\*.webp`。

用法：
    python 套用封面.py

🛑 `_covers_原圖\` 是中繼檔（1536×1024 PNG，每張 2.4 MB），**不進版控**；
   進 repo 的是壓過的 webp（每張約 30～60 KB）。

📐 卡片在桌機三欄時寬 371px；輸出 760px 寬（約 2 倍）供高解析螢幕用，
   高度固定 3:2。
"""
import glob
import os
import re

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "_covers_原圖")
DST = os.path.join(ROOT, "covers")

寬 = 760
高 = 寬 * 2 // 3          # 3:2


def main():
    if not os.path.isdir(SRC):
        raise SystemExit("🛑 找不到 %s，先跑 生成封面.py" % SRC)
    os.makedirs(DST, exist_ok=True)

    # 同一個代號重生多次時取最新的那一張（檔名帶時間戳）
    最新 = {}
    for f in sorted(glob.glob(os.path.join(SRC, "*.png"))):
        m = re.match(r"([a-z]+\d{2})_\d{8}_\d{6}\.png$", os.path.basename(f))
        if m:
            最新[m.group(1)] = f
    assert 最新, "🛑 `_covers_原圖\\` 裡沒有符合命名的封面（<代號><序號>_<時間戳>.png）"

    共 = 0
    for 代號, f in sorted(最新.items()):
        im = Image.open(f).convert("RGB")
        assert im.size == (1536, 1024), "%s 尺寸是 %s，應為 (1536, 1024)" % (代號, im.size)
        im = im.resize((寬, 高), Image.LANCZOS)
        out = os.path.join(DST, 代號 + ".webp")
        im.save(out, "WEBP", quality=82, method=6)
        共 += os.path.getsize(out)
        print("   ✅ %s.webp  %.0f KB  ←  %s"
              % (代號, os.path.getsize(out) / 1024, os.path.basename(f)))

    # 🛑 印的是數出來的值
    n = len(glob.glob(os.path.join(DST, "*.webp")))
    print("\n✅ covers\\ 共 %d 張，合計 %.0f KB（%d×%d）" % (n, 共 / 1024, 寬, 高))
    print("下一步：python 產出總入口.py  → 會把有封面的單元接上去")


if __name__ == "__main__":
    main()
