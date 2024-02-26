from app import exchange, crud, models
from sqlalchemy.orm import Session
from fastapi import HTTPException
import pytest
from pytest_mock import mocker

def test_update_exchange_rates_mocked(mocker, db_session: Session):
    # Mocking the external API call
    mocker.patch('httpx.get', return_value=mocker.Mock(status_code=200, json=lambda: {"rates": {"USD": 1.0, "EUR": 0.85}}))

    # Call the function with the mocked external API
    exchange.update_exchange_rates(db_session)

    # Check that the currencies were updated in the database
    assert crud.get_currency(db_session, "USD").rate == 1.0
    assert crud.get_currency(db_session, "EUR").rate == 0.85

def test_convert_currency(db_session: Session):
    # Add some currencies to the database
    crud.create_currency(db_session, models.Currency(id="USD", code="USD", rate=1.0))
    crud.create_currency(db_session, models.Currency(id="EUR", code="EUR", rate=0.85))

    # Test the conversion function
    result = exchange.convert_currency(db_session, "USD", "EUR", 100)
    assert result == 85.0

def test_convert_currency_currency_not_found(db_session: Session):
    # Test case where one of the currencies is not in the database
    with pytest.raises(HTTPException) as excinfo:
        exchange.convert_currency(db_session, "USD", "GBP", 100)

    assert excinfo.value.status_code == 404
    assert "Currency not found" in excinfo.value.detail
