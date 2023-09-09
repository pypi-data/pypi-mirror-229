import os
import streamlit.components.v1 as components

_RELEASE = os.environ.get("RELEASE", False)

_RELEASE = True
if not _RELEASE:
    _cookie_component = components.declare_component(
        name="cookie_component",
        url="http://localhost:3001"
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _cookie_component = components.declare_component("cookie_component", path=build_dir)

def cookie_handler(value, name="Streamlit", key=None):
    return _cookie_component(value=value, name=name, default=0)


