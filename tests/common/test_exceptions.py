from app.common.exceptions import ErrorResponse


async def test_error_response_minimal() -> None:
    resp = ErrorResponse.create(detail="Not found", status_code=404)
    import json
    body = json.loads(resp.body)
    assert body == {"detail": "Not found", "status_code": 404}
    assert resp.status_code == 404


async def test_error_response_with_errors() -> None:
    resp = ErrorResponse.create(
        detail="Validation failed",
        status_code=422,
        errors=[{"field": "email", "message": "Invalid email"}],
    )
    import json
    body = json.loads(resp.body)
    assert body["detail"] == "Validation failed"
    assert body["errors"] == [{"field": "email", "message": "Invalid email"}]
