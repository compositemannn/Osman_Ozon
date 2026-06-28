# import httpx

# from app.infrastructure.config import settings


# async def get_order(
#     posting_number: str, url: str = "https://api-seller.ozon.ru/v3/posting/fbs/get"
# ):
#     body = {"posting_number": posting_number, "with": {"financial_data": True}}

#     headers = {
#         "Client-Id": settings.CLIENT_ID,
#         "Api-Key": settings.API_KEY,
#         "Content-Type": "application/json",
#     }

#     async with httpx.AsyncClient(timeout=20.0) as client:
#         resp = await client.post(url, headers=headers, json=body)
#         if resp.status_code != 200:
#             print(f"Status: {resp.status_code}")
#             print(f"Response body: {resp.text}")
#             resp.raise_for_status()
#         payload = resp.json()

#     return payload


from typing import Any

from app.notifications.tests.order_data import orders


def get_order_by_posting_number(
    posting_number: str,
) -> dict[str, Any] | None:
    for order in orders:
        if order["result"]["posting_number"] == posting_number:
            return order

    return None
