"""
Various utilities for manipulating and formatting strings.
"""

import string
import urllib


class SliceElideFormatter(string.Formatter):
    """An extended string formatter that provides key specifiers that allow
    string values to be sliced and elided if they exceed a length limit.  The
    additional formats are optional and can be combined with normal python
    formatting.  So the whole syntax looks like:
        key[|slice-options][$elide-options[:normal-options]
    Where slice options consist of '|' character to begin a slice request,
    followed by slice indexes separated by commas.  Thus {FOO|5,} requests
    everything after the 5th element.
      The elide consist of '$' character followed by an inter max field value,
    followed by '<', '^', or '>' for pre, centered, or post eliding, followed
    by the eliding string.  Thus {FOO$10<-} would display the last 9 chanacters
    of a string longer then 10 characters with '-' prefix.
      Slicing and eliding can be combined.  For example given a dict of
    {'FOO': 'centeredtextvalue', and a format string of
    '{FOO|1,-1$11^%2E%2E%2E}' would yield 'ente...valu'.  The slice spec removes
    the first and last characrers, and the elide spec center elides the
    remaining value with '...'.  The '...' value must be encoded in URL format
    since . is an existing special format character.
    """

    def get_value(self, key, args, kwds):
        """Called by string.Formatter for each format key found in the format
        string.  The key is checked for the presence of a slice or elide intro-
        ducer character.  If one or both a found the slice and/or elide spec
        is extracted, parsed and processed on value of found with the remaining
        key string.
        Arguments:
          key, A format key string possibly containing slice or elide specs
          args, Format values list tuple
          kwds, Format values key word dictrionary
        """
        sspec = espec = None
        if '|' in key:
            key, sspec = key.split('|')
            if '$' in sspec:
                sspec, espec = sspec.split('$')
        elif '$' in key:
            key, espec = key.split('$')
        value = args[int(key)] if key.isdigit() else kwds[key]
        if sspec:
            sindices = [int(sdx) if sdx else None
                        for sdx in sspec.split(',')]
            value = value[slice(*sindices)]
        if espec:
            espec = urllib.unquote(espec)
            if '<' in espec:
                value = self._prefix_elide_value(espec, value)
            elif '>' in espec:
                value = self._postfix_elide_value(espec, value)
            elif '^' in espec:
                value = self._center_elide_value(espec, value)
            else:
                raise ValueError('invalid eliding option %r' % espec)
        if sspec or espec:
            return value

        return super(SliceElideFormatter,self).get_value(key, args, kwds)

    def _center_elide_value(self, elidespec, value):
        """Return center elide value if it exceeds the elide length.
        Arguments:
          elidespec, The elide spec field extracted from key
          value, Value obtained from remaing key to maybe be elided
        """
        elidelen, elidetxt = elidespec.split('^')
        elen, vlen = int(elidelen), len(value or ())
        if vlen > elen:
            tlen = len(elidetxt)
            return value[:(elen-tlen)//2] + elidetxt + value[-(elen-tlen)//2:]
        return value

    def _postfix_elide_value(self, elidespec, value):
        """Return postfix elided value if it exceeds the elide length.
        Arguments:
          elidespec, The elide spec field extracted from key
          value, Value obtained from remaing key to maybe be elided
        """
        elidelen, elidetxt = elidespec.split('>')
        elen, vlen  = int(elidelen), len(value or ())
        if vlen > elen:
            tlen = len(elidetxt)
            return value[:(elen-tlen)] + elidetxt
        return value

    def _prefix_elide_value(self, elidespec, value):
        """Return prefix elided value if it exceeds the elide length.
        Arguments:
          elidespec, The elide spec field extracted from key
          value, Value obtained from remaing key to maybe be elided
        """
        elidelen, elidetxt = elidespec.split('<')
        elen, vlen  = int(elidelen), len(value or ())
        if vlen > elen:
            tlen = len(elidetxt)
            return elidetxt + value[-(elen-tlen):]
        return value


if __name__ == '__main__':
    sefmtr = SliceElideFormatter()
    edata = { 'CNT':'centeredtextvalue' }
    fmt = '{CNT|1,-1$10^%2E%2E%2E}'
    print 'SLCNTFMT^: 1234567890\n          %r' % \
          sefmtr.format(fmt, *(), **edata)
    fmt = '{CNT|1,-1$10^**:>12}'
    print 'SLCNTFMT^: 123456789012\n          %r' % \
          sefmtr.format(fmt, *(), **edata)
