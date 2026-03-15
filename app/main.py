# app/main.py
from google.adk import App
from .agent import root_agent

# Initialize the ADK App
# The runner will find this object
app = App(root_agent=root_agent, name="app")
