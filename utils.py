import os
import tempfile
import mailcap
import shlex

from email.iterators import typed_subpart_iterator


def split_commandstring(cmdstring):
    """
    split command string into a list of strings to pass on to subprocess.Popen
    and the like. This simply calls shlex.split but works also with unicode
    bytestrings.
    """
    if isinstance(cmdstring, str):
        cmdstring = cmdstring.encode('utf-8', errors='ignore')
    return shlex.split(cmdstring)


def parse_mailcap_nametemplate(tmplate='%s'):
    """this returns a prefix and suffix to be used
    in the tempfile module for a given mailcap nametemplate string"""
    nt_list = tmplate.split('%s')
    template_prefix = ''
    template_suffix = ''
    if len(nt_list) == 2:
        template_suffix = nt_list[1]
        template_prefix = nt_list[0]
    else:
        template_suffix = tmplate
    return (template_prefix, template_suffix)


def string_sanitize(string, tab_width=8):
    r"""
    strips, and replaces non-printable characters
    :param tab_width: number of spaces to replace tabs with. Read from
                      `globals.tabwidth` setting if `None`
    :type tab_width: int or `None`
    >>> string_sanitize(' foo\rbar ', 8)
    ' foobar '
    >>> string_sanitize('foo\tbar', 8)
    'foo     bar'
    >>> string_sanitize('foo\t\tbar', 8)
    'foo             bar'
    """

    string = string.replace('\r', '')

    lines = list()
    for line in string.split('\n'):
        tab_count = line.count('\t')

        if tab_count > 0:
            line_length = 0
            new_line = list()
            for i, chunk in enumerate(line.split('\t')):
                line_length += len(chunk)
                new_line.append(chunk)

                if i < tab_count:
                    next_tab_stop_in = tab_width - (line_length % tab_width)
                    new_line.append(' ' * next_tab_stop_in)
                    line_length += next_tab_stop_in
            lines.append(''.join(new_line))
        else:
            lines.append(line)

    return '\n'.join(lines)


def string_decode(string, enc='ascii'):
    """
    safely decodes string to unicode bytestring, respecting `enc` as a hint.
    :param string: the string to decode
    :type string: str or unicode
    :param enc: a hint what encoding is used in string ('ascii', 'utf-8', ...)
    :type enc: str
    :returns: the unicode decoded input string
    :rtype: unicode
    """

    if enc is None:
        enc = 'ascii'
    try:
        string = str(string, enc, errors='replace')
    except LookupError:  # malformed enc string
        string = string.decode('ascii', errors='replace')
    except TypeError:  # already unicode
        pass
    return string


def extract_body(mail, types=None, field_key='copiousoutput'):
    """Returns a string view of a Message.
    If the `types` argument is set then any encoding types there will be used
    as the prefered encoding to extract. If `types` is None then
    :ref:`prefer_plaintext <prefer-plaintext>` will be consulted; if it is True
    then text/plain parts will be returned, if it is false then text/html will
    be returned if present or text/plain if there are no text/html parts.
    :param mail: the mail to use
    :type mail: :class:`email.Message`
    :param types: mime content types to use for body string
    :type types: list[str]
    :returns: The combined text of any parts to be used
    :rtype: str
    """

    # preferred = 'text/plain' if settings.get(
    #     'prefer_plaintext') else 'text/html'
    preferred = 'text/plain'
    has_preferred = False

    # see if the mail has our preferred type
    if types is None:
        has_preferred = list(typed_subpart_iterator(
            mail, *preferred.split('/')))

    body_parts = []
    for part in mail.walk():
        ctype = part.get_content_type()

        if types is not None:
            if ctype not in types:
                continue
        cd = part.get('Content-Disposition', '')
        if cd.startswith('attachment'):
            continue
        # if the mail has our preferred type, we only keep this type
        # note that if types != None, has_preferred always stays False
        if has_preferred and ctype != preferred:
            continue

        enc = part.get_content_charset() or 'ascii'
        raw_payload = part.get_payload(decode=True)
        if ctype == 'text/plain':
            raw_payload = string_decode(raw_payload, enc)
            body_parts.append(string_sanitize(raw_payload))
        else:
            # get mime handler
            # _, entry = settings.mailcap_find_match(ctype, key=field_key)
            _mailcaps = mailcap.getcaps()
            _, entry = mailcap.findmatch(_mailcaps, ctype, key=field_key)
            tempfile_name = None
            stdin = None
            
            if entry:
                handler_raw_commandstring = entry['view']
                # in case the mailcap defined command contains no '%s',
                # we pipe the files content to the handling command via stdin
                if '%s' in handler_raw_commandstring:
                    # open tempfile, respect mailcaps nametemplate
                    nametemplate = entry.get('nametemplate', '%s')
                    prefix, suffix = parse_mailcap_nametemplate(nametemplate)
                    with tempfile.NamedTemporaryFile(
                            delete=False, prefix=prefix, suffix=suffix) \
                            as tmpfile:
                        tmpfile.write(raw_payload)
                        tempfile_name = tmpfile.name
                else:
                    stdin = raw_payload

                body_parts.append(
                    string_sanitize(
                        str(raw_payload, 'utf-8')
                    )
                )
                continue

                # read parameter, create handler command
                # parms = tuple('='.join(p) for p in part.get_params())

                # create and call external command
                # cmd = mailcap.subst(entry['view'], ctype,
                #                     filename=tempfile_name, plist=parms)
                # logging.debug('command: %s', cmd)
                # logging.debug('parms: %s', str(parms))

                # cmdlist = split_commandstring(cmd)
                # # call handler
                # rendered_payload, _, _ = helper.call_cmd(cmdlist, stdin=stdin)

                # # remove tempfile
                # if tempfile_name:
                #     os.unlink(tempfile_name)

                # if rendered_payload:  # handler had output
                #     body_parts.append(string_sanitize(rendered_payload))
    return u'\n\n'.join(body_parts)
