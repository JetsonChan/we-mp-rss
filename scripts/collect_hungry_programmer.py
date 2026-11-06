import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.wx.model.weread_mp import MpsWereadMP
from jobs.article import UpdateArticle

collector = MpsWereadMP()
collector.get_Articles(
    Mps_id="MP_WXS_3228611596",
    Mps_title="饥饿程序员",
    CallBack=UpdateArticle,
    Gather_Content=True,
)
print(f"{datetime.now().isoformat()} 饥饿程序员采集完成，新增 {collector.all_count()} 篇")
