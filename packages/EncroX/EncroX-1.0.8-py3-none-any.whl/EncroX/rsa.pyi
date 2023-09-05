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
from typing import Tuple, Union

def generate_rsa_keys(bits: str = '2048') -> Tuple[str, str]:
    """
    生成RSA公钥和私钥对。

    Args:
        bits (str): 指定生成密钥对的位数，可选值为 '2048'、'3072' 和 '4096'，默认为 '2048'。

    Returns:
        tuple: 一个包含私钥PEM和公钥PEM的元组。
    """
    ...

def rsa_encrypt(data: Union[str, bytes], public_key: str) -> Union[str, bytes]:
    """
    使用RSA公钥对数据进行加密。

    Args:
        data (str or bytes): 需要加密的数据，数据类型为字符串或字节。
        public_key (str): 用于加密数据的PEM格式RSA公钥。

    Returns:
        str or bytes: 包含加密后的数据和加密后的AES密钥的元组，返回的类型与传入的数据类型相同。
    """
    ...

def rsa_decrypt(encrypted_data_with_key: Union[str, bytes], private_key: str) -> Union[str, bytes]:
    """
    使用RSA私钥解密数据。

    Args:
        encrypted_data_with_key (str or bytes): 需要解密的数据，是一个Base64编码过的字符串或字节，其中包含加密后的数据和加密后的AES密钥。
        private_key (str): 用于解密数据的PEM格式RSA私钥。

    Returns:
        str or bytes: 解密后的原始数据，返回的类型与传入的数据类型相同。
    """
    ...
