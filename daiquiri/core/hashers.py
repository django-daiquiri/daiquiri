# inspired by https://djangosnippets.org/snippets/10572/

from collections import OrderedDict

from django.contrib.auth.hashers import CryptPasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare, get_random_string
from django.utils.encoding import force_str
from django.utils.translation import gettext_noop as _


class CrypdSHA512PasswordHasher(CryptPasswordHasher):

    algorithm = 'crypt_sha512'

    def salt(self):
        return '$6$' + get_random_string(8)

    def encode(self, password, salt):
        crypt = self._load_library()
        data = crypt.crypt(force_str(password), salt)
        return f"{self.algorithm}{data}"

    def verify(self, password, encoded):
        crypt = self._load_library()
        algorithm, rest = encoded.split('$', 1)
        salt, hash = rest.rsplit('$', 1)
        salt = '$' + salt
        assert algorithm == self.algorithm
        return constant_time_compare(f'{salt}${hash}', crypt.crypt(force_str(password), salt))

    def safe_summary(self, encoded):
        algorithm, prefix, salt, hash = encoded.split('$')
        assert algorithm == self.algorithm
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('prefix'), prefix),
            (_('salt'), mask_hash(salt)),
            (_('hash'), mask_hash(hash)),
        ])
