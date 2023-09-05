from typing import List, Dict, Union
from dataclasses import dataclass

@dataclass
class GoogleDocument:
    """
    A dataclass representing a file in the Google Picker.

    The class takes a dictionary as an argument and sets the key-value pairs as attributes
    on the object. The dictionary should represent the properties of a Google Document
    as per the `Google Picker API <https://developers.google.com/drive/picker/reference#document>`_.

    .. note::
        This class is not intended to be manually instantiated. Instances of this class are
        created by the :class:`~GoogleDocuments` class.

    Attributes are dynamically set based on the key-value pairs in the dictionary provided.

    :param dict_data: A dictionary where the keys represent attribute names and the values
                            represent attribute values. Should represent a Google Document as 
                            per the Google Picker API.
    :return: An instance of the GoogleDocument class representing the Google Document.
    :rtype: dict
    """
    def __init__(self, dict_data: Dict[str, Union[str, int, bool]]):
        for key, value in dict_data.items():
            setattr(self, key, value)

class GoogleDocuments:
    """
    A class to represent a list of GoogleDocument objects.

    The class takes a list of dictionaries as an argument and creates a :class:`~GoogleDocument` object
    for each dictionary in the list.

    Usage:
    ::
        @app.callback(
            [Input('google-picker', 'documents')],
            prevent_initial_call=True
        )
        def display_output(documents):
            docs : List[GoogleDocument] = GoogleDocuments(documents)

    :param documents_data: A list of dictionaries where each dictionary should represent
                                the properties of a Google Document as per the Google Picker API.
    :return: A list of :class:`~GoogleDocument` objects.
    :rtype: List[dict]

    .. note::
        Only data from the Google Picker API returned by the :class:`~GooglePicker` should be passed into this class.
    """

    def __new__(cls, documents_data: List[Dict[str, Union[str, int, bool]]]) -> List['GoogleDocument']:
        if documents_data is None:
            return []
        else:
            return [GoogleDocument(doc) for doc in documents_data]