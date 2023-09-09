from typing import Literal

def modstring(text:str, mod:Literal['green', 'yellow', 'red', 'blue', 'bold', 'italic', 'underline']) -> str:
    """
    Modifies the string adding one of the mod list.

    Args:
    -----
        - `text` (str): string to be modified.
        - `mod` (str): modification to add to the text.
    
    Returns:
    --------
        - `str`: modified text.
    """
    mods = {'green':'\033[32m', 'yellow':'\033[33m', 'red':'\033[31m', 'blue':'\033[34m', \
            'bold':'\033[1m', 'italic':'\033[3m', 'underline':'\033[4m', \
            'end':'\033[0m'}
    try:
        assert text and type(text)==str
        return mods.get(mod) + text + mods.get('end')
    
    except AssertionError:
        print('The value passed to "text" is not type string.')
    except ValueError:
        print('The value passed to "color" is not listed.')