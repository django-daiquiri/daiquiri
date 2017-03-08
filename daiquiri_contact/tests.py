import unittest
from forms import ContactForm


class FormTests(unittest.TestCase):
    def test_validation(self):
        form_data = {
            'contact_name': 'X' * 300,
        }

        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
