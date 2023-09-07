#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *
from zenutils.cipherutils import *

import zenutils.cipherutils
__all__ = [] + zenutils.cipherutils.__all__ + [
    "get_aes_mode",
    "md5_key",
    "mysql_aes_key",
    "sha1prng_key",
    "aes_padding_ansix923",
    "aes_padding_iso10126",
    "aes_padding_pkcs5",
    "AesCipher",
    "MysqlAesCipher",
    "RawKeyAesCipher",
    "RsaCipher",
]


from Crypto.Cipher import AES

from fastutils import aesutils
from fastutils import rsautils

from fastutils.aesutils import get_aes_mode

from fastutils.aesutils import get_md5_key as md5_key
from fastutils.aesutils import get_mysql_aes_key as mysql_aes_key
from fastutils.aesutils import get_sha1prng_key as sha1prng_key
from fastutils.aesutils import get_raw_aes_key as raw_aes_key

from fastutils.aesutils import padding_ansix923 as aes_padding_ansix923
from fastutils.aesutils import padding_iso10126 as aes_padding_iso10126
from fastutils.aesutils import padding_pkcs5 as aes_padding_pkcs5

class AesCipher(CipherBase):
    """AesCipher.

    mode: AES.MODE_ECB
    padding: aes_padding_pkcs5
    key: sha1prng_key # use sha1prng to transform the original password

    Example:

    In [47]: from fastutils import cipherutils

    In [48]: cipherutils.AesCipher(password='hello')
    Out[48]: <fastutils.cipherutils.AesCipher at 0x2285d130c10>

    In [49]: cipher = cipherutils.AesCipher(password='hello')

    In [50]: cipher.encrypt('hello')
    Out[50]: b'\\xa0\\x96<YaIOy`fiw\\x0b\\xf3\\xf7\\x84'

    In [51]: cipher.decrypt(cipher.encrypt('hello'))
    Out[51]: b'hello'

    In [59]: cipher = cipherutils.AesCipher(password='hello', result_encoder=cipherutils.Base64Encoder(), force_text=True)

    In [60]: cipher.encrypt('hello')
    Out[60]: 'oJY8WWFJT3lgZml3C/P3hA=='

    In [61]: cipher.decrypt('oJY8WWFJT3lgZml3C/P3hA==')
    Out[61]: 'hello'
    """
    def __init__(self, password, padding=aes_padding_pkcs5, key=sha1prng_key, mode=AES.MODE_ECB, **kwargs):
        self.aes_params = {
            "password": password,
            "padding": padding,
            "key": key,
            "mode": mode,
        }
        super().__init__(password=password, **kwargs)
    
    def do_encrypt(self, data, **kwargs):
        calling_kwargs = {}
        calling_kwargs.update(self.aes_params)
        calling_kwargs.update(kwargs)
        return aesutils.encrypt(data, **calling_kwargs)
    
    def do_decrypt(self, data, **kwargs):
        calling_kwargs = {}
        calling_kwargs.update(self.aes_params)
        calling_kwargs.update(kwargs)
        return aesutils.decrypt(data, **calling_kwargs)

class MysqlAesCipher(AesCipher):
    """AesCipher.

    mode: AES.MODE_ECB
    padding: aes_padding_pkcs5
    key: mysql_aes_key # use mysql default way to transform the original password

    Example:

    In [52]: from fastutils import cipherutils

    In [53]: cipher = cipherutils.MysqlAesCipher(password='hello')

    In [54]: cipher.encrypt('hello')
    Out[54]: b'\\xca\\xb2\\x9e\\xe5\\x9e\\xe9\\xec\\xc3j\\xc7\\xdf\\x82l\\x1b\\xcd\\xa9'

    In [55]: cipher.decrypt(cipher.encrypt('hello'))
    Out[55]: b'hello'

    In [56]: cipher = cipherutils.MysqlAesCipher(password='hello', result_encoder=cipherutils.Base64Encoder(), force_text=True)

    In [57]: cipher.encrypt('hello')
    Out[57]: 'yrKe5Z7p7MNqx9+CbBvNqQ=='

    In [58]: cipher.decrypt('yrKe5Z7p7MNqx9+CbBvNqQ==')
    Out[58]: 'hello'
    """
    def __init__(self, password, padding=aes_padding_pkcs5, key=mysql_aes_key, mode=AES.MODE_ECB, **kwargs):
        super().__init__(password, padding, key, mode, **kwargs)

class RawKeyAesCipher(AesCipher):
    """AesCipher.

    mode: AES.MODE_ECB
    padding: aes_padding_pkcs5
    key: raw_aes_key # use password as aes key directly, so that the password must be 16 chars length.
    
    Most java applications do AES encrypt like code below.

    function encrypt(String content, String password) {
        // password length must equals 16
        try {
            byte[] key = password.getBytes();
            SecretKeySpec skey = new SecretKeySpec(key, "AES")
            Cipher cipher = Cipher.getInstance(ALGORITHMSTR);
            cipher.init(Cipher.ENCRYPT_MODE, skey);
            byte[] contentBytes = content.getBytes("utf-8");
            byte[] contentEncrypted = cipher.doFinal(contentBytes);
            return Base64.encodeBase64String(contentEncrypted);
        } catch (Exception e) {
            return null;
        }
    }

    It is not good to generate the key by taking the first 16 bytes of the password. Add this to make life easy.

    Example:

    In [1]: from fastutils import cipherutils

    In [2]: cipher = cipherutils.RawKeyAesCipher(password='hello')

    In [3]: cipher.encrypt('hello') # Since password length is not 16, so encrypt get error
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
<ipython-input-3-f47a0d4a8ca0> in <module>
......
......
ValueError: Incorrect AES key length (5 bytes)

    """

    def __init__(self, password, padding=aes_padding_pkcs5, key=raw_aes_key, mode=AES.MODE_ECB, **kwargs):
        if len(password) < 16:
            raise ValueError("The password must be in 16 chars length. More that 16 chars will be truncate the first 16 chars.")
        super().__init__(password, padding, key, mode, **kwargs)

StupidJavaAesCipher = RawKeyAesCipher

class RsaCipher(CipherBase):

    default_result_encoder = Utf8Encoder()
    default_force_text = True

    def __init__(self, public_key=None, private_key=None, passphrase=None, **kwargs):
        self.passphrase = passphrase
        if public_key:
            if isinstance(public_key, BASESTRING_TYPES):
                self.public_key = rsautils.load_public_key(public_key)
            else:
                self.public_key = public_key
        else:
            self.public_key = None
        if private_key:
            if isinstance(private_key, BASESTRING_TYPES):
                self.private_key = rsautils.load_private_key(private_key, passphrase)
            else:
                self.private_key = private_key
            if not self.public_key:
                self.public_key = self.private_key.publickey()
        else:
            self.private_key = None
        print(self.public_key)
        print(self.private_key)
        super().__init__(**kwargs)

    def do_encrypt(self, text, **kwargs):
        if not self.public_key:
            raise RuntimeError("public_key NOT provided...")
        result = rsautils.encrypt(text, self.public_key)
        result = force_bytes(result)
        return result
    
    def do_decrypt(self, data, **kwargs):
        if not self.private_key:
            raise RuntimeError("private_key NOT provided...")
        data = force_text(data)
        result = rsautils.decrypt(data, self.private_key)
        result = force_bytes(result)
        return result
