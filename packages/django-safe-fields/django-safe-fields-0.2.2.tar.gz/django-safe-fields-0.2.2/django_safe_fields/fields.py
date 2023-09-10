import copy
import logging

from fastutils import cipherutils
from zenutils import sixutils

from django.db import models
from django.conf import settings
from django.utils.datastructures import OrderedSet
from .utils import kwargs_pop_item
from .utils import kwargs_push_item

logger = logging.getLogger(__name__)


class SafeFieldMixinBase(object):
    def __init__(self, *args, **kwargs):
        used_ciphers = kwargs_pop_item(kwargs, "used_ciphers", None)
        cipher = kwargs_pop_item(kwargs, "cipher", None)
        cipher_class = kwargs_pop_item(kwargs, "cipher_class", None)
        cipher_kwargs = kwargs_pop_item(kwargs, "cipher_kwargs", None)
        result_encoder = kwargs_pop_item(kwargs, "result_encoder", None)
        force_text = kwargs_pop_item(kwargs, "force_text", None)
        password = kwargs_pop_item(kwargs, "password", None)
        self.used_ciphers = used_ciphers or []
        if cipher:
            self.cipher = cipher
        else:
            password = password or settings.SECRET_KEY
            cipher_class = cipher_class or cipherutils.MysqlAesCipher
            cipher_kwargs = cipher_kwargs and copy.deepcopy(cipher_kwargs) or {}
            if result_encoder:
                cipher_kwargs["result_encoder"] = result_encoder
            else:
                if cipher_class.default_result_encoder is None:
                    cipher_kwargs["result_encoder"] = cipherutils.HexlifyEncoder()
            if force_text is None:
                cipher_kwargs["force_text"] = True
            else:
                cipher_kwargs["force_text"] = force_text
            self.cipher = cipher_class(password=password, **cipher_kwargs)
        super(SafeFieldMixinBase, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, *args, **kwargs):
        for cipher in [self.cipher] + self.used_ciphers:
            try:
                value = cipher.decrypt(value)
                return value
            except Exception:
                logger.warn("Warn: {0} has old cipher encrypted data.".format(self))
        logger.error(
            "Error: SafeCharField.from_db_value decrypt failed: value=%s", value
        )
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.cipher.encrypt(value)
        return sixutils.TEXT(value)

    def get_lookup(self, lookup_name):
        base_lookup = super(SafeFieldMixinBase, self).get_lookup(lookup_name)
        return type(
            base_lookup.__name__,
            (base_lookup,),
            {"get_db_prep_lookup": self.get_db_prep_lookup},
        )

    def get_db_prep_lookup(self, value, connection):
        if callable(value):
            value = value()
        if isinstance(value, OrderedSet):
            value2 = OrderedSet()
            for item in value:
                value2.add(self.cipher.encrypt(item))
            value = value2
        else:
            value = [self.cipher.encrypt(value)]
        result = ("%s", value)
        return result


class SafeStringFieldMixin(SafeFieldMixinBase):
    pass


class SafeCharField(SafeStringFieldMixin, models.CharField):
    pass


class SafeTextField(SafeStringFieldMixin, models.TextField):
    pass


class SafeEmailField(SafeStringFieldMixin, models.EmailField):
    pass


class SafeURLField(SafeStringFieldMixin, models.URLField):
    pass


class SafeGenericIPAddressField(SafeStringFieldMixin, models.GenericIPAddressField):
    def __init__(self, *args, **kwargs):
        max_length = kwargs_pop_item(kwargs, "max_length", None)
        max_length = max_length or 128
        kwargs_push_item(kwargs, "max_length", max_length)
        super(SafeGenericIPAddressField, self).__init__(*args, **kwargs)
        self.max_length = max_length

    def get_internal_type(self):
        return "CharField"


class SafeIntegerField(SafeFieldMixinBase, models.IntegerField):
    def __init__(self, *args, **kwargs):
        cipher_class = kwargs_pop_item(kwargs, "cipher_class", None)
        result_encoder = kwargs_pop_item(kwargs, "result_encoder", None)
        force_text = kwargs_pop_item(kwargs, "force_text", None)
        cipher_class = cipher_class or cipherutils.IvCipher
        result_encoder = result_encoder or cipherutils.RawDataEncoder()
        kwargs_push_item(kwargs, "cipher_class", cipher_class)
        kwargs_push_item(kwargs, "result_encoder", result_encoder)
        kwargs_push_item(kwargs, "force_text", False)  # force_text force to False
        super(SafeIntegerField, self).__init__(*args, **kwargs)


class SafeNumbericFieldMixinBase(SafeFieldMixinBase):
    def __init__(self, *args, **kwargs):
        result_encoder = kwargs_pop_item(kwargs, "result_encoder", None)
        result_encoder = result_encoder or cipherutils.RawDataEncoder()
        kwargs_push_item(kwargs, "result_encoder", result_encoder)
        super(SafeNumbericFieldMixinBase, self).__init__(*args, **kwargs)

    def force_numberic(self, value):
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if isinstance(value, str):
            if "." in value:
                return float(value)
            else:
                return int(value)
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.force_numberic(value)
        result = super(SafeNumbericFieldMixinBase, self).get_db_prep_value(
            value, connection, prepared
        )
        return result


class SafeBigIntegerField(SafeNumbericFieldMixinBase, models.CharField):
    def __init__(self, *args, **kwargs):
        max_length = kwargs_pop_item(kwargs, "max_length", None)
        cipher_class = kwargs_pop_item(kwargs, "cipher_class", None)
        cipher_kwargs = kwargs_pop_item(kwargs, "cipher_kwargs", None)
        force_text = kwargs_pop_item(kwargs, "force_text", None)
        max_length = max_length or 128
        cipher_class = cipher_class or cipherutils.IvfCipher
        cipher_kwargs = cipher_kwargs and copy.deepcopy(cipher_kwargs) or {}
        cipher_kwargs["float_digits"] = 0
        kwargs_push_item(kwargs, "max_length", max_length)
        kwargs_push_item(kwargs, "cipher_class", cipher_class)
        kwargs_push_item(kwargs, "cipher_kwargs", cipher_kwargs)
        kwargs_push_item(kwargs, "force_text", False)
        super(SafeBigIntegerField, self).__init__(*args, **kwargs)


class SafeFloatField(SafeNumbericFieldMixinBase, models.CharField):
    def __init__(self, *args, **kwargs):
        max_length = kwargs_pop_item(kwargs, "max_length", None)
        cipher_class = kwargs_pop_item(kwargs, "cipher_class", None)
        force_text = kwargs_pop_item(kwargs, "force_text", None)
        max_length = max_length or 128
        cipher_class = cipher_class or cipherutils.IvfCipher
        kwargs_push_item(kwargs, "max_length", max_length)
        kwargs_push_item(kwargs, "cipher_class", cipher_class)
        kwargs_push_item(kwargs, "force_text", False)
        super(SafeFloatField, self).__init__(*args, **kwargs)
