import os
import streamlit.components.v1 as components


parent_dir = os.path.dirname(os.path.abspath(__file__))

acecm = components.declare_component(
    "cookyjar",
    path=parent_dir
)

def sc(name, value, exp_days, comp_key=None):
    js_ex = f'setCookie(\'{name}\', \'{value}\', {exp_days})'
    if comp_key is None: comp_key=js_ex
    return acecm(js_expressions=js_ex, key=comp_key)

def gc(name, comp_key=None):
    if comp_key is None: comp_key=f'getCookie_{name}'
    return acecm(js_expressions=f'getCookie(\'{name}\')', key=comp_key)

