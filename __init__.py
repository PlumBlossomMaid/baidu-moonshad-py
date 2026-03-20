# moonshad/__init__.py
"""
Baidu AI Studio / Baidu Login Signature Generator.

100% aligned with Baidu's official `moonshad.js` V3 algorithm.
Generates `sig` and `shaOne` parameters for login requests.

Example:
    >>> from moonshad import MoonshadSigner
    >>>
    >>> signer = MoonshadSigner(screen_width=1080, screen_height=1920)
    >>> result = signer.generate_login_sign(
    ...     gid="device_gid",
    ...     token="token_from_server",
    ...     username="username",
    ...     password="encrypted_password",
    ... )
    >>> print(result['sig'])
    >>> print(result['shaOne'])
"""

from moonshad import MoonshadSigner, generate_sign_for_login

__all__ = ["MoonshadSigner", "generate_sign_for_login"]
__version__ = "1.0.0"
