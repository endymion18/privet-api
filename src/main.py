import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.app:app", host="localhost", log_level="info", reload=True)
