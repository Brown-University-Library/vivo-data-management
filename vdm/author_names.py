from collections import namedtuple
from nameparser import HumanName


#A named tuple to represent author names.
#This has to be declared outside of the function for pickling.
#http://stackoverflow.com/questions/16377215/how-to-pickle-a-namedtuple-instance-correctly
Author = namedtuple('Author',
    ['full', 'last', 'first', 'first_initial', 'middle', 'middle_initial']
)


def chunk_name(name_str):
    """
    Split names into last, first initial, middle initial using
    the Python name parser:
    https://github.com/derek73/python-nameparser

    Return a named tuple representing the author.
    """
    name = HumanName(name_str)
    last = name.last.lower()
    first = name.first.lower().strip('.')
    middle = name.middle.lower().strip('.')
    if middle == u'':
        middle = None
    mi = None
    if middle is not None:
        try:
            mi = middle[0]
        except IndexError:
            pass
    try:
        fi = first[0]
    except IndexError:
        fi = None
    au = Author(
        full=name_str.lower(),
        last=last,
        first=first,
        first_initial=fi,
        middle=middle,
        middle_initial=mi
    )
    return au


def substr_match(a, b):
    """
    Verify substring matches of two strings.
    """
    if (a is None) or (b is None):
        return False
    else:
        return a in b


def catalyst_match(au1, au2):
    """
    Perform matching logic that follows the algorithim in
    http://profiles.catalyst.harvard.edu/Meetings/ProfilesRNSDisambiguation120120.pdf

    Expecting two named tuples as above.
    """
    #Exact last name match.
    if au1.last == au2.last:
        #First character match and substring match on first.
        if (au1.first[0] == au2.first[0]) and (substr_match(au1.first, au2.first) is True):
            #Substring match on middle initial if provided.
            if au1.middle_initial is not None:
                if substr_match(au1.middle_initial, au2.middle_initial) is True:
                    return True
            else:
                return True
    return False