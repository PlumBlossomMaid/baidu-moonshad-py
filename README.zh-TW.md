# baidu-moonshad-py

[![CI](https://github.com/PlumBlossomMaid/baidu-moonshad-py/actions/workflows/ci.yml/badge.svg)](https://github.com/PlumBlossomMaid/baidu-moonshad-py/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/PlumBlossomMaid/baidu-moonshad-py.svg)](https://github.com/PlumBlossomMaid/baidu-moonshad-py/blob/master/LICENSE)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

百度 AI Studio / 百度登入 簽名生成模組。

100% 對齊百度官方 `moonshad.js` V3 演算法。生成登入請求所需的 `sig` 和 `shaOne` 參數。

> 📖 **語言**: [English](README.md) | [简体中文](README.zh-CN.md)

## 特性

- ✅ 100% 對齊 `moonshad.js` V3 演算法
- ✅ 5 個版本金鑰，按日期輪換
- ✅ 純 Python 實作，無需瀏覽器
- ✅ 17 個單元測試全部通過
- ✅ MIT 授權條款

## 安裝

```bash
pip install git+https://github.com/PlumBlossomMaid/baidu-moonshad-py.git
```

## 使用範例

```python
from moonshad import MoonshadSigner

# 使用實際螢幕解析度建立簽名器
signer = MoonshadSigner(screen_width=1080, screen_height=1920)

# 產生登入簽名
result = signer.generate_login_sign(
    gid="你的裝置識別碼",
    token="從伺服器取得的臨時憑證",
    username="使用者名稱",
    password="加密後的密碼",
    # ... 其他參數如 ds, tk, dv 等
)

print(f"sig: {result['sig']}")
print(f"shaOne: {result['shaOne']}")
print(f"tt: {result['tt']}")
print(f"time: {result['time']}")
```

## API 參考

### `MoonshadSigner(screen_width, screen_height)`

建立簽名器實例。

- `screen_width`: 裝置螢幕寬度（像素）
- `screen_height`: 裝置螢幕高度（像素）

### `generate_login_sign(gid, token, **kwargs)`

產生登入簽名參數。

- `gid`: 裝置識別碼
- `token`: 臨時憑證（首次登入為空）
- `**kwargs`: 其他參數（使用者名稱、密碼、ds、tk 等）

回傳字典包含：
- `sig`: 簽名值
- `shaOne`: shaOne 值
- `tt`: 13 位毫秒時間戳
- `time`: 10 位秒時間戳
- `alg`: 演算法版本（"v3"）
- `elapsed`: 耗時（始終為 0）

### `generate_sig(params)`

從參數字典產生 `sig`。

### `generate_shaone(timestamp_ms)`

從時間戳產生 `shaOne`。

## 演算法參考

- [moonshad.js](https://wappass.baidu.com/static/waplib/moonshad.js) - 百度官方簽名腳本
- [uni_wrapper.js](https://passport.baidu.com/passApi/js/uni_wrapper.js) - 百度登入包裝器
- [逆向分析部落格](https://mikublog.com/tech/2488) - 分析參考

## 執行測試

```bash
# 複製倉庫
git clone https://github.com/PlumBlossomMaid/baidu-moonshad-py.git
cd baidu-moonshad-py

# 安裝依賴
pip install -e .[test]

# 執行測試
pytest test_moonshad.py -v
```

## 授權條款

MIT 授權條款

## 作者

PlumBlossomMaid
