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
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
import hashlib


def aes_encrypt(data, key):
    """
    使用 AES 密钥对数据进行加密。

    Args:
        data (str or bytes): 需要加密的数据。
        key (str or bytes): AES 密钥，当 key 的类型为 bytes 时，长度必须为 16、24 或 32 字节。

    Returns:
        str or bytes: 加密后的数据。
    """
    # 将密钥转换为字节类型，并使用 SHA-256 哈希函数处理密钥
    if isinstance(key, str):
        key = hashlib.sha256(key.encode()).digest()

    # 检查 data 类型并进行必要的转换
    if isinstance(data, str):
        data = data.encode()
        data_str = True
    else:
        data_str = False

    try:
        # 创建 AES 密码器
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
    except:
        raise Exception("无效的加密密钥")

    # 对数据进行填充
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    # 加密数据
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # 如果原始数据为字符串类型，则返回加密后的字符串
    return base64.urlsafe_b64encode(encrypted_data).decode('utf-8') if data_str else encrypted_data


def aes_decrypt(encrypted_data, key):
    """
    使用 AES 密钥解密数据。

    Args:
        encrypted_data (str or bytes): 需要解密的数据。
        key (str or bytes): AES 密钥，当 key 的类型为 bytes 时，长度必须为 16、24 或 32 字节。

    Returns:
        str or bytes: 解密后的原始数据。
    """
    # 将密钥转换为字节类型，并使用 SHA-256 哈希函数处理密钥
    if isinstance(key, str):
        key = hashlib.sha256(key.encode()).digest()

    # 检查 data 类型并进行必要的转换
    if isinstance(encrypted_data, str):
        encrypted_data = base64.urlsafe_b64decode(encrypted_data.encode())
        data_str = True
    else:
        data_str = False

    try:
        # 创建 AES 解码器
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()

        # 解密数据
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # 去除填充
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    except:
        raise Exception("无效的加密密钥或损坏的数据")

    # 如果原始数据为字符串类型，则返回解密后的字符串
    return str(unpadded_data, encoding="utf-8") if data_str else unpadded_data
