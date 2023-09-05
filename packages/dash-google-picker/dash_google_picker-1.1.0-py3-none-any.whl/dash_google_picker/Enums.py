from enum import Enum

class ViewId(str, Enum):
    """
    Enum for all Google Picker Views.

    Each attribute represents a different view that can be used in the Google Picker. Some views are deprecated and will return a 403 error.
    More information about these views can be found in the `Google Picker API documentation <https://developers.google.com/drive/picker/reference?#view-id>`_.
    """

    DOCS = "all"
    """
    Shows all Elements from the Google drive. This is the default view.
    """

    DOCS_IMAGES = "docs-images"
    """
    Shows only Images from the Google drive.
    """

    DOCS_IMAGES_AND_VIDEOS = "docs-images-and-videos"
    """
    Shows only images and videos from the Google drive.
    """

    DOCS_VIDEOS = "docs-videos"
    """
    Shows only videos from the Google drive.
    """

    DOCUMENTS = "documents"
    """
    Shows only Google documents from the Google drive.
    """

    DRAWINGS = "drawings"
    """
    Shows only Google Drive Drawings.
    """

    FOLDERS = "folders"
    """
    Shows only Folders from the Google drive. Making this the only view will make it impossible to select a file.
    """

    FORMS = "forms"
    """
    Shows only Google Forms from the Google drive.
    """

    IMAGE_SEARCH = "image-search"
    """
    This view is deprecated and will return a 403 error.
    """

    MAPS = "maps"
    """
    This view is deprecated and will return a 403 error.
    """

    PDFS = "pdfs"
    """
    Shows only PDFs from the Google drive.
    """

    PHOTOS = "photos"
    """
    This view is deprecated and will return a 403 error.
    """

    PHOTO_ALBUMS = "photo-albums"
    """
    This view is deprecated and will return a 403 error.
    """

    PHOTO_UPLOAD = "photo-upload"
    """
    This view is deprecated and will return a 403 error.
    """

    PRESENTATIONS = "presentations"
    """
    Shows only Google slides from the Google drive.
    """

    RECENTLY_PICKED = "recently-picked"
    """
    Shows only recently picked files from the Google drive. If no files have been picked yet, this view will be empty.
    """

    SPREADSHEETS = "spreadsheets"
    """
    Shows only Google Sheets from the Google drive.
    """

    VIDEO_SEARCH = "video-search"
    """
    This view is deprecated and will return a 403 error.
    """

    WEBCAM = "webcam"
    """
    This view is deprecated and will return a 403 error.
    """

    YOUTUBE = "youtube"
    """
    This view is deprecated and will return a 403 error.
    """

class Feature(str, Enum):
    """
    Enum for all Google Picker Features.

    Each attribute represents a features that can be enabled or disabled in the Google Picker. Some features appear to have no effect and others are deprecated and will return a 403 error. 
    Disabling features appears to rarely have an effect.
    More information about the officially supported features can be found in the `Google Picker API documentation <https://developers.google.com/drive/picker/reference?#feature>`_.
    """

    Cba = "shadeDialog"
    """
    Increases the size of the picker dialog to nearly the complete screen size.
    """

    E9 = "ftd"
    """
    Appears to stop the first two "pages" from loading thumbnails, besides that it appears to have no effect.
    """

    Hba = "simpleUploadEnabled"
    """
    Appears to have no effect.
    """

    I8 = "cropA11y"
    """
    Appears to stop the first two "pages" from loading thumbnails, besides that it appears to have no effect.
    """

    Jca = "urlInputVisible"
    """
    Adds a url input field to the Google Picker, enabling the user to select a file from an url.
    """

    K9 = "formsEnabled"
    """
    Appears to stop the first two "pages" from loading thumbnails, besides that it appears to have no effect.
    """

    MINE_ONLY = "mineOnly"
    """
    Shows only documents owned by the user when showing items from Google Drive, also appears to stop the first two "pages" from loading thumbnails.
    """

    MULTISELECT_ENABLED = "multiselectEnabled"
    """
    Allows the user to select multiple files, also appears to stop the first two "pages" from loading thumbnails.
    """

    NAV_HIDDEN = "navHidden"
    """
    Hides the drive filepath and the tabs for switching between views. If the navigation pane is hidden, users can only select from the first view chosen. It also appears to stop the first two "pages" from loading thumbnails.
    """
    
    SIMPLE_UPLOAD_ENABLED = "simpleUploadEnabled"
    """
    No effect, unsupported by this library.
    """

    SUPPORT_DRIVES = "sdr"
    """
    Deprecated, appears to have no effect.
    """

    SUPPORT_TEAM_DRIVES = "std"
    """
    Deprecated, appears to have no effect
    """

    T_DOLLAR = "mineOnly"
    """
    Same effect as :py:attr:`~Feature.MINE_ONLY`: Shows only documents owned by the user when showing items from Google Drive, also appears to stop the first two "pages" from loading thumbnails.
    """

    U_DOLLAR = "minimal"
    """
    This prevents the picker window from opening and throws an error in the console.
    """

    Uaa = "profilePhoto"
    """
    Deprecated feature and will return a 403 error if enabled.
    """

    V_DOLLAR = "minew"
    """
    Deprecated feature and will return a 403 error if enabled.
    """

    A_DOLLAR = "horizNav"
    """
    Appears to stop the first two "pages" from loading thumbnails, besides that it appears to have no effect.
    """

    bca = "sawffmi"
    """
    Appears to stop the first two "pages" from loading thumbnails, besides that it appears to have no effect.
    """

    daa = "multiselectEnabled"
    """
    Same effect as :py:attr:`~Feature.MULTISELECT_ENABLED`: Allows the user to select multiple files, also appears to stop the first two "pages" from loading thumbnails.
    """

    G_DOLLAR = "ignoreLimits"
    """
    Makes the picker window super small, making it impossible to select a file depending on the platform.
    """

    iaa = "navHidden"
    """
    Same effect as :py:attr:`~Feature.NAV_HIDDEN`: Hides the drive filepath and the tabs for switching between views. If the navigation pane is hidden, users can only select from the first view chosen. It also appears to stop the first two "pages" from loading thumbnails.
    """

    kaa = "newDriveView"
    """
    Appears to have new effect.
    """

    laa = "newHorizNav"
    """
    Appears to have new effect.
    """

    m9 = "showAttach"
    """
    Shows a switch between "Insert as Drive Link" and "Insert as Attachment" in the Google Picker. Appears to have no effect on the returned data.
    """

    maa = "newPhotoGridView"
    """
    Appears to have no effect.
    """

    n9 = "edbe"
    """
    Appears to have no effect.
    """

    oca = "sdr"
    """
    Appears to have no effect.
    """

    qca = "std"
    """
    Appears to stop the first two "pages" from loading thumbnails, besides that it appears to have no effect.
    """
    
    waa = "odv"
    """
    Changes the picker window to a more old school design with non-uniform thumbnails, thicker borders and moving the tabs from the top to the left side.
    """