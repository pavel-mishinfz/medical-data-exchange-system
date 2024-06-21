import os
import uuid
import copy
import re
import tempfile

import casbin
import jwt
import yaml
from fastapi import Request, WebSocket
from pydantic.dataclasses import dataclass
from sqlalchemy.orm import Session

from .policiesconfig import PoliciesConfig, Policy, Service
from ..crud import crud_card, crud_chat, crud_meeting, crud_message, crud_record


@dataclass
class EnforceResult:
    access_allowed: bool = False
    redirect_service: str = None


class RequestEnforcer:
    def __init__(self, config_path: str, jwt_secret: str) -> None:
        self.jwt_secret: str = jwt_secret
        self.config: PoliciesConfig = self.__load_config(config_path=config_path)
        self.enforcer: casbin.Enforcer = self.__create_enforcer()

    async def enforce_websocket(self, websocket: WebSocket, db: Session):
        access_allowed, service_name, chat_id, client_id = await self.__check_by_policy_websocket(websocket, db)
        if access_allowed:
            service = self.__get_service_by_name(service_name)
            return EnforceResult(True, service.entrypoint.unicode_string()), chat_id, client_id
        return EnforceResult(), chat_id, client_id
        
    async def enforce(self, request: Request, db: Session | None = None):
        in_whitelist, service_name = self.__is_request_in_whitelist(request)
        if in_whitelist:
            service = self.__get_service_by_name(service_name)
            return EnforceResult(True, service.entrypoint.unicode_string())

        access_allowed, service_name = await self.__check_by_policy(request, db)
        if access_allowed:
            service = self.__get_service_by_name(service_name)
            return EnforceResult(True, service.entrypoint.unicode_string())
        return EnforceResult()

    def __load_config(self, config_path: str) -> PoliciesConfig:
        with open(config_path) as file:
            data = yaml.safe_load(file)
            return PoliciesConfig(**data)

    def __create_enforcer(self) -> casbin.Enforcer:
        model_conf = self.__make_model_temp_file()
        policy_conf = self.__make_policy_temp_file()
        return casbin.Enforcer(model_conf, policy_conf)

    def __make_model_temp_file(self) -> str:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        with open(tmp.name, 'w') as f:
            f.write(self.config.model)
        tmp.close()

        return tmp.name

    def __make_policy_temp_file(self) -> str:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        with open(tmp.name, 'w') as f:
            f.writelines(
                list(f'p, {p.rule}, {p.resource}, {p.methods}\n' for p in self.config.policies if not p.white_list)
            )
        tmp.close()

        return tmp.name

    def __is_request_in_whitelist(self, request: Request) -> tuple[bool, str] | tuple[bool, None]:
        resource = '/' + request.path_params['path_name']
        for p in self.whitelist_policies:
            if re.match(p.resource, resource) is not None and request.method in p.method_list:
                return True, p.service
        return False, None

    def __extract_token_data(self, request: Request) -> dict | None:
        try:
            if 'authorization' in request.headers:
                token = request.headers['authorization'].split(' ')[1]
                return jwt.decode(token, self.jwt_secret, algorithms=["HS256"], audience=["fastapi-users:auth"])
        except:
            return None

    @staticmethod
    async def __get_request_body(request: Request):
        result = {}

        try:  # if body does not exist
            result.update(await request.json())
        except Exception as _exc:
            pass

        return result

    def __enrich_token_data(self, token_data: dict, resource_data: dict, db: Session):
        result = copy.deepcopy(token_data)
        user_id = uuid.UUID(token_data['sub'])

        # Add empty available pages of medical card
        result.update({ 'available_pages_of_medical_card': [] })

        # Add empty available pages of health diary
        result.update({ 'available_pages_of_health_diary': [] })

        # Add empty available chats
        result.update({ 'available_chats': [] })

        # Add empty available messages
        result.update({ 'available_messages': [] })

        # Add empty available records
        result.update({ 'available_records': [] })

        page_id = resource_data['params'].get('page_id', None)
        if page_id:
            # Add available pages of medical card
            available_pages_of_medical_card = crud_card.get_available_pages_of_medical_card(db=db, doctor_id=user_id)
            result['available_pages_of_medical_card'].extend([str(page) for page in available_pages_of_medical_card])
        
        card_id = resource_data['params'].get('card_id', None)
        if card_id:
            card = crud_card.get_card(db=db, card_id=card_id)
            # Add card owner id
            result.update({'card_owner_id': str(card.id_user)}) 

        page_diary_id = resource_data['params'].get('page_diary_id', None)
        if page_diary_id:
            # Add available pages of health diary
            available_pages_of_health_diary = crud_card.get_available_pages_of_health_diary(db=db, user_id=user_id)
            result['available_pages_of_health_diary'].extend([str(page) for page in available_pages_of_health_diary])

        chat_id = resource_data['params'].get('chat_id', None)
        if chat_id:
            available_chats = crud_chat.get_available_chats(db=db, user_id=user_id)
            # Add available chats
            result['available_chats'].extend([chat for chat in available_chats])
            result['available_chats'].extend([str(chat) for chat in available_chats])

        message_id = resource_data['params'].get('message_id', None)
        if message_id:
            available_messages = crud_message.get_available_messages(db=db, user_id=user_id)
            # Add available messages
            result['available_messages'].extend([str(msg) for msg in available_messages])

        meeting_id = resource_data['params'].get('meeting_id', None)
        if meeting_id:
            available_records = crud_record.get_available_records(db=db, user_id=user_id)
            # Add available records
            result['available_records'].extend([str(record) for record in available_records])
            
            meeting = crud_meeting.get_meeting(db, meeting_id)
            # Add record id
            result.update({'record_id': str(meeting.record_id)})

        return result

    @staticmethod
    def __get_data_by_pattern(resource: str, pattern: str):
        result = re.search(pattern, resource)
        if result is not None:
            return result.groupdict()
        return {}

    def __get_resource_data_by_pattern(self, resource: str, method: str) -> dict:
        for p in self.config.policies:
            if re.fullmatch(p.resource, resource) is not None and method in p.method_list:
                if p.resource_pattern is None:
                    break
                return self.__get_data_by_pattern(resource, p.resource_pattern)
        return {}

    async def __check_by_policy(self, request: Request, db: Session | None = None) -> tuple[bool, str] | tuple[bool, None]:
        token_data = self.__extract_token_data(request)

        if token_data is None:
            return False, None

        resource = '/' + request.path_params['path_name']
        resource_data = {
            'resource': resource,
            'params': {},
            'body': {}
        }
        resource_data['params'].update(self.__get_resource_data_by_pattern(resource, request.method))
        resource_data['body'].update(await self.__get_request_body(request))
        
        token_data = self.__enrich_token_data(token_data, resource_data, db)
        access_allowed = self.enforcer.enforce(token_data, resource_data, request.method)
        if access_allowed is False:
            return False, None

        for p in self.enforcing_policies:
            if re.match(p.resource, resource) is not None and request.method in p.method_list:
                return True, p.service

        return True, None

    async def __check_by_policy_websocket(
            self, websocket: WebSocket, db: Session
        ) -> tuple[bool, str, int, uuid.UUID] | tuple[bool, None, None, None]:

        websocket_method = 'GET'
        token = websocket.query_params.get('token', None)

        if token is None:
            return False, None, None, None

        token_data = jwt.decode(token, self.jwt_secret, algorithms=["HS256"], audience=["fastapi-users:auth"])

        resource = '/' + websocket.path_params['path_name']
        resource_data = {
            'resource': resource,
            'params': {},
            'body': {}
        }
        resource_data['params'].update(self.__get_resource_data_by_pattern(resource, websocket_method))

        token_data = self.__enrich_token_data(token_data, resource_data, db)
        access_allowed = self.enforcer.enforce(token_data, resource_data, websocket_method)
        if access_allowed is False:
            return False, None, None, None

        for p in self.enforcing_policies:
            if re.match(p.resource, resource) is not None and websocket_method in p.method_list:
                return True, p.service, int(resource_data['params']['chat_id']), resource_data['params']['user_id']

        return True, None, None, None

    def __get_service_by_name(self, service_name: str) -> Service | None:
        for s in self.config.services:
            if s.name == service_name:
                return s
        return None

    @property
    def service_schemes(self) -> list[str]:
        return [s.openapi_scheme for s in self.config.services]

    @property
    def services(self) -> list[Service]:
        return [s for s in self.config.services]

    @property
    def whitelist_resources(self) -> list[str]:
        return [p.resource for p in self.config.policies if p.white_list]

    @property
    def whitelist_policies(self) -> list[Policy]:
        return [p for p in self.config.policies if p.white_list]

    @property
    def enforcing_policies(self) -> list[Policy]:
        return [p for p in self.config.policies if not p.white_list]
