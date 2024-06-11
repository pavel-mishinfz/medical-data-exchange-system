import os
import uuid
import unittest
import json

import jwt
from starlette.requests import Request
from starlette.datastructures import Headers
from app.policies.requestenforcer import RequestEnforcer, Service, EnforceResult
from app.app import get_db

TEST_POLICIES_CONFIG = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'test_policies.yaml'
)

TEST_JWT_SECRET = '4e7c09ff-f69e-45f0-8285-99f80a289320'

USER_SERVICE = Service(
    name='user-service', entrypoint='http://127.0.0.1:8000/', inject_token_in_swagger=True
)

TEMPLATE_SERVICE = Service(
    name='template-service', entrypoint='http://127.0.0.1:8001/', inject_token_in_swagger=True
)

MEDICAL_CARD_SERVICE = Service(
    name='medical-card-service', entrypoint='http://127.0.0.1:8002/', inject_token_in_swagger=True
)

HEALTH_DIARY_SERVICE = Service(
    name='health-diary-service', entrypoint='http://127.0.0.1:8003/', inject_token_in_swagger=True
)

RECORD_SERVICE = Service(
    name='record-service', entrypoint='http://127.0.0.1:8004/', inject_token_in_swagger=True
)

CHAT_SERVICE = Service(
    name='chat-service', entrypoint='http://127.0.0.1:8005/', inject_token_in_swagger=True
)




def build_request(
        method: str = "GET",
        server: str = "www.example.com",
        path: str = "/",
        headers: dict = None,
        body: dict = None,
) -> Request:
    """
    Build mock-request based on Starlette Request
    """
    if headers is None:
        headers = {}
    request = Request(
        {
            "type": "http",
            "path_params": {'path_name': path[1:]},
            "path": path,
            "headers": Headers(headers).raw,
            "http_version": "1.1",
            "method": method,
            "scheme": "https",
            "client": ("127.0.0.1", 8080),
            "server": (server, 443),
        }
    )
    if body:
        async def request_body():
            return json.dumps(body).encode('utf-8')

        request.body = request_body
    return request


class RequestEnforceTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.policy_checker: RequestEnforcer = RequestEnforcer(
            TEST_POLICIES_CONFIG, TEST_JWT_SECRET
        )
        self.session = next(get_db())

        self.user_id = '4ef277c1-94fd-4045-b6a6-c126bc851b0e'
        self.outsider_user_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'

        self.card_id = 11
        self.page_id = '621f9c86-4d1e-47a5-b531-378c13e514be'
        self.template_id = 24

    async def asyncTearDown(self) -> None:
        self.session.close()

    # template-service
    async def test_templates_allow(self):
        # Admin
        request = self._prepare_request(self.user_id, 1, 'POST', '/templates')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string(), 'Admin POST /templates')
    
        request = self._prepare_request(self.user_id, 1, 'GET', '/templates')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string(), 'Admin GET /templates')

        request = self._prepare_request(self.user_id, 1, 'GET', '/templates/1')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string(), 'Admin GET /templates/1')

        request = self._prepare_request(self.user_id, 1, 'PUT', '/templates/1')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string(), 'Admin PUT /templates/1')

        request = self._prepare_request(self.user_id, 1, 'DELETE', '/templates/1')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string(), 'Admin DELETE /templates/1')

        # Doctor
        request = self._prepare_request(self.user_id, 2, 'GET', '/templates')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string(), 'Doctor GET /templates')

        request = self._prepare_request(self.user_id, 2, 'GET', '/templates/1')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string(), 'Doctor GET /templates/1')

        # Patient
        request = self._prepare_request(self.user_id, 3, 'GET', '/templates/1')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string(), 'Patient GET /templates/1')

    async def test_templates_denied(self):
        # Doctor
        request = self._prepare_request(self.user_id, 2, 'POST', '/templates')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, 'Doctor POST /templates')

        request = self._prepare_request(self.user_id, 2, 'PUT', '/templates/1')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, 'Doctor PUT /templates/1')

        request = self._prepare_request(self.user_id, 2, 'DELETE', '/templates/1')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, 'Doctor DELETE /templates/1')

        # Patient
        request = self._prepare_request(self.user_id, 3, 'POST', '/templates')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, 'Patient POST /templates')
    
        request = self._prepare_request(self.user_id, 3, 'GET', '/templates')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, 'Patient GET /templates')

        request = self._prepare_request(self.user_id, 3, 'PUT', '/templates/1')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, 'Patient PUT /templates/1')

        request = self._prepare_request(self.user_id, 3, 'DELETE', '/templates/1')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, 'Patient DELETE /templates/1')

    # medical-card-service

    # cards
    async def test_cards_allow(self):
        # Admin
        request = self._prepare_request(self.user_id, 1, 'POST', '/cards')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), 'Admin POST /cards')
    
        request = self._prepare_request(self.user_id, 1, 'GET', '/cards')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), 'Admin GET /cards')

        request = self._prepare_request(self.user_id, 1, 'GET', f'/cards/{self.card_id}')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), f'Admin GET /cards/{self.card_id}')

        request = self._prepare_request(self.user_id, 1, 'PATCH', f'/cards/{self.card_id}')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), f'Admin PATCH /cards/{self.card_id}')

        request = self._prepare_request(self.user_id, 1, 'DELETE', f'/cards/{self.card_id}')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), f'Admin DELETE /cards/{self.card_id}')

        # Doctor
        request = self._prepare_request(self.user_id, 2, 'GET', '/cards')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), 'Doctor GET /cards')

        request = self._prepare_request(self.user_id, 2, 'GET', f'/cards/{self.card_id}')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), f'Doctor GET /cards/{self.card_id}')

        # Patient
        request = self._prepare_request(self.user_id, 3, 'GET', f'/cards/me/{self.user_id}')
        result = await self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), f'Patient GET /cards/me/{self.user_id}')

    async def test_cards_denied(self):
        # Admin
        request = self._prepare_request(self.user_id, 1, 'GET', f'/cards/me/{self.user_id}')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, f'Admin GET /cards/me/{self.user_id}')

        # Doctor
        request = self._prepare_request(self.user_id, 2, 'POST', '/cards')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, 'Doctor POST /cards')

        request = self._prepare_request(self.user_id, 2, 'PATCH', f'/cards/{self.card_id}')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, f'Doctor PATCH /cards/{self.card_id}')

        request = self._prepare_request(self.user_id, 2, 'DELETE', f'/cards/{self.card_id}')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, f'Doctor DELETE /cards/{self.card_id}')

        request = self._prepare_request(self.user_id, 2, 'GET', f'/cards/me/{self.user_id}')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, f'Doctor GET /cards/me/{self.user_id}')

        # Patient
        request = self._prepare_request(self.user_id, 3, 'GET', f'/cards/me/{self.outsider_user_id}')
        result = await self.policy_checker.enforce(request)
        self._assert_access_denied(result, f'Patient GET /cards/me/{self.outsider_user_id}')

    # pages
    async def test_pages_allow(self):
        # Doctor
        request = self._prepare_request(self.user_id, 2, 'POST', f'/pages/card/{self.card_id}/template/{self.template_id}', body={"id_doctor": self.user_id})
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), f'Doctor POST /pages/card/{self.card_id}/template/{self.template_id}')
    
        request = self._prepare_request(self.user_id, 2, 'GET', f'/pages/card/{self.card_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), f'Doctor GET /pages/card/{self.card_id}')

        request = self._prepare_request(self.user_id, 2, 'PUT', f'/pages/{self.page_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), f'Doctor PUT /pages/{self.page_id}')

        request = self._prepare_request(self.user_id, 2, 'DELETE', f'/pages/{self.page_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), f'Doctor DELETE /pages/{self.page_id}')

        # Patient
        card_owner_id = '993d8c4b-fbdf-437b-bb1d-c7fae756b9d3'
        request = self._prepare_request(card_owner_id, 3, 'GET', f'/pages/card/{self.card_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string(), f'Patient GET /pages/card/{self.card_id}')

    async def test_pages_denied(self):
        # Doctor
        request = self._prepare_request(self.user_id, 2, 'POST', f'/pages/card/{self.card_id}/template/{self.template_id}', body={"id_doctor": self.outsider_user_id})
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Doctor POST /pages/card/{self.card_id}/template/{self.template_id}')

        request = self._prepare_request(self.user_id, 2, 'PUT', f'/pages/{self.outsider_user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Doctor PUT /pages/{self.outsider_user_id}')

        request = self._prepare_request(self.user_id, 2, 'DELETE', f'/pages/{self.outsider_user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Doctor DELETE /pages/{self.outsider_user_id}')

        # Patient
        request = self._prepare_request(self.user_id, 3, 'POST', f'/pages/card/{self.card_id}/template/{self.template_id}', body={"id_doctor": self.outsider_user_id})
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Doctor POST /pages/card/{self.card_id}/template/{self.template_id}')

        request = self._prepare_request(self.outsider_user_id, 3, 'GET', f'/pages/card/{self.card_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Patient GET /pages/card/{self.card_id}')

        request = self._prepare_request(self.user_id, 3, 'PUT', f'/pages/{self.page_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Doctor PUT /pages/{self.page_id}')

        request = self._prepare_request(self.user_id, 3, 'DELETE', f'/pages/{self.page_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Doctor DELETE /pages/{self.page_id}')

    # health-diary-service
    async def test_health_diary_allow(self):
        # Doctor
        patient_id = 'e6023280-4ba4-4bbf-9fcd-4b8f38c3f1b1'
        request = self._prepare_request(self.user_id, 2, 'GET', f'/diaries/user/{patient_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, HEALTH_DIARY_SERVICE.entrypoint.unicode_string(), f'Doctor GET /diaries/user/{patient_id}')

        # Patient
        request = self._prepare_request(patient_id, 3, 'GET', f'/diaries/user/{patient_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, HEALTH_DIARY_SERVICE.entrypoint.unicode_string(), f'Patient GET /diaries/user/{patient_id}')

        request = self._prepare_request(patient_id, 3, 'POST', f'/diaries/user/{patient_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, HEALTH_DIARY_SERVICE.entrypoint.unicode_string(), f'Patient POST /diaries/user/{patient_id}')

        page_diary_id = '58b784b3-fe83-4424-8865-41a201ede2fc'
        request = self._prepare_request(patient_id, 3, 'PATCH', f'/diaries/{page_diary_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, HEALTH_DIARY_SERVICE.entrypoint.unicode_string(), f'Patient PATCH /diaries/{page_diary_id}')

        request = self._prepare_request(patient_id, 3, 'DELETE', f'/diaries/{page_diary_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, HEALTH_DIARY_SERVICE.entrypoint.unicode_string(), f'Patient DELETE /diaries/{page_diary_id}')

    async def test_health_diary_denied(self):
        # Patient
        patient_id = 'e6023280-4ba4-4bbf-9fcd-4b8f38c3f1b1'
        request = self._prepare_request(patient_id, 3, 'GET', f'/diaries/user/{self.outsider_user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Patient GET /diaries/user/{self.outsider_user_id}')

        request = self._prepare_request(patient_id, 3, 'POST', f'/diaries/user/{self.outsider_user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Patient POST /diaries/user/{self.outsider_user_id}')

        request = self._prepare_request(patient_id, 3, 'PATCH', f'/diaries/{self.outsider_user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Patient PATCH /diaries/{self.outsider_user_id}')

        request = self._prepare_request(patient_id, 3, 'DELETE', f'/diaries/{self.outsider_user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Patient DELETE /diaries/{self.outsider_user_id}')

    # record-service

    # records
    async def test_records_allow(self):
        # Admin
        request = self._prepare_request(self.user_id, 1, 'GET', '/records')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, RECORD_SERVICE.entrypoint.unicode_string(), 'Admin GET /records')

        record_id = 'e6023280-4ba4-4bbf-9fcd-4b8f38c3f1b6'
        request = self._prepare_request(self.user_id, 1, 'DELETE', f'/records/{record_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, RECORD_SERVICE.entrypoint.unicode_string(), f'Doctor GET /records/{record_id}')

        # Doctor
        request = self._prepare_request(self.user_id, 2, 'GET', f'/records/user/{self.user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, RECORD_SERVICE.entrypoint.unicode_string(), f'Doctor GET /records/user/{self.user_id}')

        # Patient
        request = self._prepare_request(self.user_id, 3, 'GET', f'/records/user/{self.user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, RECORD_SERVICE.entrypoint.unicode_string(), f'Patient GET /records/user/{self.user_id}')

        request = self._prepare_request(self.user_id, 3, 'POST', '/records', body={"id_user": self.user_id})
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, RECORD_SERVICE.entrypoint.unicode_string(), 'Patient POST /records')

    async def test_records_denied(self):
        # Doctor
        request = self._prepare_request(self.user_id, 2, 'GET', f'/records/user/{self.outsider_user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Doctor GET /records/user/{self.outsider_user_id}')

        # Patient
        request = self._prepare_request(self.user_id, 3, 'GET', f'/records/user/{self.outsider_user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Patient GET /records/user/{self.outsider_user_id}')

        request = self._prepare_request(self.user_id, 3, 'POST', '/records', body={"id_user": self.outsider_user_id})
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, 'Patient POST /records')

    # chat-service
    
    # chat
    async def test_schedules_allow(self):
        # Doctor
        request = self._prepare_request(self.user_id, 2, 'POST', '/chats')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, CHAT_SERVICE.entrypoint.unicode_string(), 'Doctor POST /chats')

        request = self._prepare_request(self.user_id, 2, 'GET', f'/chats/{self.user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, CHAT_SERVICE.entrypoint.unicode_string(), f'Doctor GET /chats/{self.user_id}')

        # Patient
        request = self._prepare_request(self.user_id, 3, 'GET', f'/chats/{self.user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_allow(result, CHAT_SERVICE.entrypoint.unicode_string(), f'Patient GET /chats/{self.user_id}')

    async def test_schedules_denied(self):
        # Doctor
        request = self._prepare_request(self.user_id, 2, 'GET', f'/chats/{self.outsider_user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Doctor GET /chats/{self.outsider_user_id}')

        # Patient
        request = self._prepare_request(self.user_id, 3, 'GET', f'/chats/{self.outsider_user_id}')
        result = await self.policy_checker.enforce(request, self.session)
        self._assert_access_denied(result, f'Patient GET /chats/{self.outsider_user_id}')

    def test_services_list(self):
        expected_services = [USER_SERVICE, TEMPLATE_SERVICE, MEDICAL_CARD_SERVICE, HEALTH_DIARY_SERVICE, RECORD_SERVICE, CHAT_SERVICE]

        def sort_list(target):
            return sorted(target, key=lambda i: i.name)

        self.assertListEqual(
            sort_list(self.policy_checker.services), sort_list(expected_services)
        )

    def _make_headers(self, user_id: uuid.UUID, group: int) -> dict:
        token = jwt.encode({
            'sub': user_id,
            'group_id': group,
            'aud': ["fastapi-users:auth"]
        }, key=TEST_JWT_SECRET)
        return {
            "authorization": f'Bearer {token}'
        }

    def _prepare_request(
            self, user_id: uuid.UUID, group: int, method: str, path: str, make_headers: bool = True, body: dict = None
    ) -> Request:
        headers = self._make_headers(user_id, group) if make_headers else {}
        return build_request(method=method, path=path, headers=headers, body=body)

    def _assert_access_allow(self, result: EnforceResult, entrypoint: str, errorMessage: str):
        self.assertTrue(result.access_allowed, errorMessage)
        self.assertEqual(result.redirect_service, entrypoint)

    def _assert_access_denied(self, result: EnforceResult, errorMessage: str):
        self.assertFalse(result.access_allowed, errorMessage)
        self.assertIsNone(result.redirect_service)
