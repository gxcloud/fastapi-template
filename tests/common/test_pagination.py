from app.common.pagination import PaginatedResponse


async def test_paginated_response_computed() -> None:
    resp = PaginatedResponse[int](items=[1, 2, 3], total=50, skip=0, limit=10)
    assert resp.page == 1
    assert resp.pages == 5
    assert resp.has_next is True
    assert resp.has_prev is False


async def test_paginated_response_middle_page() -> None:
    resp = PaginatedResponse[int](items=[], total=50, skip=20, limit=10)
    assert resp.page == 3
    assert resp.has_next is True
    assert resp.has_prev is True


async def test_paginated_response_last_page() -> None:
    resp = PaginatedResponse[int](items=[], total=50, skip=40, limit=10)
    assert resp.page == 5
    assert resp.has_next is False
    assert resp.has_prev is True


async def test_paginated_response_empty() -> None:
    resp = PaginatedResponse[int](items=[], total=0, skip=0, limit=10)
    assert resp.page == 1
    assert resp.pages == 1
    assert resp.has_next is False
    assert resp.has_prev is False


async def test_paginated_response_exact() -> None:
    resp = PaginatedResponse[int](items=[1, 2], total=2, skip=0, limit=10)
    assert resp.pages == 1
    assert resp.has_next is False
