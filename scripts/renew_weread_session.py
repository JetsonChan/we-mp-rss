from datetime import datetime
from pathlib import Path

import requests
import yaml

path = Path("data/wx.lic")
config = yaml.safe_load(path.read_text())
account = config["weread_data"]["accounts"][0]
cookies = dict(part.strip().split("=", 1) for part in account["cookie"].split(";") if "=" in part)
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://weread.qq.com",
    "Referer": "https://weread.qq.com/",
    "Accept": "application/json",
})
for name, value in cookies.items():
    session.cookies.set(name, value, domain="weread.qq.com", path="/")

response = session.post(
    "https://weread.qq.com/web/login/renewal",
    json={"rq": "%2Fweb%2Fbook%2Fread", "ql": False},
    timeout=20,
)
response.raise_for_status()
result = response.json()
if result.get("succ") != 1:
    raise RuntimeError(f"微信读书续期失败：{result.get('errCode')} {result.get('errMsg')}")

cookies.update({cookie.name: cookie.value for cookie in response.cookies})
cookie_header = "; ".join(f"{name}={value}" for name, value in cookies.items())
validation = requests.get(
    "https://weread.qq.com/web/shelf/sync",
    params={"userVid": "", "synckey": 0},
    headers={**session.headers, "Cookie": cookie_header},
    timeout=20,
)
validation.raise_for_status()
result = validation.json()
if "books" not in result:
    raise RuntimeError(f"微信读书续期验证失败：{result.get('errCode')} {result.get('errMsg')}")

account["cookie"] = cookie_header
temporary = path.with_suffix(".tmp")
temporary.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
temporary.chmod(0o600)
temporary.replace(path)
print(f"{datetime.now().isoformat()} 微信读书续期成功，已保存并验证新凭证")
