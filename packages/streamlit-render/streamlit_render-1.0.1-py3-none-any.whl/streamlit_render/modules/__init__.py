from streamlit_render.modules.render import Render
from streamlit_render.modules.callbacks import sync, lazy, partial
from streamlit_render.modules.dashboard import Dashboard
from streamlit_render.modules.editors import Editors
from streamlit_render.modules.events import Events
from streamlit_render.modules.html import HTML
from streamlit_render.modules.media import Media
from streamlit_render.modules.mui import MUI
from streamlit_render.modules.nivo import Nivo



__all__ = [
    "dashboard",
    "partial",
    "editor",
    "render",
    "media",
    "event",
    "nivo",
    "sync",
    "html",
    "lazy",
    "mui",
]

render = Render()
dashboard = Dashboard()
editor = Editors()
event = Events()
html = HTML()
media = Media()
mui = MUI()
nivo = Nivo()