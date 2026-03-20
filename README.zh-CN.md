# baidu-moonshad-py

[![CI](https://github.com/PlumBlossomMaid/baidu-moonshad-py/actions/workflows/ci.yml/badge.svg)](https://github.com/PlumBlossomMaid/baidu-moonshad-py/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/PlumBlossomMaid/baidu-moonshad-py.svg)](https://github.com/PlumBlossomMaid/baidu-moonshad-py/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

百度 AI Studio / 百度登录 签名生成模块。

100% 对齐百度官方 `moonshad.js` V3 算法。生成登录请求所需的 `sig` 和 `shaOne` 参数。

> 📖 **语言**: [English](README.md) | [繁體中文](README.zh-TW.md)

## 特性

- ✅ 100% 对齐 `moonshad.js` V3 算法
- ✅ 5 个版本密钥，按日期轮换
- ✅ 纯 Python 实现，无需浏览器
- ✅ 17 个单元测试全部通过
- ✅ MIT 许可证

## 安装

```bash
pip install baidu-moonshad-py
```

或直接从 GitHub 安装：

```bash
pip install git+https://github.com/PlumBlossomMaid/baidu-moonshad-py.git
```

## 使用示例

```python
from moonshad import MoonshadSigner

# 使用实际屏幕分辨率创建签名器
signer = MoonshadSigner(screen_width=1080, screen_height=1920)

# 生成登录签名
result = signer.generate_login_sign(
    gid="你的设备标识",
    token="从服务器获取的临时凭证",
    username="用户名",
    password="加密后的密码",
    # ... 其他参数如 ds, tk, dv 等
)

print(f"sig: {result['sig']}")
print(f"shaOne: {result['shaOne']}")
print(f"tt: {result['tt']}")
print(f"time: {result['time']}")
```

## API 参考

### `MoonshadSigner(screen_width, screen_height)`

创建签名器实例。

- `screen_width`: 设备屏幕宽度（像素）
- `screen_height`: 设备屏幕高度（像素）

### `generate_login_sign(gid, token, **kwargs)`

生成登录签名参数。

- `gid`: 设备标识
- `token`: 临时凭证（首次登录为空）
- `**kwargs`: 其他参数（用户名、密码、ds、tk 等）

返回字典包含：
- `sig`: 签名值
- `shaOne`: shaOne 值
- `tt`: 13 位毫秒时间戳
- `time`: 10 位秒时间戳
- `alg`: 算法版本（"v3"）
- `elapsed`: 耗时（始终为 0）

### `generate_sig(params)`

从参数字典生成 `sig`。

### `generate_shaone(timestamp_ms)`

从时间戳生成 `shaOne`。

## 算法参考

- [moonshad.js](https://wappass.baidu.com/static/waplib/moonshad.js) - 百度官方签名脚本
- [uni_wrapper.js](https://passport.baidu.com/passApi/js/uni_wrapper.js) - 百度登录包装器
- [逆向分析博客](https://mikublog.com/tech/2488) - 分析参考

## 运行测试

```bash
# 克隆仓库
git clone https://github.com/PlumBlossomMaid/baidu-moonshad-py.git
cd baidu-moonshad-py

# 安装依赖
pip install -e .[test]

# 运行测试
pytest test_moonshad.py -v
```

## 许可证

MIT 许可证

## 作者

PlumBlossomMaid
