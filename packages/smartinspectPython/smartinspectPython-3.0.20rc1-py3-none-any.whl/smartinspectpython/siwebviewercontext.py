"""
Module: siwebviewercontext.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description
| ---------- | ----------- | ----------------------
| 2023/05/30 | 3.0.0.0     | Initial Version.  

</details>
"""

# external package imports.
# none

# our package imports.
from .sitextcontext import SITextContext
from .siviewerid import SIViewerId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIWebViewerContext(SITextContext):
    """ 
    Represents the web viewer in the Console which can display HTML
    text content as web pages.

    The web viewer in the Console interprets the Log Entry Data
    as an HTML website.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class with a SIViewerId.Web.
        """

        # initialize base instance.
        super().__init__(SIViewerId.Web)

        # initialize instance.
        # nothing to do.
