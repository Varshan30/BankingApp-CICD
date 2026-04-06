from flask import Flask, jsonify, render_template, request
from datetime import datetime, timezone
from uuid import uuid4

app = Flask(__name__)

# Demo in-memory account records for the sample banking backend.
ACCOUNTS = {
    "1001": {
        "balance": 15400.75,
        "currency": "INR",
        "status": "ACTIVE",
        "holderName": "Aarav Sharma",
        "accountType": "Salary Account",
        "maskedNumber": "**** 3819",
    },
    "1002": {
        "balance": 8200.00,
        "currency": "INR",
        "status": "ACTIVE",
        "holderName": "Nisha Verma",
        "accountType": "Savings Account",
        "maskedNumber": "**** 9274",
    },
    "1003": {
        "balance": 25890.30,
        "currency": "INR",
        "status": "ACTIVE",
        "holderName": "Rohan Iyer",
        "accountType": "Premium Savings",
        "maskedNumber": "**** 4412",
    },
    "1004": {
        "balance": 6400.50,
        "currency": "INR",
        "status": "ACTIVE",
        "holderName": "Meera Patil",
        "accountType": "Student Account",
        "maskedNumber": "**** 1109",
    },
    "1005": {
        "balance": 47210.00,
        "currency": "INR",
        "status": "ACTIVE",
        "holderName": "Kabir Singh",
        "accountType": "Current Account",
        "maskedNumber": "**** 6625",
    },
}

BENEFICIARIES = {
    "1001": [
        {
            "beneficiaryId": "b-1001-01",
            "name": "City Power Utility",
            "accountNumber": "UTIL-44521",
            "bankName": "Utility Payments Bank",
        }
    ],
    "1002": [],
    "1003": [],
    "1004": [],
    "1005": [],
}

TRANSACTIONS = []

CARDS = {
    "1001": [
        {
            "cardId": "c-1001-d1",
            "last4": "3819",
            "cardType": "Debit",
            "network": "RuPay",
            "status": "ACTIVE",
            "dailyLimit": 20000.0,
        }
    ],
    "1002": [
        {
            "cardId": "c-1002-d1",
            "last4": "9274",
            "cardType": "Debit",
            "network": "Visa",
            "status": "ACTIVE",
            "dailyLimit": 15000.0,
        }
    ],
    "1003": [
        {
            "cardId": "c-1003-d1",
            "last4": "4412",
            "cardType": "Debit",
            "network": "Mastercard",
            "status": "ACTIVE",
            "dailyLimit": 25000.0,
        }
    ],
    "1004": [],
    "1005": [
        {
            "cardId": "c-1005-d1",
            "last4": "6625",
            "cardType": "Debit",
            "network": "Visa",
            "status": "ACTIVE",
            "dailyLimit": 35000.0,
        }
    ],
}

GIFT_CARD_CATALOG = [
    {
        "catalogId": "gc-amz-500",
        "brand": "Amazon",
        "title": "Amazon Shopping Gift Card",
        "amount": 500.0,
    },
    {
        "catalogId": "gc-zom-1000",
        "brand": "Zomato",
        "title": "Zomato Food Gift Card",
        "amount": 1000.0,
    },
    {
        "catalogId": "gc-flp-2000",
        "brand": "Flipkart",
        "title": "Flipkart E-Gift Card",
        "amount": 2000.0,
    },
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_amount(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return -1.0


def _record_transaction(
    account_id: str,
    transaction_type: str,
    amount: float,
    status: str,
    metadata: dict,
) -> None:
    TRANSACTIONS.append(
        {
            "transactionId": str(uuid4()),
            "accountId": account_id,
            "type": transaction_type,
            "amount": amount,
            "status": status,
            "timestamp": _utc_now_iso(),
            "metadata": metadata,
        }
    )


def _find_card(card_id: str):
    for account_id, cards in CARDS.items():
        for card in cards:
            if card["cardId"] == card_id:
                return account_id, card
    return None, None


def _seed_demo_transactions() -> None:
    if TRANSACTIONS:
        return

    seed_rows = [
        {
            "accountId": "1001",
            "type": "SALARY_CREDIT",
            "amount": 4200.00,
            "status": "SUCCESS",
            "metadata": {"employer": "Novus Fintech LLC"},
        },
        {
            "accountId": "1001",
            "type": "UPI_PAYMENT",
            "amount": 72.50,
            "status": "SUCCESS",
            "metadata": {"merchant": "Metro Cafe"},
        },
        {
            "accountId": "1001",
            "type": "ATM_WITHDRAWAL",
            "amount": 120.00,
            "status": "SUCCESS",
            "metadata": {"location": "Downtown ATM"},
        },
        {
            "accountId": "1002",
            "type": "TRANSFER_CREDIT",
            "amount": 600.00,
            "status": "SUCCESS",
            "metadata": {"fromAccount": "1001"},
        },
        {
            "accountId": "1002",
            "type": "GROCERY_PAYMENT",
            "amount": 145.35,
            "status": "SUCCESS",
            "metadata": {"merchant": "GreenMart"},
        },
    ]

    for row in seed_rows:
        _record_transaction(
            account_id=row["accountId"],
            transaction_type=row["type"],
            amount=row["amount"],
            status=row["status"],
            metadata=row["metadata"],
        )


_seed_demo_transactions()


@app.get("/")
def root() -> tuple:
    return render_template("index.html", active_page="home"), 200


@app.get("/transactions")
def transactions_page() -> tuple:
    return render_template("transactions.html", active_page="transactions"), 200


@app.get("/pay-bills")
def pay_bills_page() -> tuple:
    return render_template("pay_bills.html", active_page="pay-bills"), 200


@app.get("/gift-cards")
def gift_cards_page() -> tuple:
    return render_template("gift_cards.html", active_page="gift-cards"), 200


@app.get("/cards")
def cards_page() -> tuple:
    return render_template("cards.html", active_page="cards"), 200


@app.get("/api")
def service_info() -> tuple:
    return (
        jsonify(
            {
                "service": "mobile-banking-backend",
                "status": "running",
                "endpoints": [
                    "/health",
                    "/ready",
                    "/api/v1/accounts",
                    "/api/v1/accounts/<account_id>",
                    "/api/v1/transfer",
                    "/api/v1/accounts/<account_id>/beneficiaries",
                    "/api/v1/accounts/<account_id>/transactions",
                    "/api/v1/bill-payments",
                    "/api/v1/accounts/<account_id>/cards",
                    "/api/v1/accounts/<account_id>/cards [POST]",
                    "/api/v1/cards/<card_id>/status",
                    "/api/v1/cards/<card_id>/limit",
                    "/api/v1/gift-cards/catalog",
                    "/api/v1/gift-cards/purchase",
                ],
            }
        ),
        200,
    )


@app.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok"}), 200


@app.get("/ready")
def ready() -> tuple:
    return jsonify({"status": "ready"}), 200


@app.get("/api/v1/accounts/<account_id>")
def get_account(account_id: str) -> tuple:
    account = ACCOUNTS.get(account_id)
    if not account:
        return jsonify({"error": "account not found"}), 404
    return jsonify({"accountId": account_id, **account}), 200


@app.get("/api/v1/accounts")
def list_accounts() -> tuple:
    accounts = [
        {
            "accountId": account_id,
            "holderName": account["holderName"],
            "accountType": account["accountType"],
            "status": account["status"],
        }
        for account_id, account in ACCOUNTS.items()
        if account.get("status") == "ACTIVE"
    ][:5]

    return jsonify({"accounts": accounts}), 200


@app.post("/api/v1/transfer")
def transfer() -> tuple:
    payload = request.get_json(silent=True) or {}
    from_account = payload.get("fromAccount")
    to_account = payload.get("toAccount")
    amount = _parse_amount(payload.get("amount"))

    if not from_account or not to_account or amount <= 0:
        return jsonify({"error": "missing required fields"}), 400

    if from_account not in ACCOUNTS or to_account not in ACCOUNTS:
        return jsonify({"error": "invalid account"}), 404

    if ACCOUNTS[from_account]["balance"] < amount:
        return jsonify({"error": "insufficient funds"}), 400

    ACCOUNTS[from_account]["balance"] -= amount
    ACCOUNTS[to_account]["balance"] += amount

    _record_transaction(
        account_id=from_account,
        transaction_type="TRANSFER_DEBIT",
        amount=float(amount),
        status="SUCCESS",
        metadata={"toAccount": to_account},
    )
    _record_transaction(
        account_id=to_account,
        transaction_type="TRANSFER_CREDIT",
        amount=float(amount),
        status="SUCCESS",
        metadata={"fromAccount": from_account},
    )

    return (
        jsonify(
            {
                "message": "transfer successful",
                "fromAccount": from_account,
                "toAccount": to_account,
                "amount": amount,
            }
        ),
        200,
    )


@app.get("/api/v1/accounts/<account_id>/beneficiaries")
def list_beneficiaries(account_id: str) -> tuple:
    if account_id not in ACCOUNTS:
        return jsonify({"error": "account not found"}), 404

    return (
        jsonify(
            {
                "accountId": account_id,
                "beneficiaries": BENEFICIARIES.get(account_id, []),
            }
        ),
        200,
    )


@app.post("/api/v1/accounts/<account_id>/beneficiaries")
def add_beneficiary(account_id: str) -> tuple:
    if account_id not in ACCOUNTS:
        return jsonify({"error": "account not found"}), 404

    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    account_number = payload.get("accountNumber")
    bank_name = payload.get("bankName")

    if not name or not account_number or not bank_name:
        return jsonify({"error": "missing required fields"}), 400

    new_beneficiary = {
        "beneficiaryId": f"b-{account_id}-{uuid4().hex[:6]}",
        "name": name,
        "accountNumber": account_number,
        "bankName": bank_name,
    }

    BENEFICIARIES.setdefault(account_id, []).append(new_beneficiary)

    return jsonify({"message": "beneficiary added", "beneficiary": new_beneficiary}), 201


@app.get("/api/v1/accounts/<account_id>/transactions")
def get_transactions(account_id: str) -> tuple:
    if account_id not in ACCOUNTS:
        return jsonify({"error": "account not found"}), 404

    limit = request.args.get("limit", default=10, type=int)
    limit = max(1, min(limit, 100))

    account_transactions = [
        tx for tx in reversed(TRANSACTIONS) if tx["accountId"] == account_id
    ][:limit]

    return jsonify({"accountId": account_id, "transactions": account_transactions}), 200


@app.post("/api/v1/bill-payments")
def pay_bill() -> tuple:
    payload = request.get_json(silent=True) or {}
    account_id = payload.get("accountId")
    beneficiary_id = payload.get("beneficiaryId")
    biller_name = payload.get("billerName")
    amount = _parse_amount(payload.get("amount"))

    if not account_id or not beneficiary_id or not biller_name or amount <= 0:
        return jsonify({"error": "missing required fields"}), 400

    if account_id not in ACCOUNTS:
        return jsonify({"error": "invalid account"}), 404

    beneficiary = next(
        (
            b
            for b in BENEFICIARIES.get(account_id, [])
            if b["beneficiaryId"] == beneficiary_id
        ),
        None,
    )
    if not beneficiary:
        return jsonify({"error": "beneficiary not found for account"}), 404

    if ACCOUNTS[account_id]["balance"] < amount:
        return jsonify({"error": "insufficient funds"}), 400

    ACCOUNTS[account_id]["balance"] -= amount
    _record_transaction(
        account_id=account_id,
        transaction_type="BILL_PAYMENT",
        amount=float(amount),
        status="SUCCESS",
        metadata={
            "beneficiaryId": beneficiary_id,
            "billerName": biller_name,
            "beneficiaryName": beneficiary["name"],
        },
    )

    return (
        jsonify(
            {
                "message": "bill payment successful",
                "accountId": account_id,
                "beneficiaryId": beneficiary_id,
                "billerName": biller_name,
                "amount": amount,
            }
        ),
        200,
    )


@app.get("/api/v1/accounts/<account_id>/cards")
def get_cards(account_id: str) -> tuple:
    if account_id not in ACCOUNTS:
        return jsonify({"error": "account not found"}), 404

    return jsonify({"accountId": account_id, "cards": CARDS.get(account_id, [])}), 200


@app.post("/api/v1/accounts/<account_id>/cards")
def add_card(account_id: str) -> tuple:
    if account_id not in ACCOUNTS:
        return jsonify({"error": "account not found"}), 404

    payload = request.get_json(silent=True) or {}
    last4 = str(payload.get("last4", "")).strip()
    card_type = str(payload.get("cardType", "")).strip()
    network = str(payload.get("network", "")).strip()
    daily_limit = _parse_amount(payload.get("dailyLimit"))

    if len(last4) != 4 or not last4.isdigit():
        return jsonify({"error": "last4 must contain exactly 4 digits"}), 400

    if not card_type or not network or daily_limit <= 0:
        return jsonify({"error": "missing required fields"}), 400

    existing_last4 = {card["last4"] for card in CARDS.get(account_id, [])}
    if last4 in existing_last4:
        return jsonify({"error": "card with same last4 already exists for account"}), 400

    new_card = {
        "cardId": f"c-{account_id}-{uuid4().hex[:4]}",
        "last4": last4,
        "cardType": card_type,
        "network": network,
        "status": "ACTIVE",
        "dailyLimit": daily_limit,
    }
    CARDS.setdefault(account_id, []).append(new_card)

    _record_transaction(
        account_id=account_id,
        transaction_type="CARD_ADDED",
        amount=0.0,
        status="SUCCESS",
        metadata={"cardId": new_card["cardId"], "cardType": card_type, "network": network},
    )

    return jsonify({"message": "card added", "card": new_card}), 201


@app.post("/api/v1/cards/<card_id>/status")
def update_card_status(card_id: str) -> tuple:
    payload = request.get_json(silent=True) or {}
    status = str(payload.get("status", "")).upper()

    if status not in {"ACTIVE", "BLOCKED"}:
        return jsonify({"error": "status must be ACTIVE or BLOCKED"}), 400

    account_id, card = _find_card(card_id)
    if not card:
        return jsonify({"error": "card not found"}), 404

    card["status"] = status
    _record_transaction(
        account_id=account_id,
        transaction_type="CARD_STATUS_CHANGE",
        amount=0.0,
        status="SUCCESS",
        metadata={"cardId": card_id, "newStatus": status},
    )

    return jsonify({"message": "card status updated", "card": card}), 200


@app.post("/api/v1/cards/<card_id>/limit")
def update_card_limit(card_id: str) -> tuple:
    payload = request.get_json(silent=True) or {}
    daily_limit = _parse_amount(payload.get("dailyLimit"))

    if daily_limit <= 0:
        return jsonify({"error": "dailyLimit must be positive"}), 400

    account_id, card = _find_card(card_id)
    if not card:
        return jsonify({"error": "card not found"}), 404

    card["dailyLimit"] = daily_limit
    _record_transaction(
        account_id=account_id,
        transaction_type="CARD_LIMIT_UPDATE",
        amount=0.0,
        status="SUCCESS",
        metadata={"cardId": card_id, "dailyLimit": daily_limit},
    )

    return jsonify({"message": "card limit updated", "card": card}), 200


@app.get("/api/v1/gift-cards/catalog")
def gift_card_catalog() -> tuple:
    return jsonify({"giftCards": GIFT_CARD_CATALOG}), 200


@app.post("/api/v1/gift-cards/purchase")
def purchase_gift_card() -> tuple:
    payload = request.get_json(silent=True) or {}
    account_id = payload.get("accountId")
    catalog_id = payload.get("catalogId")
    amount = _parse_amount(payload.get("amount"))

    if not account_id or not catalog_id or amount <= 0:
        return jsonify({"error": "missing required fields"}), 400

    if account_id not in ACCOUNTS:
        return jsonify({"error": "invalid account"}), 404

    catalog_item = next(
        (item for item in GIFT_CARD_CATALOG if item["catalogId"] == catalog_id),
        None,
    )
    if not catalog_item:
        return jsonify({"error": "gift card item not found"}), 404

    if float(catalog_item["amount"]) != amount:
        return jsonify({"error": "amount does not match selected gift card"}), 400

    if ACCOUNTS[account_id]["balance"] < amount:
        return jsonify({"error": "insufficient funds"}), 400

    ACCOUNTS[account_id]["balance"] -= amount
    voucher_code = f"NVB-{uuid4().hex[:10].upper()}"

    _record_transaction(
        account_id=account_id,
        transaction_type="GIFT_CARD_PURCHASE",
        amount=float(amount),
        status="SUCCESS",
        metadata={
            "catalogId": catalog_id,
            "brand": catalog_item["brand"],
            "title": catalog_item["title"],
            "voucherCode": voucher_code,
        },
    )

    return (
        jsonify(
            {
                "message": "gift card purchased",
                "accountId": account_id,
                "catalogId": catalog_id,
                "voucherCode": voucher_code,
                "amount": amount,
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
