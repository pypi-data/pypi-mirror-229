
from streamlit_render.core.frame import new_frame as _new_frame
from streamlit_render.core.exceptions import *
from streamlit_render.modules import *
from streamlit_render.version import __version__

    
def elements(key: str) -> None:
    """Create a Streamlit Elements frame."""
    return _new_frame(key)