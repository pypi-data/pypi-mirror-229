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
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import os
import base64


# 生成RSA公钥和私钥
def generate_rsa_keys(bits='2048'):
    """
    生成RSA公钥和私钥对。

    Args:
        bits (str): 指定生成密钥对的位数，可选值为 '2048'、'3072' 和 '4096'，默认为 '2048'。

    Returns:
        tuple: 一个包含私钥PEM和公钥PEM的元组。
    """
    # 定义不同的密钥长度
    bits_dict = {
        '2048': 2048,
        '3072': 3072,
        '4096': 4096
    }
    # 根据传入的密钥长度参数来选择使用的密钥长度
    bits = bits_dict.get(bits, 2048)

    # 生成RSA私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits
    )
    # 从私钥中获取RSA公钥
    public_key = private_key.public_key()

    # 将私钥转化为PEM格式
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 将公钥转化为PEM格式
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # 返回PEM格式的公钥和私钥
    return str(private_pem, encoding="utf-8"), str(public_pem, encoding="utf-8")


# RSA加密
def rsa_encrypt(data, public_key):
    """
    使用RSA公钥对数据进行加密。

    Args:
        data (str or bytes): 需要加密的数据，数据类型为字符串或字节。
        public_key (str): 用于加密数据的PEM格式RSA公钥。

    Returns:
        str or bytes: 包含加密后的数据和加密后的AES密钥的元组，返回的类型与传入的数据类型相同。
    """
    try:
        public_key = serialization.load_pem_public_key(
            public_key.encode(),
            backend=default_backend()
        )
    except:
        raise Exception("无效的加密密钥")

    # 检查 data 类型并进行必要的转换
    if isinstance(data, str):
        data = data.encode()
        data_str = True
    else:
        data_str = False

    aes_key = base64.urlsafe_b64encode(os.urandom(32))
    f = Fernet(aes_key)
    encrypted_data = f.encrypt(data)
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 将 encrypted_aes_key 的长度以 4 字节整数形式添加到加密数据前
    encrypted_data_with_key = (str(len(encrypted_aes_key)) + '-').encode() + encrypted_aes_key + encrypted_data
    # 如果 data 为 str 则返回 str密文 ，否则返回 bytes
    return base64.urlsafe_b64encode(encrypted_data_with_key).decode('utf-8') if data_str else encrypted_data_with_key


# RSA解密
def rsa_decrypt(encrypted_data_with_key, private_key):
    """
    使用RSA私钥解密数据。

    Args:
        encrypted_data_with_key (str or bytes): 需要解密的数据，是一个Base64编码过的字符串或字节，其中包含加密后的数据和加密后的AES密钥。
        private_key (str): 用于解密数据的PEM格式RSA私钥。

    Returns:
        str or bytes: 解密后的原始数据，返回的类型与传入的数据类型相同。
    """
    try:
        private_key = serialization.load_pem_private_key(
            private_key.encode(),
            password=None,
            backend=default_backend()
        )
    except:
        raise Exception("无效的加密密钥")

    # 检查 data 类型并进行必要的转换
    if isinstance(encrypted_data_with_key, str):
        encrypted_data_with_key = base64.urlsafe_b64decode(encrypted_data_with_key.encode())
        data_str = True
    else:
        data_str = False

    try:
        # 提取 AES 密钥的长度和 AES 密钥
        aes_key_len_end = encrypted_data_with_key.find(b'-')
        aes_key_len = int(encrypted_data_with_key[:aes_key_len_end])
        encrypted_aes_key = encrypted_data_with_key[aes_key_len_end + 1:aes_key_len_end + 1 + aes_key_len]
        encrypted_data = encrypted_data_with_key[aes_key_len_end + 1 + aes_key_len:]

        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        f = Fernet(aes_key)
        decrypted_data = f.decrypt(encrypted_data)
    except:
        raise Exception("无效的加密密钥或损坏的数据")

    # 如果 data 为 str 则返回 str明文 ，否则返回 bytes
    return str(decrypted_data, encoding="utf-8") if data_str else decrypted_data
