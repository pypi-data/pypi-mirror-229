# EncroX 官方文档

## 简介

EncroX是一个强大的加密拓展工具，旨在为您的应用程序和系统提供可靠的加密和解密功能。通过集成各种密码学算法和密钥管理方法，EncroX使您能够轻松地进行数据加密、解密和安全通信。

## 许可证

EncroX 使用 AGPL-3 开源许可证。请仔细阅读许可证文本以了解使用和分发 EncroX 的限制和义务。您可以在 [LICENSE](https://github.com/KindLittleTurtle/EncroX/blob/main/LICENSE) 文件中找到完整的许可证文本。

## 主要功能

- 支持生成 ECC（椭圆曲线加密）公钥和私钥对。
- 支持生成 RSA 公钥和私钥对。
- 提供基于 RSA 的加密和解密功能，用于保护数据的传输和存储。
- 提供基于 ECC 的加密和解密功能，用于安全通信和数据保护。
- 提供基于 AES 的加密和解密功能，用于快速且可靠地加密和解密数据。
- 提供简单易用的接口，方便集成到您的应用程序和系统中。

## 使用示例

### 生成 ECC 密钥对

```python
from EncroX.ecc import generate_ecc_key
private_key, public_key = generate_ecc_keys(curve='256')
```

生成指定椭圆曲线（可选参数：'256'、'384'、'521'）的 ECC 私钥和公钥。

#### 函数签名

```python
def generate_ecc_keys(curve='256') -> Tuple[str, str]:
    """
    使用选定的椭圆曲线生成ECC公钥和私钥对。

    Args:
        curve (str): 指定生成密钥对的椭圆曲线，可选值为 '256'、'384' 和 '521'，默认为 '256'。

    Returns:
        tuple: 一个包含私钥PEM和公钥PEM的元组。
    """
    ...
```

### 生成 RSA 密钥对

```python
from EncroX.rsa import generate_rsa_keys
private_key, public_key = generate_rsa_keys(bits='2048')
```

生成指定位数（可选参数：'2048'、'3072'、'4096'）的 RSA 私钥和公钥。

#### 函数签名

```python
def generate_rsa_keys(bits='2048') -> Tuple[str, str]:
    """
    生成RSA公钥和私钥对。

    Args:
        bits (str): 指定生成密钥对的位数，可选值为 '2048'、'3072' 和 '4096'，默认为 '2048'。

    Returns:
        tuple: 一个包

含私钥PEM和公钥PEM的元组。
    """
    ...
```

### 使用 RSA 公钥加密数据

```python
from EncroX.rsa import rsa_encrypt
encrypted_data = rsa_encrypt(data, public_key)
```

使用 RSA 公钥对数据进行加密，并返回加密后的数据。

#### 函数签名

```python
def rsa_encrypt(data, public_key) -> Union[str, bytes]:
    """
    使用RSA公钥对数据进行加密。

    Args:
        data (str or bytes): 需要加密的数据，数据类型为字符串或字节。
        public_key (str): 用于加密数据的PEM格式RSA公钥。

    Returns:
        str or bytes: 包含加密后的数据和加密后的AES密钥的元组，返回的类型与传入的数据类型相同。
    """
    ...
```

### 使用 RSA 私钥解密数据

```python
from EncroX.rsa import rsa_decrypt
decrypted_data = rsa_decrypt(encrypted_data_with_key, private_key)
```

使用 RSA 私钥解密包含加密数据和加密密钥的数据，并返回解密后的原始数据。

#### 函数签名

```python
def rsa_decrypt(encrypted_data_with_key, private_key) -> Union[str, bytes]:
    """
    使用RSA私钥解密数据。

    Args:
        encrypted_data_with_key (str or bytes): 需要解密的数据，是一个Base64编码过的字符串或字节，其中包含加密后的数据和加密后的AES密钥。
        private_key (str): 用于解密数据的PEM格式RSA私钥。

    Returns:
        str or bytes: 解密后的原始数据，返回的类型与传入的数据类型相同。
    """
    ...
```

### 使用 ECC 加密数据

```python
from EncroX.ecc import ecc_encrypt
encrypted_data = ecc_encrypt(data, public_key, private_key)
```

使用对方的 ECC 公钥和自己的 ECC 私钥对数据进行加密，并返回加密后的数据。

#### 函数签名

```python
def ecc_encrypt(data, public_key, private_key) -> Union[str, bytes]:
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
```

### 使用 ECC 解密数据

```python
from EncroX.ecc import ecc_decrypt
decrypted_data = ecc_decrypt(encrypted_data, public_key, private_key)
```

使用对方的 ECC 公钥和自己的 ECC 私钥解密数据，并返回解密后的原始数据。

#### 函数签名

```python
def ecc_decrypt(encrypted_data, public_key, private_key) -> Union[str, bytes]:
    """
    使用ECC公钥和私钥解密数据。

    Args:
        encrypted_data (str or bytes): 需要解密的数据，数据类型为字符串或字节。
        public_key (str): 对方的PEM格式ECC公钥。
        private_key (str): 自己的PE

M格式ECC私钥。

    Returns:
        str or bytes: 解密后的原始数据，返回的类型与传入的数据类型相同。
    """
    ...
```

### 使用 AES 加密数据

```python
from EncroX.aes import aes_encrypt
encrypted_data = aes_encrypt(data, key)
```

使用 AES 密钥对数据进行加密，并返回加密后的数据。

#### 函数签名

```python
def aes_encrypt(data: Union[str, bytes], key: Union[str, bytes]) -> Union[str, bytes]:
    """
    使用 AES 密钥对数据进行加密。

    Args:
        key (str or bytes): AES 密钥，当 key 的类型为 bytes 时，长度必须为 16、24 或 32 字节。
        data (str or bytes): 需要加密的数据，数据类型为字符串或字节。

    Returns:
        str or bytes: 加密后的数据，返回的类型与传入的数据类型相同。
    """
    ...
```

### 使用 AES 解密数据

```python
from EncroX.aes import aes_decrypt
decrypted_data = aes_decrypt(encrypted_data, key)
```

使用 AES 密钥解密数据，并返回解密后的原始数据。

#### 函数签名

```python
def aes_decrypt(encrypted_data: Union[str, bytes], key: Union[str, bytes]) -> Union[str, bytes]:
    """
    使用 AES 密钥解密数据。

    Args:
	encrypted_data (str or bytes): 需要解密的数据，数据类型为字符串或字节。
        key (str or bytes): AES 密钥，当 key 的类型为 bytes 时，长度必须为 16、24 或 32 字节。

    Returns:
        str or bytes: 解密后的原始数据，返回的类型与传入的数据类型相同。
    """
    ...
```

## 安装

您可以使用以下命令安装 EncroX：

```
pip install EncroX
```

## 更多信息

请参阅 [EncroX GitHub 仓库](https://github.com/KindLittleTurtle/EncroX) 获取更多信息和示例代码。

如果您有任何问题或需要进一步的帮助，请随时联系我们的支持团队。

---
