#!/usr/bin/env python3
# app.py

import json
import logging
import os
import sys
import time
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from flask import (
    Flask, Blueprint, render_template, request,
    redirect, url_for, send_file, send_from_directory,
    Response, flash, g, current_app
)
from flask_mail import Mail, Message
from flask_recaptcha import ReCaptcha
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app() -> Flask:
    # ─── 1. ENV & LOGGER ─────────────────────────────────────────────
    load_dotenv()
    DEV = os.getenv("FLASK_ENV", "development") == "development"
    logging.basicConfig(
        level=logging.DEBUG if DEV else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    log = logging.getLogger("rubu")
    log.debug("ENV=development? %s", DEV)

    # ─── 2. FLASK & CONFIG ───────────────────────────────────────────
    root = Path(__file__).parent.resolve()
    app = Flask(__name__, root_path=str(root))
    cfg_name = os.getenv("FLASK_ENV", "development").capitalize()
    app.config.from_object(f"settings.{cfg_name}Config")

    # Proxy-Fix (z.B. hinter einem Reverse-Proxy)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # type: ignore

    # ─── 3. SECURITY (Talisman) ───────────────────────────────────────
    CSP = {
        "default-src": {"'self'"},
        "script-src": {
            "'self'", "'unsafe-inline'", "'unsafe-eval'",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://www.googletagmanager.com",
            "https://www.google-analytics.com",
            "https://region1.google-analytics.com",
            "https://maps.googleapis.com",
            "https://maps.gstatic.com",
            "https://www.google.com",
            "https://www.gstatic.com",
            "https://www.google.com/recaptcha/",
            "https://www.gstatic.com/recaptcha/",
        },
        "style-src": {
            "'self'", "'unsafe-inline'",
            "https://cdn.jsdelivr.net",
            "https://fonts.googleapis.com",
        },
        "font-src": {
            "'self'", "data:",
            "https://fonts.gstatic.com",
            "https://cdn.jsdelivr.net",
        },
        "img-src": {
            "'self'", "data:", "blob:",
            "https://maps.googleapis.com",
            "https://www.google-analytics.com",
            "https://cdn.jsdelivr.net",
            "https://maps.gstatic.com",
        },
        "connect-src": {
            "'self'", "blob:",
            "https://www.google-analytics.com",
            "https://region1.google-analytics.com",
            "https://www.googletagmanager.com",
        },
        "frame-src": {
            "'self'",
            "https://www.google.com",
            "https://www.gstatic.com",
            "https://maps.googleapis.com",
            "https://www.google.com/recaptcha/",
            "https://www.gstatic.com/recaptcha/",
        },
        "object-src": {"'none'"},
        "base-uri": {"'self'"},
        "frame-ancestors": {"'none'"},
    }
    Talisman(app, content_security_policy=CSP, content_security_policy_nonce_in=[])

    # ─── 4. EXTENSIONS ────────────────────────────────────────────────
    mail = Mail(app)
    recaptcha = ReCaptcha(app) if app.config.get("RECAPTCHA_ENABLED") else None

    # ─── 5. DOCS BLUEPRINT ───────────────────────────────────────────
    # Pfad zur generierten Sphinx‐Dokumentation
    docs_root = root / "static" / "docs_html" / "html"

    docs_bp = Blueprint(
        "docs",
        __name__,
        static_folder=str(docs_root / "_static"),
        static_url_path="/documentation/_static",
        template_folder=str(docs_root),
        url_prefix="/documentation",
    )

    @docs_bp.after_request
    def cache_docs(resp: Response) -> Response:
        if request.path.startswith(docs_bp.static_url_path):
            resp.headers["Cache-Control"] = "public, max-age=3600"
        return resp

    @docs_bp.route("/", defaults={"path": "index.html"})
    @docs_bp.route("/<path:path>")
    def serve_docs(path: str) -> Response:
        full = docs_root / path

        # 5a) PDF-Download
        if path.startswith("downloads/"):
            pdf = docs_root / path
            if pdf.exists():
                return send_file(pdf, as_attachment=True)
            return Response("404 Not Found", status=HTTPStatus.NOT_FOUND)

        # 5b) Static assets (CSS, JS, images)
        if path.startswith("_static/"):
            return send_from_directory(str(docs_root), path)

        # 5c) HTML‐Seiten
        if full.exists() and full.suffix == ".html":
            html = full.read_text(encoding="utf-8")
            # Injektion eines “← Zurück zur Website”-Banners:
            banner = (
                "<div style='padding:.5rem;background:#f8f9fa;"
                "border-bottom:1px solid #ddd;text-align:center;'>"
                "<a href='/' style='font-weight:bold;color:#333;"
                "text-decoration:none'>← Zurück zur Website</a>"
                "</div>"
            )
            html = html.replace("<body>", f"<body>{banner}")
            return Response(html, mimetype="text/html")

        # 5d) Fallback auf index.html
        idx = docs_root / "index.html"
        if idx.exists():
            return send_from_directory(str(docs_root), "index.html")
        return Response("404 Not Found", status=HTTPStatus.NOT_FOUND)

    app.register_blueprint(docs_bp)

    # Template-Context (Cache-Buster, GA-ID, reCAPTCHA-Key)
    @app.context_processor
    def _ctx() -> Dict[str, Any]:  # noqa: D401
        return {
            "cache_version": int(time.time()),
            "ga_id": app.config.get("GA_MEASUREMENT_ID"),
            "recaptcha_site_key": app.config.get("RECAPTCHA_SITE_KEY"),
        }

    # ─── 6. KANONISCHE URL “/documentation/” ─────────────────────────
    # 6a) Nur EIN Alias ohne Slash → permanenter 301-Redirect
    @app.route("/documentation", endpoint="documentation")  # <-- strict_slashes weg!
    def documentation_alias():
        # dauerhafter Redirect reicht völlig
        return redirect("/documentation/", code=301)

    # ─── 7. SPRACHWECHSEL ─────────────────────────────────────────────
    @app.before_request
    def _inject_lang():
        g.selected_language = request.cookies.get("language", "de")

    @app.route("/set_language/<lang>")
    def set_language(lang: str):
        resp = redirect(request.referrer or url_for("index"))
        resp.set_cookie("language", lang, max_age=60 * 60 * 24 * 365)
        return resp

    # ─── 8. STARTSEITE & KONTAKTFORMULAR ────────────────────────────
    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            if not app.config.get("RECAPTCHA_ENABLED") or (recaptcha and recaptcha.verify()):
                f = request.form
                mail.send(
                    Message(
                        subject=f.get("subject", "Kontaktformular"),
                        sender=app.config["MAIL_USERNAME"],
                        recipients=[f["email"]],
                        body=f"{f['name']} {f['nachname']} <{f['email']}>\n\n{f['message']}",
                    )
                )
                flash("Ihre Nachricht wurde versendet!", "success")
                return redirect(request.url)
            flash("reCAPTCHA fehlgeschlagen.", "warning")
            return redirect(request.url)

        # GET
        lang = g.selected_language
        trans_file = root / "static" / "assets" / "json" / f"{lang}.json"
        translations = json.loads(trans_file.read_text(encoding="utf-8"))
        return render_template("index.html", translations=translations)

    # ─── 9. IMPRESSUM & DATENSCHUTZ ─────────────────────────────────
    @app.route("/impressum")
    def impressum():
        return render_template("impressum.html")

    @app.route("/datenschutz")
    def datenschutz():
        return render_template("datenschutz.html")

    @app.errorhandler(404)
    def page_not_found(e):
        return "404 – Not Found", 404

    @app.errorhandler(500)
    def internal_error(e):
        return "500 – Internal Server Error", 500

    # Favicon routen, wenn keins per static kommt
    @app.route("/favicon.ico")
    def favicon():
        static_dir = Path(current_app.root_path) / "static"
        fav = static_dir / "favicon.ico"

        if fav.exists():
            # schneller direkter Weg
            return send_from_directory(static_dir, "favicon.ico",
                                       mimetype="image/vnd.microsoft.icon")
        # kein Favicon hinterlegt → leerer 204-Response genügt
        return ("", 204)  # 204 = No Content

    # ─── 10. ERROR‐HANDLER ──────────────────────────────────────────
    # Die Templates "errors/404.html" und "errors/500.html" existieren nicht.
    # Stattdessen nutzen wir die oben definierten Handler-Funktionen.
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_error)

    return app


if __name__ == "__main__":
    app = create_app()
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    logging.getLogger("rubu").info("Running on http://%s:%s (debug=%s)", host, port, debug)
    app.run(host=host, port=port, debug=debug)
