"""Refresh approved public projects without querying private repository metadata."""
import html
import json
import re
import time
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'jacoboi33'
START = '<!-- RECENT-PROJECTS:START -->'
END = '<!-- RECENT-PROJECTS:END -->'
NAME = re.compile(r'[A-Za-z0-9_.-]+')
MAX_ITEMS = 5
MAX_PAGES = 10
MAX_DESCRIPTION = 120
ATTEMPTS = 3
RETRYABLE = {429, 500, 502, 503, 504}


def safe_text(value, limit=MAX_DESCRIPTION):
    text = str(value or '').replace('\n', ' ').replace('\r', ' ')
    # Drop control, format (bidi overrides, zero-width) and line/paragraph separators.
    text = ''.join(c for c in text if unicodedata.category(c) not in ('Cc', 'Cf', 'Zl', 'Zp')).strip()
    if len(text) > limit:
        text = text[:limit - 1].rstrip() + '…'
    return re.sub(r'([\\`*\[\]_|])', r'\\\1', html.escape(text))


def eligible(r, allowed):
    return (isinstance(r, dict) and r.get('private') is False and not r.get('fork')
            and not r.get('archived') and isinstance(r.get('name'), str)
            and r['name'] in allowed and r['name'] not in ('.', '..')
            and isinstance(r.get('owner'), dict) and r['owner'].get('login') == OWNER
            and NAME.fullmatch(r['name']) is not None)


def render(repositories, allowed):
    selected = [r for r in repositories if eligible(r, allowed)]
    if not selected:
        raise ValueError('No approved public projects found; leave README unchanged')
    selected.sort(key=lambda r: r.get('pushed_at') or '', reverse=True)
    lines = []
    for r in selected[:MAX_ITEMS]:
        name = r['name']
        detail = safe_text(r.get('description') or r.get('language') or 'Project repository')
        date = (r.get('pushed_at') or '')[:10]
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
            date = 'not available'
        lines.append(f'- **[{safe_text(name)}](https://github.com/{OWNER}/{name})** — {detail} · Last push: {date}')
    return '\n'.join(lines)


def update(readme, content):
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError('Expected exactly one pair of recent-project markers')
    if readme.index(START) > readme.index(END):
        raise ValueError('Recent-project START marker must come before END')
    before, tail = readme.split(START)
    _, after = tail.split(END)
    return before + START + '\n' + content + '\n' + END + after


def load_allowlist(path):
    names = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(names, list) or not all(isinstance(n, str) and NAME.fullmatch(n) for n in names):
        raise ValueError(f'{path.name} must be a JSON list of repository names')
    return set(names)


def get_json(url):
    # Deliberately no Authorization header: this endpoint can return only public data.
    request = Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'jacoboi33-profile'})
    for attempt in range(1, ATTEMPTS + 1):
        try:
            with urlopen(request, timeout=15) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in RETRYABLE or attempt == ATTEMPTS:
                raise
            retry_after = (error.headers or {}).get('Retry-After', '')
            time.sleep(min(int(retry_after), 60) if retry_after.isdigit() else 5 * attempt)
        except (URLError, TimeoutError):
            if attempt == ATTEMPTS:
                raise
            time.sleep(5 * attempt)


def fetch_public():
    repos = []
    for page in range(1, MAX_PAGES + 1):
        batch = get_json(f'https://api.github.com/users/{OWNER}/repos?type=owner&sort=pushed&direction=desc&per_page=100&page={page}')
        if not isinstance(batch, list):
            raise ValueError('Unexpected API response; leave README unchanged')
        repos.extend(batch)
        if len(batch) < 100:
            return repos
    raise ValueError('Pagination limit exceeded; leave README unchanged')


def main(root=ROOT, fetch=fetch_public):
    allowed = load_allowlist(root / 'scripts/public-projects.json')
    repositories = fetch()
    content = render(repositories, allowed)
    found = {r['name'] for r in repositories if eligible(r, allowed)}
    for name in sorted(allowed - found):
        print(f'::warning::{name} is allowlisted but is not an eligible public repository')
    path = root / 'README.md'
    with open(path, encoding='utf-8', newline='') as f:
        old = f.read()
    new = update(old, content)
    if old == new:
        return False
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(new)
    return True


if __name__ == '__main__':
    main()
