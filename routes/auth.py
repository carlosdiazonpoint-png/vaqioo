from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db, bcrypt
from models import User, Wallet

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("wallet.dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        pin = request.form.get("pin", "")

        if not all([full_name, phone, email, password, pin]) or len(pin) != 4 or not pin.isdigit():
            flash("Revisa que todos los campos estén completos y el PIN tenga 4 dígitos.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter((User.email == email) | (User.phone == phone)).first():
            flash("Ya existe una cuenta con ese correo o número de celular.", "danger")
            return redirect(url_for("auth.register"))

        user = User(
            full_name=full_name,
            phone=phone,
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            pin_hash=bcrypt.generate_password_hash(pin).decode("utf-8"),
        )
        db.session.add(user)
        db.session.flush()  # obtener user.id antes del commit

        wallet = Wallet(user_id=user.id, balance=0)
        db.session.add(wallet)
        db.session.commit()

        login_user(user)
        flash(f"¡Bienvenido, {user.full_name.split()[0]}! Tu billetera fue creada.", "success")
        return redirect(url_for("wallet.dashboard"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("wallet.dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect(url_for("wallet.dashboard"))

        flash("Credenciales incorrectas. Intenta de nuevo.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
