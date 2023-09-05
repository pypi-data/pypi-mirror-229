from typing import Union, List, Dict

class View:
    """
    A View is a Tab in the Google Picker window which shows a list of files, it can also be used to prefill searches and filter by mimeTypes.
    
    :param viewId: The :class:`~ViewId` that gets used to create the View.
    :param mimeTypes: A single or a list of mimeTypes which are allowed to be shown in this View. If None is passed, no filtering is applied.
    :param query: A query string to prefill the search bar in the Google Picker window. The user can edit or remove this text freely.
    """
    def __init__(self, viewId : str, mimeTypes : Union[str, List[str]] = None, query : str = None):
        self.viewId = viewId
        self.mimeTypes = mimeTypes
        self.query = query

    def getId() -> str:
        """
        Returns the ViewId of this View.

        :return: The ViewId of this View.
        """
        return self.viewId

    def setMimeTypes(mimeTypes : Union[str, List[str]]):
        """
        Sets the mimeTypes of files which should be shown in this View. Overwrites any previous mimeTypes.
        """
        if isInstance(mimeTypes, str):
            self.mimeTypes = [mimeTypes]
        else:
            self.mimeTypes = mimeTypes

    def setQuery(query : str):
        """
        Sets the query string of this View, this can be changed by the user. Overwrites any previous query.
        """
        self.query = query

    def to_plotly_json(self) -> Dict[str, Union[str, List[str], None]]:
        """
        Converts the View to a dictionary for plotly. This is used internally by dash to pass the ViewGroup to the react frontend.
        """
        return {"type": "View", "viewId" : self.viewId, "mimeTypes" : self.mimeTypes, "query" : self.query}

class ViewGroup():
    """
    A ViewGroup is a collection of one or many Views. It can be used to group Views into a separate tab in the :class:`~GooglePicker`.

    :param args: One or many :class:`~ViewId` or :class:`~ViewGroup`. The first argument needs to be a :class:`~ViewId` which is the root view for this group.
    :param label: The label shown only on the root view of this group.
    """
    def __init__(self, *args : List[str], label : Union[str, None] = None):
        if not args or (not isinstance(args[0], str) and not isinstance(args[0], View)):
            raise ValueError("A ViewGroup needs one ViewID as root item")
        
        self.views = list(args)
        self.label = label

    def add(self, view : Union[str, "ViewGroup"]):
        """
        Adds a new View to the ViewGroup.

        :param view: A :class:`~ViewId` or :class:`~ViewGroup` to add to this ViewGroup.
        """
        self.views.append(view)

    def remove(self, view : Union[str, "ViewGroup"]):
        """
        Remove a view from the ViewGroup.

        :param view: A :class:`~ViewId` or :class:`~ViewGroup` to remove from this ViewGroup.
        """

        self.views.remove(view)

    def to_plotly_json(self) -> Dict[str, Union[str, List[Union[str, "ViewGroup"]]]]:
        """
        Converts the ViewGroup to a dictionary for plotly. This is used internally by dash to pass the ViewGroup to the react frontend.

        :return: A dictionary representing the ViewGroup.
        """
        return {"type": "ViewGroup", "views": self.views, "label": self.label}
