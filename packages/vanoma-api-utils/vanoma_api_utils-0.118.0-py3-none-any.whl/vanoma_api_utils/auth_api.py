from typing import Any, Dict
from requests import Response
from django.conf import settings
from rest_framework import status
from vanoma_api_utils.http import client
from djangorestframework_camel_case.util import camelize  # type: ignore
from .exceptions import BackendServiceException


class AuthApiException(BackendServiceException):
    pass


def create_actor(data: Dict[str, Any]) -> Response:
    response = client.post(
        f"{settings.VANOMA_AUTH_API_URL}/actors",
        data=camelize(data),
    )

    if not response.ok:
        json = response.json()
        raise AuthApiException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            json["error_code"],
            json["error_message"],
        )

    return response


def get_auth_tokens(data: Dict[str, Any]) -> Response:
    response = client.post(
        f"{settings.VANOMA_AUTH_API_URL}/auth-tokens",
        data=camelize(data),
    )

    if not response.ok:
        json = response.json()
        raise AuthApiException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            json["error_code"],
            json["error_message"],
        )

    return response
