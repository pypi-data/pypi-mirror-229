import pytest

from rest_framework.reverse import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_403_FORBIDDEN)

pytestmark = pytest.mark.django_db


def test_admin_user_can_apply_data_access_request(admin_client, data_access_request,
                                                  attribute_schema):
    response = apply_request(admin_client, data_access_request)

    assert response.status_code == HTTP_200_OK


def test_admin_user_can_create_data_access_request(admin_client, contact):
    response = create_request(admin_client, contact)

    assert response.status_code == HTTP_201_CREATED


def test_admin_user_can_delete_data_access_request(admin_client, data_access_request):
    response = delete_request(admin_client, data_access_request)

    assert response.status_code == HTTP_204_NO_CONTENT


def test_admin_user_can_list_data_access_requests(admin_client):
    response = list_requests(admin_client)

    assert response.status_code == HTTP_200_OK


def test_normal_user_cannot_apply_data_access_request(client, data_access_request,
                                                      attribute_schema):
    response = apply_request(client, data_access_request)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_user_without_permissions_can_create_data_access_request(client, contact):
    response = create_request(client, contact)

    assert response.status_code == HTTP_201_CREATED


def test_user_without_permissions_cannot_delete_data_access_request(client, data_access_request):
    response = delete_request(client, data_access_request)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_user_without_permissions_cannot_list_data_access_requests(client):
    response = list_requests(client)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_apply_data_access_request(anonymous_client, data_access_request,
                                                         attribute_schema):
    response = apply_request(anonymous_client, data_access_request)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_create_data_access_request(anonymous_client, contact):
    response = create_request(anonymous_client, contact)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_delete_data_access_request(anonymous_client, data_access_request):
    response = delete_request(anonymous_client, data_access_request)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_list_data_access_requests(anonymous_client):
    response = list_requests(anonymous_client)

    assert response.status_code == HTTP_403_FORBIDDEN


def apply_request(client, obj):
    return client.post(reverse('dataaccessrequest-apply', kwargs=dict(pk=obj.pk)))


def create_request(client, contact):
    return client.post(reverse('dataaccessrequest-list'), data=dict(contact=contact.pk))


def delete_request(client, obj):
    return client.delete(reverse('dataaccessrequest-detail', kwargs=dict(pk=obj.pk)))


def list_requests(client):
    return client.get(reverse('dataaccessrequest-list'))
