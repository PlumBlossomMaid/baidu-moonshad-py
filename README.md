# baidu-moonshad-py

[![CI](https://github.com/PlumBlossomMaid/baidu-moonshad-py/actions/workflows/ci.yml/badge.svg)](https://github.com/PlumBlossomMaid/baidu-moonshad-py/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/PlumBlossomMaid/baidu-moonshad-py.svg)](https://github.com/PlumBlossomMaid/baidu-moonshad-py/blob/master/LICENSE)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Baidu AI Studio / Baidu Login Signature Generator.

100% aligned with Baidu's official `moonshad.js` V3 algorithm. Generates `sig` and `shaOne` parameters for login requests.

> 📖 **Languages**: [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

## Features

- ✅ 100% aligned with `moonshad.js` V3
- ✅ 5 version keys rotation (daily)
- ✅ Pure Python implementation, no browser required
- ✅ 17 unit tests passed
- ✅ MIT License

## Installation

```bash
pip install baidu-moonshad-py
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/PlumBlossomMaid/baidu-moonshad-py.git
```

## Usage

```python
from moonshad import MoonshadSigner

# Create signer with actual screen resolution
signer = MoonshadSigner(screen_width=1080, screen_height=1920)

# Generate signature for login
result = signer.generate_login_sign(
    gid="YOUR_DEVICE_GID",
    token="TOKEN_FROM_SERVER",
    username="your_username",
    password="encrypted_password",
    # ... other parameters like ds, tk, dv, etc.
)

print(f"sig: {result['sig']}")
print(f"shaOne: {result['shaOne']}")
print(f"tt: {result['tt']}")
print(f"time: {result['time']}")
```

## API Reference

### `MoonshadSigner(screen_width, screen_height)`

Create a signer instance.

- `screen_width`: Device screen width in pixels
- `screen_height`: Device screen height in pixels

### `generate_login_sign(gid, token, **kwargs)`

Generate signature parameters for login.

- `gid`: Device identifier
- `token`: Temporary credential (empty for first login)
- `**kwargs`: Additional parameters (username, password, ds, tk, etc.)

Returns a dict with:
- `sig`: Signature value
- `shaOne`: shaOne value
- `tt`: 13-digit millisecond timestamp
- `time`: 10-digit second timestamp
- `alg`: Algorithm version ("v3")
- `elapsed`: Elapsed time (always 0)

### `generate_sig(params)`

Generate `sig` from parameters dict.

### `generate_shaone(timestamp_ms)`

Generate `shaOne` from timestamp.

## Algorithm Reference

- [moonshad.js](https://wappass.baidu.com/static/waplib/moonshad.js) - Baidu's official signature script
- [uni_wrapper.js](https://passport.baidu.com/passApi/js/uni_wrapper.js) - Baidu's login wrapper
- [Reverse Engineering Blog](https://mikublog.com/tech/2488) - Analysis reference

## Testing

```bash
# Clone the repository
git clone https://github.com/PlumBlossomMaid/baidu-moonshad-py.git
cd baidu-moonshad-py

# Install dependencies
pip install -e .[test]

# Run tests
pytest test_moonshad.py -v
```

## License

MIT License

## Author

PlumBlossomMaid
