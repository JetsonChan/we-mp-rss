import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.wx.model.weread_mp import MpsWereadMP
from jobs.article import UpdateArticle

for account_id, title in [
    ("MP_WXS_3228611596", "饥饿程序员"),
    ("MP_WXS_3693376220", "斑点狗AI掘金日记"),
]:
    collector = MpsWereadMP()
    collector.get_Articles(
        Mps_id=account_id,
        Mps_title=title,
        CallBack=UpdateArticle,
        Gather_Content=True,
    )
    print(f"{datetime.now().isoformat()} {title}采集完成，新增 {collector.all_count()} 篇")
