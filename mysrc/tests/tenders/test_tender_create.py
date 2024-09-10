import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from mysrc.api.tenders.models import TenderServiceType, TenderStatus, MTender
from mysrc.api.organisations.models import MOrganization
from mysrc.api.employees.models import MEmployee
from mysrc.tests.helpers import create_test_organization, create_test_employee


async def test_create_tender_good(client: TestClient, async_session: AsyncSession):
    new_organization = await create_test_organization(async_session)
    new_employee = await create_test_employee(async_session)

    data = {
        "name": "New Tender",
        "description": "This is a test tender",
        "serviceType": TenderServiceType.construction,
        "status": TenderStatus.created,
        "organizationId": new_organization.id,
        "creatorUsername": new_employee.username
    }

    response = client.post("/api/tender/new", json=data)

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["name"] == data["name"]
    assert response_data["description"] == data["description"]
    assert response_data["status"] == data["status"]
    assert response_data["serviceType"] == data["serviceType"]
    assert response_data["version"] == 1


async def test_create_tender_bad_creator(client: TestClient, async_session: AsyncSession):
    new_organization = await create_test_organization(async_session)
    new_employee = await create_test_employee(async_session)

    data = {
        "name": "New Tender",
        "description": "This is a test tender",
        "serviceType": TenderServiceType.construction,
        "status": TenderStatus.created,
        "organizationId": new_organization.id,
        "creatorUsername": 'not_existing_username'
    }

    response = client.post("/api/tender/new", json=data)
    assert response.status_code == 404


async def test_create_tender_bad_organisation(client: TestClient, async_session: AsyncSession):
    new_organization = await create_test_organization(async_session)
    new_employee = await create_test_employee(async_session)

    data = {
        "name": "New Tender",
        "description": "This is a test tender",
        "serviceType": TenderServiceType.construction,
        "status": TenderStatus.created,
        "organizationId": 999,
        "creatorUsername": new_employee.username
    }

    response = client.post("/api/tender/new", json=data)
    assert response.status_code == 404


async def test_create_tender_not_enough_data(client: TestClient, async_session: AsyncSession):
    new_organization = await create_test_organization(async_session)
    new_employee = await create_test_employee(async_session)

    data = {
        "name": "New Tender",
        "serviceType": TenderServiceType.construction,
        "status": TenderStatus.created,
        "organizationId": new_organization.id,
        "creatorUsername": new_employee.username
    }

    response = client.post("/api/tender/new", json=data)
    assert response.status_code == 422
