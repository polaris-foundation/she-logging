import uvicorn

from she_logging import SHE_LOGGING_CONFIG

if __name__ == "__main__":
    uvicorn.run(
        "tests.scripts.fastapi_app:app",
        host="127.0.0.1",
        port=8000,
        log_config=SHE_LOGGING_CONFIG,
        workers=3,
    )
