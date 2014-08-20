"""
This module defines a number of canned templates used to create the static objects which serve the redirects. It also \
defined get_template which will take a string from the stiny config fle and return a jinja2.Template object for the \
file-based template or canned template.

.. note:: Template Config Strings
This documentation is duplicated in the configuration module, but it's worth noting twice. There are two valid forms \
of a template config string in the configration file. For a canned template, it must start with  "CANNED:" and be the \
name of a canned template in this module, e.g. "CANNED:META_REDIRECT_NO_BODY". For a user-provided file-based template \
it must start with "FILE:" and be the os path to the file ('~' is recognized), e.g. "FILE:~/.stiny/my_template.html".
"""

from os.path import exists as _os_path_exists

from jinja2 import Template as _Template

# In order to perform module introspection with hasattr, getattr
# noinspection PyUnresolvedReferences
import stiny.templates
from configuration import valid_template_value, Invalid
from exceptions import MalformedTemplateConfig, TemplateNotFoundException


# noinspection PyPep8
META_REDIRECT_REDIRECT_TEXT = \
    """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
        <meta http-equiv="Refresh" content="0; url={{ url.url }}"/>
    </head>
    <body>
    <p>Please click this link if you are not redirected: <a url="{{ url.url }}">link</a>.</p>
    </body>
    </html>
    """

META_REDIRECT = \
    """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
        <meta http-equiv="Refresh" content="0; url={{ url.url }}" />
    </head>
    </html>
    """

META_REDIRECT_GOOGLE_ANALYTICS = \
    """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
        <meta http-equiv="Refresh" content="0; url={{ url.url }}" />
        <script>
          (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
          (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
          m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
          })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

          ga('create', '{{ analytics.id }}', 'auto');
          ga('send', 'pageview', { 'title': 'target:{{ url.url }}'});
        </script>
    </head>
    </html>
    """

BLANK_TEMPLATE = ""

def get_template(template_config):
    """
    Returns the template based on the config string
    :param template_config: The template config string from the configutation file
    :type template_config: str
    :raises MalformedTemplateConfig: If the template config string does not begin with CANNED or FILE
    :raises TemplateNotFoundException: If the name of the canned template or the path of the file based template \
    cannot be found.
    :returns jinja2.Template: The Template object containing the user-defined tempalte or canned template
    """
    try:
        valid_template_value(template_config)
    except Invalid as e:
        raise MalformedTemplateConfig(e.msg)

    template_value = template_config.split(":")[1]

    if 'CANNED:' in template_config:
        if hasattr(stiny.templates, template_value):
            return _Template(getattr(stiny.templates, template_value))
        else:
            raise TemplateNotFoundException("Canned template {} not found".format(template_config))
    else:
        if _os_path_exists(template_value):
            with open(template_value, 'r') as f:
                template = '\n'.join(f.read())
                return _Template(template)
        else:
            raise TemplateNotFoundException("File based template {} not found".format())
