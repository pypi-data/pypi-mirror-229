# django-safe-fields

Save field value encrypted to database.

## Install

```shell
pip install django-safe-fields
```

## Shipped Fields

**Mixins**

- SafeFieldMixinBase
- SafeStringFieldMixin
- SafeNumbericFieldMixinBase # used for fields that using none numberic database backend

**Fields & Instance Extra Init Parameters (You can use django's fields default parameters)**

- SafeCharField
    - password: default to settings.SECRET_KEY.
    - cipher_class: choices are cipherutils.AesCipher, cipherutils.S12Cipher or something similar. default to cipherutils.AesCipher.
    - kwargs
        - **Note**: kwargs parameters depend on the cipher class you choose. see details at https://pypi.org/project/fastutils/.
    - cipher: or you can provides cipher instance instead of cipher_class and class parameters. Has higher priority than cipher_class.
- SafeTextField
    - Same as SafeCharField
- SafeEmailField
    - Same as SafeCharField
- SafeURLField
    - Same as SafeCharField
- SafeGenericIPAddressField
    - Same as SafeCharField
- SafeIntegerField
    - **Note**: no extra init parameters
- SafeBigIntegerField # using varchar(max_length=128) in datatabase storage
    - password
    - kwargs
        - int_digits: default to 12
- SafeFloatField # using varchar(max_length=128) in database storage.
    - password
    - kwargs
        - int_digits: default to 12
        - float_digits: default to 4

## Note

1. Default cipher class is MysqlAesCipher. It keeps the same with mysql's aes_encrypt and aes_decrypt when the mysql's server variable block_encryption_mode=aes-128-ecb. The main trick is the method used to prepair the final key from the password.
1. Default password is settings.SECRET_KEY, but we STRONGLY suggest you use different password for every different field.

## Usage

**pro/settings.py**

```
INSTALLED_APPS = [
    ...
    'django_safe_fields',
    ...
]
```

1. Insert `django_safe_fields` into INSTALLED_APPS.

**app/models.py**

```
from django.db import models
from django.conf import settings
from django_safe_fields.fields import SafeCharField
from django_safe_fields.fields import SafeGenericIPAddressField
from django_safe_fields.fields import SafeIntegerField
from fastutils.cipherutils import S12Cipher
from fastutils.cipherutils import HexlifyEncoder

class Account(models.Model):
    username = SafeCharField(max_length=64)
    name = SafeCharField(max_length=64, cipher_class=S12Cipher)
    email = SafeCharField(max_length=128, null=True, blank=True, cipher=S12Cipher(password=settings.SECRET_KEY, encoder=HexlifyEncoder(), force_text=True))
    last_login_ip = SafeGenericIPAddressField(max_length=256, null=True, blank=True, password="THIS FIELD PASSWORD")
    level = SafeIntegerField(null=True, blank=True)

    def __str__(self):
        return self.username

```

1. All fields will be stored with encryption.
1. Aes is a strong cipher.
1. With aes encryption, you can NOT search partly, only the `exact` search rule will be accepted.
1. With aes encryption, you can NOT sort.
1. S12Cipher is string encode method that keeps the sorting result after encoded.
1. IvCihper is a week cipher for integer field that let you sort with the field.

## Test Passed On Python and Django Versions

- python27:~=django1.11.29
- python34:~=django1.11.29
- python34:~=django2.0.13
- python35:~=django1.11.29
- python35:~=django2.0.13
- python35:~=django2.1.15
- python35:~=django2.2.28
- python36:~=django2.0.13
- python36:~=django2.1.15
- python36:~=django2.2.28
- python36:~=django3.0.14
- python36:~=django3.1.14
- python36:~=django3.2.21
- python37:~=django2.0.13
- python37:~=django2.1.15
- python37:~=django2.2.28
- python37:~=django3.0.14
- python37:~=django3.1.14
- python37:~=django3.2.21
- python38:~=django2.0.13
- python38:~=django2.1.15
- python38:~=django2.2.28
- python38:~=django3.0.14
- python38:~=django3.1.14
- python38:~=django3.2.21
- python38:~=django4.0.10
- python38:~=django4.1.11
- python38:~=django4.2.5
- python39:~=django2.0.13
- python39:~=django2.1.15
- python39:~=django2.2.28
- python39:~=django3.0.14
- python39:~=django3.1.14
- python39:~=django3.2.21
- python39:~=django4.0.10
- python39:~=django4.1.11
- python39:~=django4.2.5
- python310:~=django2.1.15
- python310:~=django2.2.28
- python310:~=django3.0.14
- python310:~=django3.1.14
- python310:~=django3.2.21
- python310:~=django4.0.10
- python310:~=django4.1.11
- python310:~=django4.2.5
- python311:~=django2.2.28
- python311:~=django3.0.14
- python311:~=django3.1.14
- python311:~=django3.2.21
- python311:~=django4.0.10
- python311:~=django4.1.11
- python311:~=django4.2.5

## Releases

### v0.2.2

- Fix fastutils.strutils.force_text problem. Use zenutils.sixutils.TEXT instead.

### v0.2.1

- Fix problem with latest version of fastutils.

### v0.1.11

- Fix callable default value problem.

### v0.1.7

- Add used_ciphers parameters support, so that we can decrypt old data when we change cipher_class or field password.
- Add safe field management commands: list_safe_fields, mapping_cipher_fields_dumps. *Note:* Use mapping_cipher_fields_dumps to speed up the safe field initialization.

### v0.1.6

- Fix xxx__in query problem.

### v0.1.5

- Turn to bytes before doing encryption.

### v0.1.4

- Change init parameter encoder to result_encoder.

### v0.1.3

- Fix get_db_prep_lookup problem.

### v0.1.2

- Add SafeBigIntegerField and SafeFloatField.

### v0.1.1

- Fix problem in objects.get that double encrypt the raw data.

### v0.1.0

- First release.
