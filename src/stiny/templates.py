# noinspection PyPep8
META_REDIRECT = \
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>redirect</title>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
    <meta http-equiv="Refresh" content="0; url={{ url.url }}"/>
</head>
<body>
<p>Please click this link if you are not redirected: <a url="{{ url.url }}">link</a>.</p>
</body>
</html>
"""

META_REDIRECT_NO_BODY = \
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>redirect</title>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
    <meta http-equiv="Refresh" content="0; url={{ url.url }}" />
</head>
</html>
"""
