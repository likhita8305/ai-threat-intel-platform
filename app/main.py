from fastapi import FastAPI
from . import models, routes, assessments # Import the new assessments file
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cyber Threat Intelligence Platform")

# Include the routers from both files
app.include_router(routes.router)
app.include_router(assessments.router) # Add the new assessments router

@app.get("/")
def read_root():
    return {"message": "Server is running and database is set up!"}
