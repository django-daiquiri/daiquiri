import os
from lunr import lunr
import re

from django.conf import settings

from .utils import get_file_path, read_file_content

# lunr index variable
_lunr_index = []

# content from all files
_cms_files = {}


def _find_title_in_content(html):
    start_pattern = "<h\d{1,5}>"
    end_pattern = "</h\d{1,5}>"

    title = "..."
    match_start = re.search(start_pattern, html)
    if match_start:
        title_starts_at = match_start.span()[1]
        match_end = re.search(end_pattern, html[title_starts_at:])
        if match_end:
            title_ends_at = title_starts_at + match_end.span()[0]
            title = html[title_starts_at:title_ends_at]
    return title


def search_for_string(string_query):

    build_lunr_index()

    try:
        file_urls = [f["ref"] for f in _lunr_index.search(string_query)]
        results = [f for _, f in _cms_files.items() if f["url"] in file_urls]
    except:
        results = []

    return results


def build_lunr_index():

    global _lunr_index
    global _cms_files

    docs_path = os.path.join(settings.FILES_BASE_PATH, settings.FILES_DOCS_REL_PATH)

    unique_files = set()
    for dir_path, _, files in os.walk(docs_path):
        for file in files:
            file_path = get_file_path(os.path.join(dir_path, file))
            if file_path and (file_path.endswith(".html") or file_path.endswith(".md")):
                unique_files.add(file_path)

    any_changes = False

    # clean up files that do not exist anymore
    for file_path in _cms_files:
        if file_path not in unique_files:
            any_changes = True
            _cms_files.pop(file_path)


    # read content of a file if it was modified since the last read
    for file_path in unique_files:
        current_mtime = os.path.getmtime(file_path)
        previous_mtime = _cms_files.get(file_path, {}).get("mtime", 0.0)
        if current_mtime != previous_mtime:
            any_changes = True
            body = read_file_content(file_path)
            title = _find_title_in_content(body)
            _cms_files[file_path] = {}
            _cms_files[file_path]["mtime"] = current_mtime
            _cms_files[file_path]["body"] = body
            _cms_files[file_path]["title"] = title
            _cms_files[file_path]["url"] = \
                    os.path.join(settings.FILES_BASE_URL,
                                 os.path.relpath(os.path.splitext(file_path)[0],
                                                 settings.FILES_BASE_PATH), "")

    # make an update of the lunr index if there were any changes in the files
    # since the previous search
    if any_changes:
        docs = [{
            "path": path,
            "url": doc["url"],
            "body": doc["body"]
            } for path, doc in _cms_files.items()]
        _lunr_index = lunr(ref="url", fields=("body",), documents = docs)

    return _lunr_index, _cms_files

