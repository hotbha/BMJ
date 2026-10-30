"""Deterministic mock BMJ backend used only for before/after screenshot capture.

Both the legacy (HEAD) worktree and the migrated working tree are launched with
--dart-define=API_BASE_URL=http://127.0.0.1:8099 so they render the exact same
catalog / subscription / cart payloads.

Run:  python stub_server.py [--port 8099]
"""

from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

SIZES = [("200ml", 1.0), ("300ml", 1.34), ("500ml", 1.96)]


def _item(item_id, name, category, image, start, end, base_price, calories,
          ingredients, description):
    prices = []
    for size, factor in SIZES:
        prices.append(
            {
                "priceId": f"{item_id}-{size}",
                "id": f"{item_id}-{size}",
                "itemId": item_id,
                "name": size,
                "price": round(base_price * factor),
                "currencyCode": "INR",
                "pricingModel": "flat_fee",
                "period": 1,
                "periodUnit": "month",
                "status": "ACTIVE",
                "externalName": f"{name} {size}",
            }
        )
    return {
        "itemId": item_id,
        "id": item_id,
        "name": name,
        "description": description,
        "category": category,
        "itemFamilyId": category.lower(),
        "imagePath": image,
        "startColor": start,
        "endColor": end,
        
        "calories": calories,
        "status": "ACTIVE",
        "enabledForCheckout": True,
        "enabledInPortal": True,
        "servingSize": "300ml",
        "type": "CHARGE",
        "prices": prices,
    }


CATALOG = [
    _item("pineapple-delight", "Pineapple Delight", "Delight",
          "assets/pineapple.png", "#FFE082", "#FFB300", 149, 118,
          ["Pineapple", "Lime", "Mint"],
          "Cold-pressed pineapple with a squeeze of lime and fresh mint."),
    _item("watermelon-delight", "Watermelon Delight", "Delight",
          "assets/watermelon.png", "#FF8A80", "#E53935", 129, 96,
          ["Watermelon", "Basil", "Sea Salt"],
          "Sun-ripened watermelon pressed the same morning it is delivered."),
    _item("abc-signature", "ABC Signature", "Signature",
          "assets/ABC.png", "#FF7043", "#D84315", 189, 142,
          ["Apple", "Beetroot", "Carrot"],
          "The classic apple-beet-carrot trio for a clean daily reset."),
    _item("vitamin-c-signature", "Vitamin C Signature", "Signature",
          "assets/VitaminC.png", "#FFD54F", "#FF8F00", 169, 104,
          ["Orange", "Amla", "Ginger"],
          "Immunity-first blend of orange, amla and a warm ginger finish."),
    _item("carrot-premium", "Carrot Premium", "Premium",
          "assets/carrot.png", "#FFB74D", "#EF6C00", 199, 127,
          ["Carrot", "Turmeric", "Black Pepper"],
          "Golden carrots with turmeric and a pinch of black pepper."),
    _item("pbc-premium", "PBC Premium", "Premium",
          "assets/PBC.png", "#A1887F", "#5D4037", 209, 158,
          ["Pineapple", "Beetroot", "Carrot"],
          "Deep-red premium press with a sweet pineapple backbone."),
]

NOW = int(time.time())
NEXT_BILLING = NOW + 6 * 24 * 3600


SUBSCRIPTIONS = [
    {
        "id": "SUB-1042",
        "subscriptionId": "SUB-1042",
        "status": "ACTIVE",
        "planId": "Weekly Family Plan",
        "planName": "Weekly Family Plan",
        "nextBillingAt": NEXT_BILLING,
        "currentTermEnd": NEXT_BILLING,
        "currencyCode": "INR",
        "startDate": NOW - 8 * 24 * 3600,
        "quantity": 2,
        "billingPeriod": 1,
        "billingPeriodUnit": "week",
    },
    {
        "id": "SUB-2077",
        "subscriptionId": "SUB-2077",
        "status": "PAUSED",
        "planId": "Monthly Starter",
        "planName": "Monthly Starter",
        "nextBillingAt": NEXT_BILLING + 10 * 24 * 3600,
        "currentTermEnd": NEXT_BILLING + 10 * 24 * 3600,
        "currencyCode": "INR",
        "startDate": NOW - 25 * 24 * 3600,
        "quantity": 1,
        "billingPeriod": 1,
        "billingPeriodUnit": "month",
    },
]

PLANS = [
    {
        "planId": "weekly-family",
        "id": "weekly-family",
        "name": "Weekly Family Plan",
        "price": 699,
        "period": 1,
        "periodUnit": "week",
        "currencyCode": "INR",
        "description": "4 bottles a day, delivered every morning.",
    },
    {
        "planId": "monthly-starter",
        "id": "monthly-starter",
        "name": "Monthly Starter",
        "price": 2299,
        "period": 1,
        "periodUnit": "month",
        "currencyCode": "INR",
        "description": "2 bottles a day with weekend flexibility.",
    },
]

USER = {
    "id": "user_capture_001",
    "userId": "user_capture_001",
    "name": "Aarav Sharma",
    "fullName": "Aarav Sharma",
    "email": "aarav.sharma@bookmyjuice.test",
    "phone": "+919876543210",
    "phoneNumber": "+919876543210",
    "role": "USER",
    "status": "ACTIVE",
    "customerId": "capture_customer_001",
}

EMPTY_CART = {
    "cart_id": "cart_capture_001",
    "items": [],
    "subtotal": 0,
    "discount": 0,
    "total": 0,
    "currency": "INR",
}


def route(path, method):
    if path.endswith("/catalog/charge-items") or path.endswith("/test/charge-items"):
        return 200, CATALOG
    if path.endswith("/subscriptions/my"):
        return 200, {"subscriptions": SUBSCRIPTIONS}
    if path.endswith("/subscriptions/pricing/plans"):
        return 200, {"plans": PLANS, "data": PLANS}
    if path.endswith("/v1/cart"):
        return 200, EMPTY_CART
    if "/v1/cart/" in path:
        return 200, EMPTY_CART
    if path.endswith("/auth/account") or path.endswith("/test/user"):
        return 200, USER
    if path.endswith("/bottles/ledger"):
        return 200, {"balance": 4, "returned": 2, "outstanding": 2, "entries": []}
    if path.endswith("/bottles/transactions"):
        return 200, {"transactions": []}
    if "/api/invoices" in path:
        return 200, []
    if "/api/orders" in path:
        return 200, []
    if path.endswith("/api/products"):
        return 200, []
    if path.endswith("/health"):
        return 200, {"status": "UP", "message": "stub", "timestamp": NOW}
    return 200, {}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _respond(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods",
                         "GET,POST,PUT,PATCH,DELETE,OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):  # noqa: N802
        self._respond(200, {})

    def _handle(self, method):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        if length and method in ("POST", "PUT", "PATCH"):
            self.rfile.read(length)
        status, payload = route(path, method)
        self._respond(status, payload)
        print(f"[stub] {method} {path} -> {status}")

    def do_GET(self):  # noqa: N802
        self._handle("GET")

    def do_POST(self):  # noqa: N802
        self._handle("POST")

    def do_PUT(self):  # noqa: N802
        self._handle("PUT")

    def do_PATCH(self):  # noqa: N802
        self._handle("PATCH")

    def do_DELETE(self):  # noqa: N802
        self._handle("DELETE")

    def log_message(self, fmt, *args):
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8099)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"[stub] listening on http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
