import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError, URLError

from recent_projects import (END, NAME, ROOT, START, eligible, fetch_public, load_allowlist,
                             main, render, safe_text, update)


def repo(name='safe', **changes):
    r = dict(name=name, private=False, fork=False, archived=False,
             owner={'login': 'jacoboi33'}, pushed_at='2026-11-18T00:00:00Z')
    r.update(changes)
    return r


def names(output):
    return [line.split('**[')[1].split(']')[0] for line in output.splitlines()]


def response(payload):
    return io.BytesIO(json.dumps(payload).encode())


def http_error(code, retry_after=None):
    headers = {'Retry-After': retry_after} if retry_after else {}
    return HTTPError('https://api.github.com', code, 'error', headers, None)


class EligibilityTests(unittest.TestCase):
    def test_public_approved_repo_is_shown(self):
        self.assertEqual(names(render([repo()], {'safe'})), ['safe'])

    def test_ineligible_repos_excluded(self):
        cases = {
            'private': repo(private=True),
            'private missing': {k: v for k, v in repo().items() if k != 'private'},
            'private null': repo(private=None),
            'fork': repo(fork=True),
            'archived': repo(archived=True),
            'other owner': repo(owner={'login': 'other'}),
            'owner null': repo(owner=None),
            'owner not a dict': repo(owner='jacoboi33'),
            'name null': repo(name=None),
            'not a dict': ['safe'],
        }
        for label, r in cases.items():
            with self.subTest(label):
                self.assertFalse(eligible(r, {'safe'}))

    def test_unapproved_excluded(self):
        self.assertFalse(eligible(repo(), set()))

    def test_invalid_names_excluded(self):
        for name in ['javascript:evil', '../x', '.', '..', 'a b']:
            with self.subTest(name):
                self.assertFalse(eligible(repo(name), {name}))

    def test_nothing_eligible_raises_instead_of_blanking(self):
        with self.assertRaises(ValueError):
            render([repo(private=True)], {'safe'})
        with self.assertRaises(ValueError):
            render([], {'safe'})


class RenderTests(unittest.TestCase):
    def test_order_and_limit(self):
        rs = [repo(f'r{i}', pushed_at=f'2026-11-{10 + i}T00:00:00Z') for i in range(6)]
        out = render(rs, {r['name'] for r in rs})
        self.assertEqual(names(out), ['r5', 'r4', 'r3', 'r2', 'r1'])

    def test_equal_dates_keep_api_order(self):
        out = render([repo('first'), repo('second')], {'first', 'second'})
        self.assertEqual(names(out), ['first', 'second'])

    def test_line_format(self):
        out = render([repo(description='A tool')], {'safe'})
        self.assertEqual(out, '- **[safe](https://github.com/jacoboi33/safe)** — A tool · Last push: 2026-11-18')

    def test_detail_falls_back_to_language_then_default(self):
        self.assertIn('— Go ·', render([repo(description='', language='Go')], {'safe'}))
        self.assertIn('— Project repository ·', render([repo(description=None)], {'safe'}))

    def test_missing_or_invalid_date(self):
        for value in [None, 'garbage']:
            with self.subTest(value):
                self.assertIn('Last push: not available', render([repo(pushed_at=value)], {'safe'}))

    def test_undated_repos_sort_last(self):
        out = render([repo('old', pushed_at=None), repo('new')], {'old', 'new'})
        self.assertEqual(names(out), ['new', 'old'])


class SafeTextTests(unittest.TestCase):
    def test_untrusted_description_escaped(self):
        out = render([repo(description='<img src="x"> [link](javascript:evil)')], {'safe'})
        self.assertNotIn('<img', out)
        self.assertIn('&lt;img', out)
        self.assertIn('\\[link\\]', out)

    def test_markdown_characters_escaped(self):
        self.assertEqual(safe_text('a*b_c|d`e\\f'), 'a\\*b\\_c\\|d\\`e\\\\f')

    def test_newlines_and_control_characters_removed(self):
        self.assertEqual(safe_text('a\nb\rc‮d e\x00f​g'), 'a b cdefg')

    def test_long_text_truncated(self):
        out = safe_text('x' * 500)
        self.assertEqual(len(out), 120)
        self.assertTrue(out.endswith('…'))


class UpdateTests(unittest.TestCase):
    def test_only_marker_section_changes(self):
        old = 'intro\n' + START + '\nold\n' + END + '\nfooter'
        self.assertEqual(update(old, 'new'), 'intro\n' + START + '\nnew\n' + END + '\nfooter')

    def test_missing_duplicate_or_reversed_markers_fail(self):
        for old in ['', START, END, START + START + END, START + END + END, END + START]:
            with self.subTest(old):
                with self.assertRaises(ValueError):
                    update(old, 'new')


class AllowlistTests(unittest.TestCase):
    def load(self, text):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'list.json'
            path.write_text(text, encoding='utf-8')
            return load_allowlist(path)

    def test_valid_list(self):
        self.assertEqual(self.load('["a", "b-c"]'), {'a', 'b-c'})

    def test_invalid_shapes_rejected(self):
        for text in ['"bookie2"', '[1]', '{}', '["bad name"]', '[']:
            with self.subTest(text):
                with self.assertRaises(ValueError):
                    self.load(text)


@mock.patch('recent_projects.time.sleep')
@mock.patch('recent_projects.urlopen')
class FetchTests(unittest.TestCase):
    def test_single_short_page(self, urlopen, sleep):
        urlopen.return_value = response([repo()])
        self.assertEqual(fetch_public(), [repo()])
        self.assertEqual(urlopen.call_count, 1)

    def test_paginates_until_short_page(self, urlopen, sleep):
        urlopen.side_effect = [response([repo()] * 100), response([repo()] * 3)]
        self.assertEqual(len(fetch_public()), 103)
        self.assertIn('page=2', urlopen.call_args_list[1].args[0].full_url)

    def test_never_sends_credentials(self, urlopen, sleep):
        urlopen.return_value = response([])
        fetch_public()
        request = urlopen.call_args.args[0]
        self.assertTrue(request.full_url.startswith('https://api.github.com/users/jacoboi33/repos?'))
        self.assertNotIn('Authorization', request.headers)
        self.assertNotIn('authorization', {k.lower() for k in request.headers})

    def test_non_list_response_rejected(self, urlopen, sleep):
        urlopen.return_value = response({'message': 'API rate limit exceeded'})
        with self.assertRaises(ValueError):
            fetch_public()

    def test_page_limit(self, urlopen, sleep):
        urlopen.side_effect = lambda *a, **k: response([repo()] * 100)
        with self.assertRaisesRegex(ValueError, 'Pagination limit'):
            fetch_public()

    def test_retries_transient_errors(self, urlopen, sleep):
        urlopen.side_effect = [http_error(503), http_error(429, '7'), response([repo()])]
        self.assertEqual(fetch_public(), [repo()])
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [5, 7])

    def test_gives_up_after_three_attempts(self, urlopen, sleep):
        urlopen.side_effect = [http_error(502), http_error(502), http_error(502)]
        with self.assertRaises(HTTPError):
            fetch_public()
        self.assertEqual(urlopen.call_count, 3)

    def test_retries_network_errors(self, urlopen, sleep):
        urlopen.side_effect = [URLError('reset'), TimeoutError(), response([repo()])]
        self.assertEqual(fetch_public(), [repo()])
        urlopen.side_effect = [URLError('down')] * 3
        with self.assertRaises(URLError):
            fetch_public()

    def test_rate_limit_403_not_retried(self, urlopen, sleep):
        urlopen.side_effect = [http_error(403)]
        with self.assertRaises(HTTPError):
            fetch_public()
        sleep.assert_not_called()


class MainTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/public-projects.json').write_text('["safe", "gone"]', encoding='utf-8')
        self.readme = self.root / 'README.md'
        self.original = '# Hi 🚀\r\n' + START + '\nold\n' + END + '\n— end\n'
        self.readme.write_bytes(self.original.encode('utf-8'))

    def tearDown(self):
        self.dir.cleanup()

    def test_writes_changed_section_and_preserves_rest(self):
        with mock.patch('builtins.print') as printed:
            self.assertTrue(main(self.root, lambda: [repo()]))
        text = self.readme.read_bytes().decode('utf-8')
        self.assertTrue(text.startswith('# Hi 🚀\r\n'))
        self.assertIn('[safe](https://github.com/jacoboi33/safe)', text)
        self.assertTrue(text.endswith(END + '\n— end\n'))
        printed.assert_called_once_with('::warning::gone is allowlisted but is not an eligible public repository')

    def test_unchanged_readme_not_rewritten(self):
        with mock.patch('builtins.print'):
            main(self.root, lambda: [repo()])
            before = self.readme.stat().st_mtime_ns
            self.assertFalse(main(self.root, lambda: [repo()]))
        self.assertEqual(self.readme.stat().st_mtime_ns, before)

    def test_failures_leave_readme_untouched(self):
        def broken():
            raise http_error(403)
        for fetch in [broken, lambda: [], lambda: [repo(private=True)]]:
            with self.subTest(fetch):
                with self.assertRaises(Exception):
                    main(self.root, fetch)
                self.assertEqual(self.readme.read_bytes(), self.original.encode('utf-8'))


class RepositoryContractTests(unittest.TestCase):
    def test_real_readme_has_one_ordered_marker_pair(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        current = readme.split(START)[1].split(END)[0].strip()
        self.assertEqual(update(readme, current), readme)

    def test_real_allowlist_is_valid(self):
        allowed = load_allowlist(ROOT / 'scripts/public-projects.json')
        self.assertTrue(allowed)
        self.assertTrue(all(NAME.fullmatch(n) for n in allowed))


if __name__ == '__main__':
    unittest.main()
