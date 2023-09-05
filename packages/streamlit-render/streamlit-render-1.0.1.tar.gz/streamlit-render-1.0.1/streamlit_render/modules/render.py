from streamlit_render.core.frame import new_element
import streamlit as st
import json
class Render:  
    def parse(self, data, dashboard=False):       
        file = fileExtension = None
        if data is not None:
            file = data.getvalue().decode("utf-8")
            fileExtension = data.name.split(".")[-1]
        new_element("renderObject", "Render")(
            file=file, 
            fileExtension=fileExtension,  
            dashboard=dashboard,      

        )
    def load(self, file=None, fileExtension=None, dashboard=False):
        new_element("renderObject", "Render")(
            file=file, 
            fileExtension=fileExtension,         
            dashboard=dashboard,
        )
        