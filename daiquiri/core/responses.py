from django.http import HttpResponseRedirect


class HttpResponseSeeOtherRedirect(HttpResponseRedirect):
    status_code = 303
