from decimal import Decimal, InvalidOperation
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from extensions import db, bcrypt
from models import User, Transaction

wallet_bp = Blueprint("wallet", __name__)


@wallet_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


# ---------- API interna consumida por static/js/main.js ----------

@wallet_bp.route("/api/balance")
@login_required
def api_balance():
    return jsonify({"balance": float(current_user.wallet.balance)})


@wallet_bp.route("/api/history")
@login_required
def api_history():
    txs = (
        Transaction.query.filter(
            (Transaction.sender_id == current_user.id) | (Transaction.receiver_id == current_user.id)
        )
        .order_by(Transaction.created_at.desc())
        .limit(30)
        .all()
    )
    return jsonify([t.to_dict(current_user.id) for t in txs])


@wallet_bp.route("/api/deposit", methods=["POST"])
@login_required
def api_deposit():
    data = request.get_json(force=True)
    try:
        amount = Decimal(str(data.get("amount", 0)))
    except InvalidOperation:
        return jsonify({"error": "Monto inválido"}), 400

    if amount <= 0:
        return jsonify({"error": "El monto debe ser mayor a cero"}), 400

    current_user.wallet.balance += amount
    tx = Transaction(type="deposit", amount=amount, receiver_id=current_user.id, description="Recarga")
    db.session.add(tx)
    db.session.commit()

    return jsonify({"ok": True, "balance": float(current_user.wallet.balance)})


@wallet_bp.route("/api/transfer", methods=["POST"])
@login_required
def api_transfer():
    data = request.get_json(force=True)
    phone = str(data.get("phone", "")).strip()
    pin = str(data.get("pin", "")).strip()
    description = str(data.get("description", "")).strip()[:255]

    try:
        amount = Decimal(str(data.get("amount", 0)))
    except InvalidOperation:
        return jsonify({"error": "Monto inválido"}), 400

    if amount <= 0:
        return jsonify({"error": "El monto debe ser mayor a cero"}), 400

    if not bcrypt.check_password_hash(current_user.pin_hash, pin):
        return jsonify({"error": "PIN incorrecto"}), 403

    receiver = User.query.filter_by(phone=phone).first()
    if not receiver:
        return jsonify({"error": "No encontramos un usuario con ese número"}), 404
    if receiver.id == current_user.id:
        return jsonify({"error": "No puedes transferirte a ti mismo"}), 400
    if current_user.wallet.balance < amount:
        return jsonify({"error": "Saldo insuficiente"}), 400

    # Transacción atómica: descuenta y acredita
    current_user.wallet.balance -= amount
    receiver.wallet.balance += amount

    tx_out = Transaction(
        type="transfer_out", amount=amount, sender_id=current_user.id,
        receiver_id=receiver.id, description=description or "Transferencia"
    )
    db.session.add(tx_out)
    db.session.commit()

    return jsonify({"ok": True, "balance": float(current_user.wallet.balance)})
