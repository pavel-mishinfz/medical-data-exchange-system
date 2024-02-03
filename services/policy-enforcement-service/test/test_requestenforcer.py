import os
import unittest

import jwt
from starlette.requests import Request
from starlette.datastructures import Headers
from app.policies.requestenforcer import RequestEnforcer, Service, EnforceResult

TEST_POLICIES_CONFIG = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'test_policies.yaml'
)

TEST_JWT_SECRET = '4e7c09ff-f69e-45f0-8285-99f80a289320'

TEMPLATE_SERVICE = Service(
    name='template-service', entrypoint='http://template-service:5000/', inject_token_in_swagger=True
)

MEDICAL_CARD_SERVICE = Service(
    name='medical-card-service', entrypoint='http://medical-card-service:5000/', inject_token_in_swagger=True
)

USER_SERVICE = Service(
    name='user-service', entrypoint='http://user-service:5000/', inject_token_in_swagger=True
)


def build_request(
        method: str = "GET",
        server: str = "www.example.com",
        path: str = "/",
        headers: dict = None,
        body: str = None,
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
            return body

        request.body = request_body
    return request


class RequestEnforceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.policy_checker: RequestEnforcer = RequestEnforcer(
            TEST_POLICIES_CONFIG, TEST_JWT_SECRET
        )

    def test_templates_allow(self):
        # Admin
        request = self._prepare_request(21, 1, 'GET', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(21, 1, 'POST', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(21, 1, 'PUT', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(21, 1, 'DELETE', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string())

        # Doctor
        request = self._prepare_request(21, 2, 'GET', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(21, 2, 'POST', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(21, 2, 'PUT', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(21, 2, 'DELETE', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, TEMPLATE_SERVICE.entrypoint.unicode_string())

    def test_templates_denied(self):
        # Patient
        request = self._prepare_request(21, 3, 'GET', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(21, 3, 'POST', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(21, 3, 'PUT', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(21, 3, 'DELETE', '/templates')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

    def test_groups_allow(self):
        # Admin
        request = self._prepare_request(75, 1, 'GET', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(75, 1, 'POST', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(75, 1, 'PUT', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(75, 1, 'DELETE', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

    def test_groups_denied(self):
        # Doctor
        request = self._prepare_request(65, 2, 'GET', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 2, 'POST', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 2, 'PUT', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 2, 'DELETE', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        # Patient
        request = self._prepare_request(65, 3, 'GET', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 3, 'POST', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 3, 'PUT', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 3, 'DELETE', '/groups')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

    def test_users_allow(self):
        # Admin
        request = self._prepare_request(65, 1, 'GET', '/users/')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 1, 'PUT', '/users/')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 1, 'DELETE', '/users/')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

        # Doctor
        request = self._prepare_request(65, 2, 'GET', '/users/')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 2, 'PUT', '/users/me')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

        # Patient
        request = self._prepare_request(65, 3, 'GET', '/users/me')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 3, 'PUT', '/users/me')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

    def test_users_denied(self):
        # Doctor
        request = self._prepare_request(65, 2, 'GET', '/users/', make_headers=False)
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 2, 'PUT', '/users/', make_headers=False)
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 2, 'PUT', '/users/1')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 2, 'DELETE', '/users/1')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        # Patient
        request = self._prepare_request(65, 3, 'GET', '/users/me', make_headers=False)
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 3, 'PUT', '/users/me', make_headers=False)
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 3, 'PUT', '/users/1')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 3, 'DELETE', '/users/1')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

    def test_auth_allow(self):
        # Admin
        request = self._prepare_request(65, 1, 'POST', '/auth/', make_headers=False)
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

        # Doctor
        request = self._prepare_request(65, 2, 'POST', '/auth/', make_headers=False)
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

        # Patient
        request = self._prepare_request(65, 3, 'POST', '/auth/', make_headers=False)
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, USER_SERVICE.entrypoint.unicode_string())

    def test_cards_allow(self):
        # Admin
        request = self._prepare_request(65, 1, 'POST', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 1, 'GET', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 1, 'PUT', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 1, 'DELETE', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        # Doctor
        request = self._prepare_request(65, 2, 'GET', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 2, 'PUT', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        # Patient
        request = self._prepare_request(65, 3, 'GET', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

    def test_cards_denied(self):
        # Doctor
        request = self._prepare_request(65, 2, 'POST', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 2, 'DELETE', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        # Patient
        request = self._prepare_request(65, 3, 'POST', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 3, 'PUT', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 3, 'DELETE', '/cards')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

    def test_pages_allow(self):
        # Admin
        request = self._prepare_request(65, 1, 'GET', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 1, 'POST', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 1, 'PUT', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 1, 'DELETE', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        # Docotor
        request = self._prepare_request(65, 2, 'GET', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 2, 'POST', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 2, 'PUT', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        request = self._prepare_request(65, 2, 'DELETE', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

        # Patient
        request = self._prepare_request(65, 3, 'GET', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_allow(result, MEDICAL_CARD_SERVICE.entrypoint.unicode_string())

    def test_pages_denied(self):
        # Patient
        request = self._prepare_request(65, 3, 'POST', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 3, 'PUT', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

        request = self._prepare_request(65, 3, 'DELETE', '/pages')
        result = self.policy_checker.enforce(request)
        self._assert_access_denied(result)

    def test_services_list(self):
        expected_services = [USER_SERVICE, TEMPLATE_SERVICE, MEDICAL_CARD_SERVICE]

        def sort_list(target):
            return sorted(target, key=lambda i: i.name)

        self.assertListEqual(
            sort_list(self.policy_checker.services), sort_list(expected_services)
        )

    def _make_headers(self, age: int, group: int) -> dict:
        token = jwt.encode({
            'age': age,
            'group_id': group,
            'aud': ["fastapi-users:auth"]
        }, key=TEST_JWT_SECRET)
        return {
            "authorization": f'Bearer {token}'
        }

    def _prepare_request(
            self, age: int, group: int, method: str, path: str, make_headers: bool = True
    ) -> Request:
        headers = self._make_headers(age, group) if make_headers else {}
        return build_request(method=method, path=path, headers=headers)

    def _assert_access_allow(self, result: EnforceResult, entrypoint: str):
        self.assertTrue(result.access_allowed)
        self.assertEqual(result.redirect_service, entrypoint)

    def _assert_access_denied(self, result: EnforceResult):
        self.assertFalse(result.access_allowed)
        self.assertIsNone(result.redirect_service)
