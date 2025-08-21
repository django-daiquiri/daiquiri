from collections import OrderedDict

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import get_random_string
from django.utils.encoding import force_str
from django.utils.translation import gettext_noop as _

from passlib.hash import sha512_crypt


class CrypdSHA512PasswordHasher(BasePasswordHasher):
    """
    SHA-512-crypt password hasher using passlib.
    Compatible with Unix /etc/shadow ($6$salt$hash).
    """

    algorithm = 'crypt_sha512'

    def salt(self):
        return get_random_string(8)

    def encode(self, password, salt):
        """
        Encode a password using SHA-512-crypt via passlib.
        Returns format: crypt_sha512$6$salt$hash
        """
        password = force_str(password)
        stored = sha512_crypt.using(rounds=5000, salt=salt).hash(password)
        return f'{self.algorithm}${stored.lstrip("$")}'

    def verify(self, password, encoded):
        """
        Verify a password against a stored hash.
        `encoded` format: crypt_sha512$6$salt$hash
        """
        try:
            algorithm, rest = encoded.split('$', 1)
            if algorithm != self.algorithm:
                return False
            stored = '$' + rest  # reconstruct $6$salt$hash for passlib
            return sha512_crypt.verify(force_str(password), stored)
        except Exception:
            return False

    def safe_summary(self, encoded):
        """
        Provide a masked summary for admin display.
        """
        try:
            algorithm, prefix, salt, hash = encoded.split('$')
            assert algorithm == self.algorithm
            return OrderedDict(
                [
                    (_('algorithm'), algorithm),
                    (_('prefix'), prefix),
                    (_('salt'), mask_hash(salt)),
                    (_('hash'), mask_hash(hash)),
                ]
            )
        except ValueError:
            return OrderedDict(
                [
                    (_('algorithm'), self.algorithm),
                    (_('hash'), mask_hash(encoded)),
                ]
            )
