"""Main module."""
import uvicorn
from fastapi import FastAPI

from app.configs.main_config import HOST, PORT
from app.routers import orders

app = FastAPI()

app.include_router(orders.router)

if __name__ == '__main__':
    uvicorn.run('app.main:app', host=HOST, port=PORT, reload=True)
