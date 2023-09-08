from typing import Any, Dict
from requests import Response
from django.conf import settings
from rest_framework import status
from vanoma_api_utils.http import client
from djangorestframework_camel_case.util import camelize  # type: ignore
from .exceptions import BackendServiceException


class CommunicationApiException(BackendServiceException):
    pass


def send_sms(data: Dict[str, Any]) -> Response:
    response = client.post(
        f"{settings.VANOMA_COMMUNICATION_API_URL}/sms", data=camelize(data)
    )

    if not response.ok:
        json = response.json()
        raise CommunicationApiException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            json["errorCode"],
            json["errorMessage"],
        )

    return response


def send_email(data: Dict[str, Any]) -> Response:
    response = client.post(
        f"{settings.VANOMA_COMMUNICATION_API_URL}/email", data=camelize(data)
    )

    if not response.ok:
        json = response.json()
        raise CommunicationApiException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            json["errorCode"],
            json["errorMessage"],
        )

    return response


def send_push(data: Dict[str, Any]) -> Response:
    response = client.post(
        f"{settings.VANOMA_COMMUNICATION_API_URL}/push", data=camelize(data)
    )

    if not response.ok:
        json = response.json()
        raise CommunicationApiException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            json["errorCode"],
            json["errorMessage"],
        )

    return response


def verify_otp(otp_id: str, data: Dict[str, Any]) -> Response:
    response = client.post(
        f"{settings.VANOMA_COMMUNICATION_API_URL}/otp/{otp_id}/verification",
        data=camelize(data),
    )

    if not response.ok:
        json = response.json()
        raise CommunicationApiException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            json["errorCode"],
            json["errorMessage"],
        )

    return response
