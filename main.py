from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello from WARMS Backend"}
@app.get("/ping")
async def ping():
    return{"message":"Health verified: Backend running"}