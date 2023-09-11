import re
import string
from typing import List, Iterable, Tuple, Any, Dict

from api_compose.core.logging import (get_logger)

logger = get_logger(__name__)


def split_pascal_case_string(s: str) -> List[str]:
    result = []
    current_word = s[0]

    for i in range(1, len(s)):
        if s[i].isupper():
            result.append(current_word)
            current_word = s[i]
        else:
            current_word += s[i]

    result.append(current_word)
    return result


def convert_dotted_string_to_nested_dict(pairs: Iterable[Tuple[str, Any]]) -> Dict[str, Any]:
    """
    Parameters
    ----------
    pairs Iterable of string (in dots) - anything pairs
    Returns
    -------

    """
    nested_dict = {}

    for key, value in pairs:
        keys = key.split('.')
        current_dict = nested_dict

        for i, key in enumerate(keys):
            if type(current_dict) != dict:
                logger.error(
                    f'Cannot create nested dict for key path **{keys}** as it is already occupied by **{current_dict}**')
                current_dict = {}

            if i == len(keys) - 1:
                current_dict[key] = value
            else:
                if key not in current_dict:
                    current_dict[key] = {}
                current_dict = current_dict[key]

    return nested_dict


def normalise_sentence(sentence: str) -> str:
    """
    Parameters
    ----------
    sentence

    Returns
    -------
    """
    return re.sub('\s+', ' ', (sentence.lower().translate(str.maketrans('', '', string.punctuation))).strip())
