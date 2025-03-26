from fastapi import FastAPI
from routes.users import router as users_router
from routes.drugs import router as drugs_router
from routes.ddi import router as ddi_router
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

app = FastAPI()

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(drugs_router, prefix="/drugs", tags=["Drugs"])
app.include_router(ddi_router, prefix="/ddi", tags=["DDI"])

if __name__ == "__main__":
    print(f"Server is running at: http://{HOST}:{PORT}")
    uvicorn.run("main:app", host=HOST, port=int(PORT), reload=True)
