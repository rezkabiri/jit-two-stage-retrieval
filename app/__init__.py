# app/__init__.py
from google.adk import App
from .agent import root_agent

# Initialize the ADK App
# The name MUST match the package name "app"
app = App(root_agent=root_agent, name="app")
