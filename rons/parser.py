'''
Recursive decoder for Redis protocol. The code is quite reasonable and
has no external dependencies whatsoever.

To test run:
$ python -m doctest parser.py -v
'''
import collections
import itertools


class ProtocolError(Exception): pass

EMPTY=0
BULK=1
MULTIBULK=2
_State = collections.namedtuple('State', ['s', 'l', 'r', 'state'])
def State(**kwargs):
    x = {'s':None, 'l':None, 'r':None, 'state':None}
    x.update(kwargs)
    return _State(**x)

INITIAL_STATE=State(s=EMPTY)

def initial_state():
    return INITIAL_STATE

def decode(buf, state):
    if state.s is EMPTY:
        line, p, rest = buf.partition('\r\n')
        if not p: return ( 0, None, INITIAL_STATE )
        c, t, line_len = line[0], line[1:], len(line)+2
        if c not in '+-:$*':
            raise ProtocolError("Unexpected Redis response %r" % (line,))

        if c in ('+', '-'):
            return ( line_len, (c, t), INITIAL_STATE )
        elif c is ':':
            return ( line_len, (':', int(t)), INITIAL_STATE )

        no = int(t)
        if c is '$':
            if no is -1:
                return ( line_len, ('$', None), INITIAL_STATE )
            else:
                return ( line_len, None, State(s=BULK, l=no) )
        elif c is '*':
            if no is -1:
                return ( line_len, ('*', None), INITIAL_STATE )
            else:
                return ( line_len, None, State(s=MULTIBULK, l=no, r=[], state=INITIAL_STATE) )
    elif state.s is BULK:
        if len(buf) < state.l+2: return (0, None, state)
        return ( state.l+2, ('$', buf[:state.l]), INITIAL_STATE )
    elif state.s is MULTIBULK:
        if state.l is 0:
            return ( 0, ('*', state.r), INITIAL_STATE )
        else:
            (c, frame, new_s_state) = decode(buf, state.state)
            state = state._replace(state=new_s_state)
            if frame:
                state = state._replace(r=state.r + [frame],
                                       l=state.l - 1)
            return (c, None, state)

def test_decode(buf):
    r'''
    >>> test_decode("$-1\r\n")
    [('$', None)]
    >>> test_decode("$6\r\nfoobar\r\n")
    [('$', 'foobar')]
    >>> test_decode("*0\r\n")
    [('*', [])]
    >>> test_decode("*-1\r\n")
    [('*', None)]
    >>> test_decode("*3\r\n$3\r\nfoo\r\n$-1\r\n$3\r\nbar\r\n")
    [('*', [('$', 'foo'), ('$', None), ('$', 'bar')])]
    >>> test_decode("*3\r\n$3\r\nSET\r\n$5\r\nmykey\r\n$7\r\nmyvalue\r\n")
    [('*', [('$', 'SET'), ('$', 'mykey'), ('$', 'myvalue')])]
    >>> test_decode("*4\r\n$3\r\nfoo\r\n$3\r\nbar\r\n$5\r\nHello\r\n$5\r\nWorld\r\n")
    [('*', [('$', 'foo'), ('$', 'bar'), ('$', 'Hello'), ('$', 'World')])]
    >>> # All at  once
    >>> test_decode("$-1\r\n$6\r\nfoobar\r\n*0\r\n*-1\r\n*3\r\n$3\r\nfoo\r\n$-1\r\n$3\r\nbar\r\n*3\r\n$3\r\nSET\r\$5\r\nmykey\r\n$7\r\nmyvalue\r\n*4\r\n$3\r\nfoo\r\n$3\r\nbar\r\n$5\r\nHello\r\n$5\r\nWorld\r\n")
    [('$', None), ('$', 'foobar'), ('*', []), ('*', None), ('*', [('$', 'foo'), ('$', None), ('$', 'bar')]), ('*', [('$', 'SET'), ('$', 'mykey'), ('$', 'myvalue')]), ('*', [('$', 'foo'), ('$', 'bar'), ('$', 'Hello'), ('$', 'World')])]
    >>> # Other things
    >>> test_decode("r\r\n")
    Traceback (most recent call last):
      ...
    ProtocolError: Unexpected Redis response 'r'
    >>> test_decode("+OK\r\n")
    [('+', 'OK')]
    >>> test_decode("-ERROR\r\n")
    [('-', 'ERROR')]
    >>> test_decode("$6\r\nfoo\r\n\r\r\n")
    [('$', 'foo\r\n\r')]
    '''
    pos, state, results = 0, initial_state(), []
    while True:
        (consumed, frame, state) = decode(buf[pos:], state)
        if frame:
            results.append( frame )
        elif not consumed:
            break
        pos += consumed
    return results

def encode(arguments):
    return ''.join(itertools.chain(
            ('*', str(len(arguments)), '\r\n'),
            *(('$', str(len(a)), '\r\n', a, '\r\n') for a in arguments)))

def test_encode(arguments):
    r'''
    >>> test_encode(['SET', 'mykey', 'myvalue'])
    '*3\r\n$3\r\nSET\r\n$5\r\nmykey\r\n$7\r\nmyvalue\r\n'
    >>> test_encode(['SET'])
    '*1\r\n$3\r\nSET\r\n'
    >>> test_encode([])
    '*0\r\n'
    '''
    return encode(arguments)
