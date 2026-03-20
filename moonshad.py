#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2026 PlumBlossomMaid
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Baidu AI Studio / Baidu Login Signature Generation Module.

This module implements the signature algorithm used by Baidu's login system,
based on reverse engineering of moonshad.js V3.

Algorithm sources:
- https://wappass.baidu.com/static/waplib/moonshad.js
- https://passport.baidu.com/passApi/js/uni_wrapper.js
- https://mikublog.com/tech/2488 (reverse engineering reference)

Code style reference:
- https://github.com/PaddlePaddle/Paddle
"""

import base64
import hashlib
import time
from typing import Any, Dict, Optional

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class MoonshadSigner:
    """
    Baidu moonshad signature generator.

    This class implements the signature algorithm used in Baidu's login system.
    It generates `sig` and `shaOne` parameters required for login requests.

    Args:
        screen_width: Screen width in pixels (used for screen mapping).
        screen_height: Screen height in pixels (used for screen mapping).

    Attributes:
        VERSION_KEYS: List of 5 version keys that rotate daily.
        SCREEN_MAP: Mapping table for screen resolution digits.
        EXCLUDED_PARAMS: Parameters excluded from signature calculation.
    """

    # Five version keys extracted from moonshad.js
    VERSION_KEYS: list[str] = [
        "moonshad5moonsh2",
        "moonshad3moonsh0",
        "moonshad8moonsh6",
        "moonshad0moonsh1",
        "moonshad1moonsh9",
    ]

    # Screen resolution digit mapping table from moonshad.js
    SCREEN_MAP: dict[str, str] = {
        "0": "s",
        "1": "t",
        "2": "r",
        "3": "h",
        "4": "i",
        "5": "j",
        "6": "k",
        "7": "l",
        "8": "m",
        "9": "n",
        "a": "3",
        "b": "4",
        "c": "5",
        "d": "9",
        "e": "8",
        "f": "7",
        "g": "1",
        "h": "2",
        "i": "6",
        "j": "0",
        "k": "a",
        "l": "b",
        "m": "c",
        "n": "d",
        "o": "e",
        "p": "f",
        "q": "g",
        "r": "z",
        "s": "y",
        "t": "x",
        "u": "w",
        "v": "v",
        "w": "u",
        "x": "o",
        "y": "p",
        "z": "q",
    }

    # Parameters excluded from signature calculation
    EXCLUDED_PARAMS: set[str] = {"sig", "traceid", "callback", "elapsed", "shaOne"}

    def __init__(self, screen_width: int = 1920, screen_height: int = 1080) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

    def _get_version_key(self, timestamp: Optional[int] = None) -> str:
        """
        Get the version key based on the date (rotates every day).

        The key rotates among 5 predefined keys based on the number of days
        since the Unix epoch.

        Args:
            timestamp: Unix timestamp (seconds). Uses current time if None.

        Returns:
            The version key for the given date.
        """
        if timestamp is None:
            timestamp = int(time.time())

        days = timestamp // 86400
        index = days % 5
        return self.VERSION_KEYS[index]

    def _generate_screen_string(self) -> str:
        """
        Generate the screen mapping string.

        Concatenates screen width and height, then maps each digit using
        SCREEN_MAP.

        Returns:
            Mapped screen string.
        """
        screen_str = f"{self.screen_width}{self.screen_height}"
        mapped_chars = [self.SCREEN_MAP.get(ch, ch) for ch in screen_str]
        return "".join(mapped_chars)

    @staticmethod
    def _interleave_strings(str1: str, str2: str) -> str:
        """
        Interleave two strings character by character.

        Example:
            str1 = "abcde", str2 = "123" -> "a1b2c3de"

        Args:
            str1: First string.
            str2: Second string.

        Returns:
            Interleaved string.
        """
        result = []
        len1, len2 = len(str1), len(str2)

        for i in range(min(len1, len2)):
            result.append(str1[i])
            result.append(str2[i])

        if len1 > len2:
            result.append(str1[len2:])
        elif len2 > len1:
            result.append(str2[len1:])

        return "".join(result)

    def _prepare_sign_string(self, params: Dict[str, Any]) -> str:
        """
        Prepare the string for signature calculation.

        Filters out excluded parameters, sorts keys alphabetically,
        and concatenates as "key=value" pairs joined by "&".

        Args:
            params: Input parameters.

        Returns:
            Prepared signature string.
        """
        filtered = {}
        for key, value in params.items():
            if key not in self.EXCLUDED_PARAMS and value is not None:
                filtered[key] = value

        sorted_keys = sorted(filtered.keys())
        parts = [f"{k}={filtered[k]}" for k in sorted_keys]
        return "&".join(parts)

    @staticmethod
    def _md5(text: str) -> str:
        """Calculate MD5 hash."""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _sha1(text: str) -> str:
        """Calculate SHA1 hash."""
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _aes_ecb_encrypt(plaintext: str, key: str) -> bytes:
        """
        Encrypt plaintext using AES-ECB mode.

        If the key length is not 16 bytes, it is extended to 16 bytes using MD5.

        Args:
            plaintext: Plaintext to encrypt.
            key: Encryption key.

        Returns:
            Encrypted bytes.
        """
        if len(key) != 16:
            key_bytes = hashlib.md5(key.encode("utf-8")).digest()
        else:
            key_bytes = key.encode("utf-8")

        cipher = AES.new(key_bytes, AES.MODE_ECB)
        padded_data = pad(plaintext.encode("utf-8"), AES.block_size)
        return cipher.encrypt(padded_data)

    @staticmethod
    def _base64_encode(data: bytes) -> str:
        """Encode bytes to Base64 string."""
        return base64.b64encode(data).decode("utf-8")

    def generate_sig(
        self, params: Dict[str, Any], version_key: Optional[str] = None
    ) -> str:
        """
        Generate the `sig` parameter.

        Algorithm steps:
        1. Prepare signature string (sort and concatenate parameters)
        2. Calculate MD5 of the signature string
        3. Generate screen mapping string
        4. Interleave MD5 result with screen mapping
        5. Encrypt with AES-ECB using the version key
        6. Double Base64 encode the result

        Args:
            params: Request parameters.
            version_key: Version key (auto-selected by date if None).

        Returns:
            `sig` parameter value.
        """
        # Step 1: Prepare signature string
        sign_str = self._prepare_sign_string(params)

        # Step 2: MD5
        md5_result = self._md5(sign_str)

        # Step 3: Screen mapping
        screen_str = self._generate_screen_string()

        # Step 4: Interleave
        interleaved = self._interleave_strings(md5_result, screen_str)

        # Step 5: Get version key
        if version_key is None:
            timestamp = params.get("time", int(time.time()))
            version_key = self._get_version_key(timestamp)

        # Step 6: AES-ECB encryption
        encrypted = self._aes_ecb_encrypt(interleaved, version_key)

        # Step 7: Double Base64 encoding
        sig = self._base64_encode(encrypted)
        sig = self._base64_encode(sig.encode("utf-8"))

        return sig

    def generate_shaone(self, timestamp_ms: Optional[int] = None) -> str:
        """
        Generate the `shaOne` parameter.

        Algorithm steps:
        1. Start with a 13-digit millisecond timestamp
        2. Loop: current = SHA1(MD5(current))
        3. Stop when the result starts with "00"

        Args:
            timestamp_ms: 13-digit millisecond timestamp. Uses current time if None.

        Returns:
            `shaOne` parameter value (40-character hex string starting with "00").
        """
        if timestamp_ms is None:
            timestamp_ms = int(time.time() * 1000)

        current = str(timestamp_ms)

        while True:
            md5_result = self._md5(current)
            sha1_result = self._sha1(md5_result)

            if sha1_result[:2] == "00":
                return sha1_result

            current = sha1_result

    def generate_login_sign(
        self,
        gid: str,
        token: str = "",
        tpl: str = "aip",
        apiver: str = "v3",
        loginversion: str = "v5",
        lang: str = "zh-CN",
        login_class: str = "login",
        logintype: str = "dialogLogin",
        traceid: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate signature parameters for a login request.

        This is a convenience method that constructs the full parameter dictionary
        and generates both `sig` and `shaOne`.

        Args:
            gid: Device identifier.
            token: Temporary credential (empty for first login).
            tpl: Template, defaults to "aip".
            apiver: API version, defaults to "v3".
            loginversion: Login version, defaults to "v5".
            lang: Language, defaults to "zh-CN".
            login_class: The `class` parameter, defaults to "login".
            logintype: Login type, defaults to "dialogLogin".
            traceid: Trace ID.
            **kwargs: Additional parameters to include in the signature.

        Returns:
            Dictionary containing:
                - sig: Signature value
                - shaOne: shaOne value
                - tt: 13-digit millisecond timestamp
                - time: 10-digit second timestamp
                - alg: Algorithm version ("v3")
                - elapsed: Elapsed time (always 0)
        """
        tt_ms = int(time.time() * 1000)
        tt_sec = int(time.time())

        params = {
            "token": token,
            "tpl": tpl,
            "subpro": "",
            "apiver": apiver,
            "tt": tt_ms,
            "gid": gid,
            "loginversion": loginversion,
            "lang": lang,
            "traceid": traceid,
            "time": tt_sec,
            "alg": "v3",
            "elapsed": 0,
            "class": login_class,
            "logintype": logintype,
            **kwargs,
        }

        sig = self.generate_sig(params)
        sha_one = self.generate_shaone(tt_ms)

        return {
            "sig": sig,
            "shaOne": sha_one,
            "tt": tt_ms,
            "time": tt_sec,
            "alg": "v3",
            "elapsed": 0,
        }


def generate_sign_for_login(gid: str, token: str = "", **kwargs: Any) -> Dict[str, Any]:
    """
    Convenience function to generate login signature.

    Args:
        gid: Device identifier.
        token: Temporary credential.
        **kwargs: Additional parameters.

    Returns:
        Dictionary containing sig, shaOne, tt, time, alg, elapsed.
    """
    signer = MoonshadSigner()
    return signer.generate_login_sign(gid, token, **kwargs)


def main() -> None:
    """Test function for the module."""
    print("=" * 70)
    print("Baidu Moonshad Signature Generator Test")
    print("=" * 70)

    test_params = {
        "gid": "ACCFD4B-AA4B-4FA6-8453-2F0F96D0D23F",
        "token": "",
        "tpl": "aip",
        "apiver": "v3",
        "loginversion": "v5",
        "lang": "zh-CN",
        "login_class": "login",
        "logintype": "dialogLogin",
        "traceid": "",
    }

    print("\n[Input Parameters]")
    for key, value in test_params.items():
        print(f"  {key}: {value}")

    try:
        signer = MoonshadSigner(screen_width=1920, screen_height=1080)

        print("\n[Version Key Selection Test]")
        for i in range(10):
            test_time = 1700000000 + i * 86400
            key = signer._get_version_key(test_time)
            print(f"  Time {test_time} (day {test_time // 86400}) -> Key: {key}")

        result = signer.generate_login_sign(
            gid=test_params["gid"],
            token=test_params["token"],
            tpl=test_params["tpl"],
            apiver=test_params["apiver"],
            loginversion=test_params["loginversion"],
            lang=test_params["lang"],
            login_class=test_params["login_class"],
            logintype=test_params["logintype"],
            traceid=test_params["traceid"],
        )

        print("\n[Generated Results]")
        print(f"  tt: {result.get('tt')}")
        print(f"  time: {result.get('time')}")
        print(f"  alg: {result.get('alg')}")
        print(f"  sig: {result.get('sig')}")
        print(f"  shaOne: {result.get('shaOne')}")
        print(f"  elapsed: {result.get('elapsed')}")

        url_params = (
            f"&tt={result['tt']}&time={result['time']}"
            f"&alg={result['alg']}&sig={result['sig']}"
            f"&elapsed={result['elapsed']}&shaOne={result['shaOne']}"
        )
        print("\n[URL Parameter String]")
        print(f"  {url_params}")

        if result["shaOne"][:2] == "00":
            print("\n[Verification Passed] ✓ shaOne starts with '00'")
        else:
            print(
                f"\n[Verification Failed] ✗ shaOne starts with '{result['shaOne'][:2]}', expected '00'"
            )

        print("\n[Test Completed]")

    except Exception as e:
        print("\n[Test Failed] ✗")
        print(f"  Error: {e}")
        raise


if __name__ == "__main__":
    main()
