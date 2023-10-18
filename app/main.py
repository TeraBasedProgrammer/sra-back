from fastapi import FastAPI


app = FastAPI()


@app.get("/something")
async def get_hyina() -> None:
    return {"something": 123}