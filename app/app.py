from flask import Flask, jsonify, render_template, request
from datetime import datetime, timezone
from uuid import uuid4

app = Flask(__name__)

# Demo in-memory account records for the sample banking backend.
ACCOUNTS = {
    "1001": {"balance": 15400.75, "currency": "USD"},
    "1002": {"balance": 8200.00, "currency": "USD"},
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
}

TRANSACTIONS = []


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


@app.get("/")
def root() -> tuple:
    return render_template("index.html"), 200


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
                    "/api/v1/accounts/<account_id>",
                    "/api/v1/transfer",
                    "/api/v1/accounts/<account_id>/beneficiaries",
                    "/api/v1/accounts/<account_id>/transactions",
                    "/api/v1/bill-payments",
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


@app.post("/api/v1/transfer")
def transfer() -> tuple:
    payload = request.get_json(silent=True) or {}
    from_account = payload.get("fromAccount")
    to_account = payload.get("toAccount")
    amount = payload.get("amount")

    if not from_account or not to_account or amount is None:
        return jsonify({"error": "missing required fields"}), 400

    if from_account not in ACCOUNTS or to_account not in ACCOUNTS:
        return jsonify({"error": "invalid account"}), 404

    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400

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
    amount = payload.get("amount")

    if not account_id or not beneficiary_id or not biller_name or amount is None:
        return jsonify({"error": "missing required fields"}), 400

    if account_id not in ACCOUNTS:
        return jsonify({"error": "invalid account"}), 404

    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
