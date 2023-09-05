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


def generate_ecc_keys(curve: str = '256') -> Tuple[str, str]:
    """
    使用选定的椭圆曲线生成ECC公钥和私钥对。

    Args:
        curve (str): 指定生成密钥对的椭圆曲线，可选值为 '256'、'384' 和 '521'，默认为 '256'。

    Returns:
        tuple: 一个包含私钥PEM和公钥PEM的元组。
    """
    ...


def ecc_encrypt(data: Union[str, bytes], public_key: str, private_key: str) -> Union[str, bytes]:
    """
    使用ECC公钥和私钥对数据进行加密。

    Args:
        data (str or bytes): 需要加密的数据，数据类型为字符串或字节。
        public_key (str): 对方的PEM格式ECC公钥。
        private_key (str): 自己的PEM格式ECC私钥。

    Returns:
        str or bytes: 加密后的数据，返回的类型与传入的数据类型相同。
    """
    ...


def ecc_decrypt(encrypted_data: Union[str, bytes], public_key: str, private_key: str) -> Union[str, bytes]:
    """
    使用ECC公钥和私钥解密数据。

    Args:
        encrypted_data (str or bytes): 需要解密的数据，数据类型为字符串或字节。
        public_key (str): 对方的PEM格式ECC公钥。
        private_key (str): 自己的PEM格式ECC私钥。

    Returns:
        str or bytes: 解密后的原始数据，返回的类型与传入的数据类型相同。
    """
    ...
