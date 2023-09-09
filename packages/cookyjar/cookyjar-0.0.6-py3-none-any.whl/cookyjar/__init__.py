import os
import streamlit.components.v1 as components

_RELEASE = os.environ.get("RELEASE", False)
_RELEASE = True

if not _RELEASE:
    _cookyjar = components.declare_component(
        name="cookyjar",
        url="http://localhost:3001"
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _cookyjar = components.declare_component("cookyjar", path=build_dir)

def cookie_handler(value="ACE-APPS", name="Streamlit", type="getter"):
    return _cookyjar(value=value, name=name, type=type)

