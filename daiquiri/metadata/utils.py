def get_doi_url(doi):
    if doi:
        return 'https://doi.org/%s' % doi.rstrip('/')
    else:
        return ''
