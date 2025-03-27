from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import FastAPI
from routes.users import router as users_router
from routes.drugs import router as drugs_router
from routes.ddi import router as ddi_router
import uvicorn
from config import HOST, PORT


app = FastAPI()

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(drugs_router, prefix="/drugs", tags=["Drugs"])
app.include_router(ddi_router, prefix="/ddi", tags=["DDI"])

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Custom Swagger UI",
        swagger_ui_version="0.1.0",  # Thay đổi version tại đây
    )


if __name__ == "__main__":
    print(f"Server is running at: http://{HOST}:{PORT} !!!!")
    uvicorn.run("main:app", host=HOST, port=int(PORT), reload=True)
