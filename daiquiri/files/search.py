import logging
import os
import re
from pathlib import Path

from django.conf import settings
from django.shortcuts import Http404, reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator

from lunr import lunr

from .storage import FileStore
from .utils import read_file_content

logger = logging.getLogger(__name__)

class Searcher:
    cms_files = {}
    lunr_index = None

    @classmethod
    def search_for_string(cls, string_query):

        cls.build_lunr_index()

        try:
            lunr_results = cls.lunr_index.search(string_query)
            file_urls = {f['ref']: f['score'] for f in lunr_results}
            match_data = {f['ref']: f['match_data'].metadata for f in lunr_results}
            results = [f for _, f in cls.cms_files.items() if f['url'] in file_urls]
        except:  # noqa: E722
            results = []

        for res in results:
            res['score'] = file_urls[res['url']]
            res['match_data'] = match_data[res['url']]
        results = sorted(results, key=lambda res: -res['score'])

        return cls._reformat(results.copy())

    @classmethod
    def build_lunr_index(cls):
        store = FileStore()
        docs_reference = settings.FILES_DOCS_REL_PATH

        if not docs_reference or docs_reference in ('.', './'):
            logger.error('FILES_DOCS_REL_PATH is not configured.')
            raise Http404

        try:
            docs_path = store.path(docs_reference)
        except ValueError:
            logger.error('FILES_DOCS_REL_PATH must be relative path: %s', docs_reference)
            raise Http404 from None

        if not docs_path.is_dir():
            logger.error('Documentation directory does not exist: %s', docs_reference)
            raise Http404

        content_references = set()
        for dir_path, _, names in os.walk(docs_path):
            for name in names:
                filesystem_path = Path(dir_path, name)
                if filesystem_path.suffix.lower() not in ('.html', '.md'):
                    continue
                content_references.add(store.relative(filesystem_path))

        if len(content_references) == 0:
            logger.error('No files found in %s', docs_path)
            raise Http404

        any_changes = False

        # Remove cache entries whose logical files disappeared.
        for reference in list(cls.cms_files):
            if reference not in content_references:
                any_changes = True
                cls.cms_files.pop(reference)

        # read content of a file if it was modified since the last read
        for reference in content_references:
            filesystem_path = store.path(reference)
            current_mtime = filesystem_path.stat().st_mtime
            previous_mtime = cls.cms_files.get(reference, {}).get('mtime', 0.0)
            if current_mtime != previous_mtime:
                any_changes = True
                body = read_file_content(Path(filesystem_path))
                title = cls.find_title_in_content(body)
                cls.cms_files[reference] = {
                    'mtime': current_mtime,
                    'body': strip_tags(body),
                    'title': strip_tags(title),
                    'url': reverse(
                        'files:file', kwargs={'file_path': os.path.splitext(reference)[0]}
                    ),
                }

        # make an update of the lunr index if there were any changes in the files
        # since the previous search
        if any_changes:
            docs = [
                {'path': path, 'url': doc['url'], 'body': doc['body'], 'title': doc['title']}
                for path, doc in cls.cms_files.items()
            ]
            cls.lunr_index = lunr(
                ref='url',
                fields=(
                    'body',
                    'title',
                ),
                documents=docs,
            )

    @classmethod
    def find_title_in_content(cls, html):
        start_pattern = '<h\\d{1,5}>'
        end_pattern = '</h\\d{1,5}>'

        title = '...'
        match_start = re.search(start_pattern, html)
        if match_start:
            title_starts_at = match_start.span()[1]
            match_end = re.search(end_pattern, html[title_starts_at:])
            if match_end:
                title_ends_at = title_starts_at + match_end.span()[0]
                title = html[title_starts_at:title_ends_at]
        return title

    @classmethod
    def _reformat(cls, results):
        """Truncates the text in the body around the search string -50:+250 chars"""
        num_chars_before = 50
        num_chars_after = 250
        num_chars = num_chars_before + num_chars_after

        for result in results:
            result['body'] = result['body'].strip(result['title'])
            result['match_data'] = next(iter(result['match_data'].keys()))
            truncator = Truncator(result['body'])
            if result['match_data'] in result['title']:
                result['body'] = truncator.chars(num_chars)
            else:
                search_string_pos = result['body'].find(result['match_data'])
                if search_string_pos >= 0:
                    result['body'] = truncator.chars(search_string_pos + num_chars_after)
                    if len(result['body']) > num_chars:
                        result['body'] = ''.join(['...', result['body'][-num_chars:]])
                else:
                    result['body'] = truncator.chars(num_chars)

        return results
