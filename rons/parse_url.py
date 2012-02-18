import urlparse
import urllib

def parse_redis_url(redis_url):
    '''
    >>> parse_redis_url('redis://:pass%20@localhost:1234/selecteddb%20')
    ('localhost', 1234, 'pass ', 'selecteddb ')
    >>> parse_redis_url('redis://:pass%20@localhost:1234/')
    ('localhost', 1234, 'pass ', None)
    >>> parse_redis_url('redis://localhost:1234/')
    ('localhost', 1234, None, None)
    >>> parse_redis_url('redis://localhost:1234')
    ('localhost', 1234, None, None)
    >>> parse_redis_url('redis://localhost/')
    ('localhost', 6379, None, None)
    >>> parse_redis_url('redis://')
    ('localhost', 6379, None, None)
    >>> parse_redis_url('redis://')
    ('localhost', 6379, None, None)
    '''
    (use, pas, hos, por, pat) = _parse_url(redis_url, 'redis://', def_port=6379)
    return (hos, por, pas, pat)

def _parse_url(url, scheme, def_username=None, def_password=None,
                           def_host='localhost', def_port=None, def_path=None):
    assert url.startswith(scheme), "Only " + scheme + " protocol supported."
    # Urlsplit doesn't know how to parse query when scheme is weird.
    # Pretend we're using http.
    o = urlparse.urlsplit('http://' + url[len(scheme):])
    path = o.path[1:] if o.path.startswith('/') else o.path

    return (
        urllib.unquote(o.username) if o.username is not None else def_username,
        urllib.unquote(o.password) if o.password is not None else def_password,
        urllib.unquote(o.hostname) if o.hostname is not None else def_host,
        o.port if o.port else def_port,
        urllib.unquote(path) if path else def_path,
        )


