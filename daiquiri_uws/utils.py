from django.http import HttpResponse, HttpResponseRedirect


class UWSBadRequest(HttpResponse):
    status_code = 403


class UWSSuccessRedirect(HttpResponseRedirect):
    status_code = 303
