import logging
from typing import Any, Dict

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse

from . import config, schemes
from .policies.requestenforcer import EnforceResult, RequestEnforcer


# setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-9s %(message)s"
)

app_config: config.Config = config.load_config()

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


@app.api_route(
    "/{path_name:path}",
    methods=["GET", "DELETE", "PATCH", "POST", "PUT", "HEAD", "OPTIONS", "CONNECT", "TRACE"]
)
async def catch_all(request: Request, path_name: str):
    enforce_result: EnforceResult = policy_checker.enforce(request)
    if not enforce_result.access_allowed:
        logger.info('The user does not have enough permissions. A blocked route: %s', path_name)
        raise HTTPException(detail='Content not found', status_code=404)

    return await redirect_user_request(request, enforce_result)


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
