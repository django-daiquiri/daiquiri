from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict


class TestSingleObjectMixin():

    def model_to_dict(self, instance=None):
        if instance is None:
            instance = self.instance

        model_dict = model_to_dict(instance)
        model_data = {}
        for key in model_dict:
            if model_dict[key] is not None:
                model_data[key] = model_dict[key]

        return model_data


class TestListViewMixin():

    def test_list_view(self):
        url = reverse(self.list_url_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestRetrieveViewMixin():

    def test_retrieve_view(self):
        url = reverse(self.retrieve_url_name, args=[self.instance.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestCreateViewMixin(TestSingleObjectMixin):

    def test_create_view_get(self):
        url = reverse(self.create_url_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_view_post(self):
        url = reverse(self.create_url_name)
        response = self.client.post(url, self.model_to_dict())
        self.assertEqual(response.status_code, 302)


class TestUpdateViewMixin(TestSingleObjectMixin):

    def test_update_view_get(self):
        url = reverse(self.update_url_name, args=[self.instance.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_view_post(self):
        url = reverse(self.update_url_name, args=[self.instance.pk])
        response = self.client.post(url, self.model_to_dict())
        self.assertEqual(response.status_code, 302)


class TestDeleteViewMixin(TestSingleObjectMixin):

    def test_delete_view_get(self):
        url = reverse(self.delete_url_name, args=[self.instance.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_view_post(self):
        url = reverse(self.delete_url_name, args=[self.instance.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)


class TestModelStringMixin(TestSingleObjectMixin):

    def test_model_str(self):
        self.assertIsNotNone(self.instance.__str__())
