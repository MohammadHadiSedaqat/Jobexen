from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.endpoints.v1 import user_router
from src.connections.sync_postgres import get_db_connection
from src.data.models import get_schema_queries
from fastapi_swagger import patch_fastapi

# app = FastAPI(
#     title="Jabexen API",
#     description="پلتفرم تخصص محور برای متخصصان و بلاگر های فنی",
#     version="1.0,0",
# )
app = FastAPI(
    title="Jobexen API",
    description="پلتفرم تخصص محور برای متخصصان و بلاگر های فنی",
    version="1.0,0",
    docs_url=None,
    swagger_ui_oauth2_redirect_url=None
)
patch_fastapi(app, docs_url="/swagger")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router , prefix="/api/v1")

app.include_router(user_router.profile_router , prefix="/api/v1")


@app.on_event("startup")
async def create_tables():
    print("داریم بررسی و میکنیم و جداول رو در دیتابیس ایجاد میکنیم!")
    conn = get_db_connection()
    if  conn:
        cursor = conn.cursor()
        queries = get_schema_queries()
        try:
            for table_name, query in queries.items():
                cursor.execute(query)
            print("✅ تمام جداول با موفقیت ساخته یا آپدیت شدند.")

        except Exception as e:
            print(f"❌ خطا در ساخت جداول: {e}")

        finally:
            cursor.close()
            conn.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Jobexen API - Version 1.0.0"}