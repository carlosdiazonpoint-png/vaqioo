import uuid
from datetime import datetime
from flask_login import UserMixin
from extensions import db


def gen_uuid():
    return str(uuid.uuid4())


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    pin_hash = db.Column(db.String(255), nullable=False)  # PIN de 4 dígitos para transferencias
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wallet = db.relationship("Wallet", backref="owner", uselist=False, cascade="all, delete-orphan")

    def get_id(self):
        return self.id


class Wallet(db.Model):
    __tablename__ = "wallets"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    balance = db.Column(db.Numeric(14, 2), default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    type = db.Column(db.String(20), nullable=False)  # deposit | transfer_out | transfer_in
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    description = db.Column(db.String(255))

    sender_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    receiver_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])

    def to_dict(self, current_user_id):
        is_outgoing = self.sender_id == current_user_id
        counterpart = self.receiver if is_outgoing else self.sender
        return {
            "id": self.id,
            "type": self.type,
            "amount": float(self.amount),
            "description": self.description,
            "date": self.created_at.strftime("%d/%m/%Y %H:%M"),
            "direction": "out" if is_outgoing and self.type == "transfer_out" else "in",
            "counterpart": counterpart.full_name if counterpart else "Recarga",
        }
