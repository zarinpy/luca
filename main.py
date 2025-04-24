#!/usr/bin/env python3
from contextlib import asynccontextmanager

import uvicorn
from br_py.base import br_lib_init
from br_py.do_log import log_d, log_e, log_i, log_w
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from api import api_router
from config import setting
from core.middlewares import (
    DBSessionMiddleware,
    DurationMiddleware,
    TimeoutMiddleware,
)
from core.renderer import CustomResponse


async def initialize_database() -> bool:
    async def is_table_raw(schema_name: str, table_name: str) -> bool:
        log_i(f"[*] Checking for [{schema_name}/{table_name}].")
        query = (
            f"SELECT COUNT(*) FROM {schema_name}.{table_name}"  # noqa: S608
        )
        count_result = await database.fetch_one(query)
        record_count = count_result[0] if count_result else 0
        if record_count == 0:  # noqa: SIM103
            return True
        return False

    async def execute_sql_file(filename: str) -> None:
        with open(filename, "r") as file:
            sql_commands = file.readlines()
            sql_commands = [command.strip() for command in sql_commands]

            for command in sql_commands:
                if not command:
                    pass
                # Replacing Dynamic Variables
                command = command.replace(
                    "$$BACKEND_ENDPOINT$$", setting.HOST_NAME
                )
                try:
                    await database.execute(query=command)
                except Exception as e:
                    log_i(
                        (
                            f"[-] Failed to execute SQL Command."
                            f"\n[SQL] {command}\n[Err] {e}"
                        ),
                    )

    raw_table_status = []
    check_tables = [
        ("public", "users"),
        ("public", "adapter"),
        ("public", "roles"),
        ("public", "city"),
    ]
    for each_table_status in check_tables:
        raw_table = await is_table_raw(
            each_table_status[0],
            each_table_status[1],
        )
        raw_table_status.append(raw_table)

    seed_table_records = [
        "scripts/seed/user_management.sql",
        "scripts/seed/web_crawler.sql",
        "scripts/seed/port.sql",
        "scripts/seed/adapter.sql",
        "scripts/seed/business_service.sql",
        "scripts/seed/category.sql",
        "scripts/seed/default_groups.sql",
        "scripts/seed/general_data.sql",
        "scripts/seed/location.sql",
        "scripts/seed/os_family.sql",
        "scripts/seed/os_name.sql",
        "scripts/seed/schedule.sql",
    ]
    if True not in raw_table_status:
        log_i("[+] All db records are updated.")
        return True

    for each_seed_data in seed_table_records:
        await execute_sql_file(each_seed_data)
    log_i("[+] Seed data inserted into DB.")
    return True


@asynccontextmanager
async def lifespan(apl: FastAPI):  # noqa: ARG001
    await br_lib_init(
        path_of_logs=setting.LOGS_PATH,
        log_to_file_level=setting.LOG_TO_FILE_LEVEL,
        log_to_std_out_level=setting.LOG_TO_STD_OUT_LEVEL,
        root_path=setting.ROOT_PATH,
        file_log_rotation_size=setting.FILE_LOG_ROTATION_SIZE,
        file_log_retention_duration=setting.FILE_LOG_RETENTION_DURATION,
    )
    await database.connect()
    await initialize_database()
    log_e("startup")
    log_w("startup")
    log_d("startup")
    log_i("startup")
    yield
    await database.disconnect()


app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"docExpansion": "none", "tryItOutEnabled": True},
    title="coreInspect API",
    description="",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redirect_slashes=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Timeout MiddleWare to handle timeout on all endpoints after 1:30h
app.add_middleware(
    TimeoutMiddleware,
    timeout=90 * 60,  # 01:30h timeout
    exclude_paths=[],  # Example: Exclude specific paths from the timeout
)

app.add_middleware(DurationMiddleware)
app.add_middleware(DBSessionMiddleware)
# app.add_middleware(RequestResponseLoggingMiddleware)


@app.exception_handler(HTTPException)
def http_exception_handler(
    request: Request,  # noqa: ARG001
    exc: HTTPException,
) -> CustomResponse:
    _error_status = list(range(400, 599))
    message_type = "success"

    if exc.status_code in _error_status:
        message_type = "error"

    return CustomResponse(
        status_code=exc.status_code,
        message=exc.detail,
        content={},
        message_type=message_type,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,  # noqa: ARG001
    exc: RequestValidationError,
) -> CustomResponse:
    errors = exc.errors()
    details = [{item["loc"][1]: item["msg"]} for item in errors]
    message = " ".join(item["msg"] for item in errors)
    return CustomResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message=message,
        details=details,
        message_type="error",
    )


app.include_router(router=api_router, prefix="/api/v1")


def main() -> None:
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=setting.HOST_PORT,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
        ssl_keyfile_password="aaaa",
    )


if __name__ == "__main__":
    main()
