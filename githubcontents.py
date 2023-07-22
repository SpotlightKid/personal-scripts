from base64 import b64decode
from functools import lru_cache

from requests import Session
from requests.exceptions import RequestException
from cachecontrol import CacheControlAdapter
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import ExpiresAfter


__all__ = ("get_file",)
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_CONTENTS_API_URL = GITHUB_API_BASE_URL + "/repos/{owner}/{repo}/contents/{path}"


@lru_cache
def _get_session(cache_dir, expires):
    session = Session()
    adapter = CacheControlAdapter(cache=FileCache(cache_dir), heuristic=ExpiresAfter(seconds=expires))
    session.mount(GITHUB_API_BASE_URL, adapter)
    return session


def get_file(owner, repo, path, cache_dir='.web_cache', expires=3600*24*30, **kw):
    headers = kw.pop("headers", {})
    headers["accept"] = "application/vnd.github.v3+json"
    headers.setdefault("accept-encoding", "gzip")
    res = _get_session(cache_dir, expires).get(GITHUB_CONTENTS_API_URL.format(owner=owner, repo=repo, path=path.lstrip("/")), headers=headers, **kw)
    res.raise_for_status()

    try:
        return res, b64decode(res.json()["content"])
    except (KeyError, ValueError, TypeError) as exc:
        raise RequestException("Unexpected API response: {}".format(res.text))


if __name__ == "__main__":
    import logging
    import sys
    log = logging.getLogger("githubcontents")
    logging.basicConfig(level=logging.DEBUG)
    res, content = get_file(*sys.argv[1:])
    log.debug("Cached response: %s", "yes" if res.from_cache else "no")
    print(content.decode("utf-8"))
