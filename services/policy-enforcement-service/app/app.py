import logging
from typing import Any, Dict
import websockets
import asyncio

import httpx
from fastapi import FastAPI, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from . import config, schemes
from .policies.requestenforcer import EnforceResult, RequestEnforcer
from .database.database import DB_INITIALIZER


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# setup logging
# logger = logging.getLogger(__name__)
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(levelname)-9s %(message)s"
# )

app_config: config.Config = config.load_config()

SessionLocal = DB_INITIALIZER.init_database(app_config.postgres_dsn.unicode_string())

policy_checker: RequestEnforcer = RequestEnforcer(
    app_config.policies_config_path, app_config.jwt_secret.get_secret_value()
)


class App(FastAPI):
    def openapi(self) -> Dict[str, Any]:
        scheme_builder = schemes.SchemeBuilder(super().openapi())

        for target in policy_checker.services:
            resp = httpx.get(target.openapi_scheme)
            scheme_builder.append(resp.json(), inject_token_in_swagger=target.inject_token_in_swagger)
        return scheme_builder.result


app = App()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api_route(
    "/{path_name:path}",
    methods=["GET", "DELETE", "PATCH", "POST", "PUT", "HEAD", "OPTIONS", "CONNECT", "TRACE"]
)
async def catch_all(request: Request, path_name: str, db: Session = Depends(get_db)):
    enforce_result: EnforceResult = await policy_checker.enforce(request, db)
    if not enforce_result.access_allowed:
        # logger.info('The user does not have enough permissions. A blocked route: %s', path_name)
        raise HTTPException(detail='Метод не доступен', status_code=404)

    return await redirect_user_request(request, enforce_result)


@app.websocket(
    "/{path_name:path}",
)
async def catch_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    enforce_result, chat_id, client_id = await policy_checker.enforce_websocket(websocket, db)
    if not enforce_result.access_allowed:
        await websocket.close(code=1008)
        raise HTTPException(detail='Метод не доступен', status_code=404)

    location = enforce_result.redirect_service.split('/')[2]
    target_url = f"ws://{location}/ws/{chat_id}/{client_id}"
    await redirect_websocket(websocket, target_url)


async def redirect_user_request(request: Request, enforce_result: EnforceResult):
    client = httpx.AsyncClient(base_url=enforce_result.redirect_service)
    url = httpx.URL(path=request.url.path,
                    query=request.url.query.encode("utf-8"))
    rp_req = client.build_request(request.method, url,
                                  headers=request.headers.raw,
                                  content=await request.body())
    rp_resp = await client.send(rp_req, stream=True)
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers
    )


async def redirect_websocket(client_ws: WebSocket, target_url: str):
    await client_ws.accept()

    async with websockets.connect(target_url) as server_ws:
        async def forward_client_to_server(client_ws, server_ws):
            try:
                while True:
                    data = await client_ws.receive_text()
                    await server_ws.send(data)
            except WebSocketDisconnect:
                await server_ws.close()

        async def forward_server_to_client(client_ws, server_ws):
            try:
                while True:
                    data = await server_ws.recv()
                    await client_ws.send_text(data)
            except websockets.ConnectionClosed:
                await client_ws.close()

        try:
            await asyncio.gather(
                forward_client_to_server(client_ws, server_ws),
                forward_server_to_client(client_ws, server_ws),
            )
        except Exception as e:
            print(f"Error in redirect_websocket: {e}")