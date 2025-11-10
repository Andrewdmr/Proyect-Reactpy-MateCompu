from reactpy import component, html
from reactpy.backend.fastapi import configure
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from components.grafo_components import GrafoInput

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@component
def App():
    return html.div(
        html.link({"rel": "stylesheet", "href": "/static/styles.css"}),
        GrafoInput()
    )

configure(app, App)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)