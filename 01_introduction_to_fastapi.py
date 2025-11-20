from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "this is my first code of fastapi."}
    



@app.get("/name")
def get_name():
    return {"prasad": "FastAPI Application"}