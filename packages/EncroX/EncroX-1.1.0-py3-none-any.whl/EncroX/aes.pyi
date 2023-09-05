# EncroX是一个强大的加密拓展工具，旨在为您的应用程序和系统提供可靠的加密和解密功能。通过集成各种密码学算法和密钥管理方法，EncroX使您能够轻松地进行数据加密、解密和安全通信
# Copyright (C) 2023  Abner
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Union

def aes_encrypt(data: Union[str, bytes], key: Union[str, bytes]) -> Union[str, bytes]:
    """
    使用 AES 密钥对数据进行加密。

    Args:
        data (str or bytes): 需要加密的数据。
        key (str or bytes): AES 密钥，当 key 的类型为 bytes 时，长度必须为 16、24 或 32 字节。

    Returns:
        str or bytes: 加密后的数据。
    """
    ...

def aes_decrypt(encrypted_data: Union[str, bytes], key: Union[str, bytes]) -> Union[str, bytes]:
    """
    使用 AES 密钥解密数据。

    Args:
        encrypted_data (str or bytes): 需要解密的数据。
        key (str or bytes): AES 密钥，当 key 的类型为 bytes 时，长度必须为 16、24 或 32 字节。

    Returns:
        str or bytes: 解密后的原始数据。
    """
    ...
