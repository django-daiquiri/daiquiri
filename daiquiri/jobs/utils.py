from rest_framework.reverse import reverse

def make_query_dict_upper_case(input_dict):
    output_dict = input_dict.copy()

    for key in output_dict.keys():
        if key.upper() != key:
            values = output_dict.getlist(key)

            if key.upper() in output_dict:
                output_dict.appendlist(key.upper(), values)
            else:
                output_dict.setlist(key.upper(), values)

            output_dict.pop(key)

    return output_dict

def get_job_url(request, kwargs):
    namespace = request.resolver_match.namespace
    base_name = request.resolver_match.url_name.rsplit('-', 1)[0]
    return reverse('%s:%s-detail' % (namespace, base_name), request=request, kwargs=kwargs)
