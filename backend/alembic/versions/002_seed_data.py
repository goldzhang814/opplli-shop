"""seed initial data

Revision ID: 002
Revises: 001
Create Date: 2026-01-01 00:00:01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from datetime import datetime
import bcrypt
import os
import json

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def _hash_password(plain: str) -> str:
    pwd = plain.encode("utf-8")
    if len(pwd) > 72:
        import hashlib
        pwd = hashlib.sha256(pwd).hexdigest().encode("utf-8")
    return bcrypt.hashpw(pwd, bcrypt.gensalt(rounds=12)).decode("utf-8")


def upgrade() -> None:
    conn = op.get_bind()
    now  = datetime.utcnow()

    # ── Super Admin ───────────────────────────────────────────────────────────
    email    = os.environ.get("SUPER_ADMIN_EMAIL",    "admin@example.com")
    password = os.environ.get("SUPER_ADMIN_PASSWORD", "changeme123")
    all_perms = {
        "products": True, "categories": True, "inventory": True, "reviews": True,
        "orders": True, "payments": True, "coupons": True, "banners": True,
        "newsletter": True, "channels": True, "shipping": True, "tax": True,
        "carriers": True, "content": True, "seo": True, "email_templates": True,
        "statistics": True, "admins": True,
    }
    conn.execute(sa.text("""
        INSERT INTO admins (email, password_hash, full_name, role, is_active, permissions, created_at, updated_at)
        VALUES (:email, :pw, 'Super Admin', 'super_admin', 1, :perms, :now, :now)
    """), {"email": email, "pw": _hash_password(password), "perms": json.dumps(all_perms), "now": now})

    # ── Shipping Zones ────────────────────────────────────────────────────────
    zones = [
        (1, "US Mainland"),
        (2, "Europe"),
        (3, "United Kingdom"),
        (4, "Canada"),
        (5, "International"),
    ]
    conn.execute(sa.text(
        "INSERT INTO shipping_zones (id, name, created_at, updated_at) VALUES (:id, :name, :now, :now)"
    ), [{"id": z[0], "name": z[1], "now": now} for z in zones])

    # ── Zone → Country mappings ───────────────────────────────────────────────
    zone_countries = [
        (1, "US"),
        (2, "DE"), (2, "FR"), (2, "IT"), (2, "ES"), (2, "NL"),
        (2, "BE"), (2, "AT"), (2, "PT"), (2, "SE"), (2, "DK"),
        (2, "FI"), (2, "NO"), (2, "PL"), (2, "CZ"), (2, "HU"),
        (3, "GB"),
        (4, "CA"),
    ]
    conn.execute(sa.text(
        "INSERT INTO shipping_zone_regions (zone_id, country_code) VALUES (:zone_id, :country_code)"
    ), [{"zone_id": z, "country_code": c} for z, c in zone_countries])

    # ── Shipping Rules (fee + free shipping threshold) ────────────────────────
    rules = [
        (1, 5.99,  50.00),   # US Mainland
        (2, 8.99,  70.00),   # Europe
        (3, 7.99,  60.00),   # UK
        (4, 9.99,  70.00),   # Canada
        (5, 14.99, 100.00),  # International
    ]
    conn.execute(sa.text("""
        INSERT INTO shipping_rules (zone_id, shipping_fee, free_shipping_threshold, is_active, created_at, updated_at)
        VALUES (:zone_id, :fee, :threshold, 1, :now, :now)
    """), [{"zone_id": r[0], "fee": r[1], "threshold": r[2], "now": now} for r in rules])

    # ── Shipping Regions: US states ───────────────────────────────────────────
    us_states_enabled = [
        "AL","AR","AZ","CA","CO","CT","DE","FL","GA","IA","ID","IL","IN","KS",
        "KY","LA","MA","MD","ME","MI","MN","MO","MS","MT","NC","ND","NE","NH",
        "NJ","NM","NV","NY","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT",
        "VA","VT","WA","WI","WV","WY","DC",
    ]
    us_states_disabled = ["AK", "HI"]  # no shipping to Alaska / Hawaii

    rows = []
    for sc in us_states_enabled:
        rows.append({"country_code": "US", "state_code": sc, "enabled": 1, "now": now})
    for sc in us_states_disabled:
        rows.append({"country_code": "US", "state_code": sc, "enabled": 0, "now": now})
    # Non-US countries — whole country enabled (state_code NULL)
    for cc in ["DE","FR","IT","ES","NL","BE","AT","PT","SE","DK","FI","NO","PL","CZ","HU","GB","CA"]:
        rows.append({"country_code": cc, "state_code": None, "enabled": 1, "now": now})
    conn.execute(sa.text("""
        INSERT INTO shipping_regions (country_code, state_code, enabled, created_at, updated_at)
        VALUES (:country_code, :state_code, :enabled, :now, :now)
    """), rows)

    # ── Logistics Carriers ────────────────────────────────────────────────────
    carriers = [
        ("UPS",   "ups",   "https://www.ups.com/track?tracknum={tracking_no}"),
        ("FedEx", "fedex", "https://www.fedex.com/fedextrack/?tracknumbers={tracking_no}"),
        ("USPS",  "usps",  "https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_no}"),
        ("DHL",   "dhl",   "https://www.dhl.com/en/express/tracking.html?AWB={tracking_no}"),
        ("Royal Mail", "royal_mail", "https://www.royalmail.com/track-your-item#/tracking-results/{tracking_no}"),
    ]
    conn.execute(sa.text("""
        INSERT INTO logistics_carriers (name, code, tracking_url_template, is_active, created_at, updated_at)
        VALUES (:name, :code, :url, 1, :now, :now)
    """), [{"name": c[0], "code": c[1], "url": c[2], "now": now} for c in carriers])

    # ── Site Settings ──────────────────────────────────────────────────────────
    settings_data = [
        ("site_name",                     "My Store",          "Store display name"),
        ("site_url",                       "https://example.com", "Canonical site URL"),
        ("meta_title",                     "My Store — Official Site", "Default meta title"),
        ("meta_description",               "Shop our products.", "Default meta description"),
        ("og_image",                       "",                  "Default Open Graph image URL"),
        ("google_analytics_id",            "",                  "Google Analytics measurement ID"),
        ("robots_txt",                     "User-agent: *\nAllow: /\nSitemap: https://example.com/sitemap.xml", "robots.txt content"),
        ("contact_whatsapp",               "",                  "WhatsApp contact URL or number"),
        ("contact_facebook",               "",                  "Facebook page URL"),
        ("contact_telegram",               "",                  "Telegram username or URL"),
        ("contact_email",                  "support@example.com", "Support email address"),
        ("review_auto_approve_threshold",  "3",                 "Reviews >= this rating auto-approve (0 = all manual)"),
        ("currency",                       "USD",               "Store currency (fixed)"),
        ("languages",                      "en,es",             "Supported language codes"),
        ("default_language",               "en",                "Default language code"),
    ]
    conn.execute(sa.text("""
        INSERT INTO site_settings (setting_key, setting_value, description, created_at, updated_at)
        VALUES (:key, :value, :desc, :now, :now)
    """), [{"key": s[0], "value": s[1], "desc": s[2], "now": now} for s in settings_data])

    # ── Countries ──────────────────────────────────────────────────────────────
    countries = [
        ("US", "United States", 1),
        ("GB", "United Kingdom", 2),
        ("CA", "Canada", 3),
        ("DE", "Germany", 4),
        ("FR", "France", 5),
        ("IT", "Italy", 6),
        ("ES", "Spain", 7),
        ("NL", "Netherlands", 8),
        ("AU", "Australia", 9),
        ("JP", "Japan", 10),
    ]
    conn.execute(sa.text("""
        INSERT INTO countries (code, name, is_active, sort_order)
        VALUES (:code, :name, 1, :sort_order)
    """), [{"code": c[0], "name": c[1], "sort_order": c[2]} for c in countries])

    # ── US States ──────────────────────────────────────────────────────────────
    us_states = [
        ("AL","Alabama"),("AK","Alaska"),("AZ","Arizona"),("AR","Arkansas"),
        ("CA","California"),("CO","Colorado"),("CT","Connecticut"),("DE","Delaware"),
        ("FL","Florida"),("GA","Georgia"),("HI","Hawaii"),("ID","Idaho"),
        ("IL","Illinois"),("IN","Indiana"),("IA","Iowa"),("KS","Kansas"),
        ("KY","Kentucky"),("LA","Louisiana"),("ME","Maine"),("MD","Maryland"),
        ("MA","Massachusetts"),("MI","Michigan"),("MN","Minnesota"),("MS","Mississippi"),
        ("MO","Missouri"),("MT","Montana"),("NE","Nebraska"),("NV","Nevada"),
        ("NH","New Hampshire"),("NJ","New Jersey"),("NM","New Mexico"),("NY","New York"),
        ("NC","North Carolina"),("ND","North Dakota"),("OH","Ohio"),("OK","Oklahoma"),
        ("OR","Oregon"),("PA","Pennsylvania"),("RI","Rhode Island"),("SC","South Carolina"),
        ("SD","South Dakota"),("TN","Tennessee"),("TX","Texas"),("UT","Utah"),
        ("VT","Vermont"),("VA","Virginia"),("WA","Washington"),("WV","West Virginia"),
        ("WI","Wisconsin"),("WY","Wyoming"),("DC","Washington D.C."),
    ]
    conn.execute(sa.text("""
        INSERT INTO country_states (country_code, code, name, is_active)
        VALUES (:cc, :code, :name, :active)
    """), [{"cc": "US", "code": s[0], "name": s[1],
             "active": 0 if s[0] in ("AK","HI") else 1} for s in us_states])

    # ── Default Email Templates (EN + ES) ─────────────────────────────────────
    templates = [
        ("order_confirmation", "en", "Order Confirmed — #{{order_id}}",
         "<h2>Thank you, {{customer_name}}!</h2><p>Your order <strong>#{{order_id}}</strong> has been confirmed.</p>"),
        ("order_confirmation", "es", "Pedido Confirmado — #{{order_id}}",
         "<h2>¡Gracias, {{customer_name}}!</h2><p>Tu pedido <strong>#{{order_id}}</strong> ha sido confirmado.</p>"),
        ("order_shipped", "en", "Your order has shipped! 🚚",
         "<h2>Great news, {{customer_name}}!</h2><p>Order #{{order_id}} is on its way via {{carrier_name}}.</p><p>Tracking: <a href='{{tracking_url}}'>{{tracking_no}}</a></p>"),
        ("order_shipped", "es", "¡Tu pedido está en camino! 🚚",
         "<h2>¡Buenas noticias, {{customer_name}}!</h2><p>El pedido #{{order_id}} está en camino con {{carrier_name}}.</p><p>Rastreo: <a href='{{tracking_url}}'>{{tracking_no}}</a></p>"),
        ("order_cancelled", "en", "Your order #{{order_id}} has been cancelled",
         "<p>Hi {{customer_name}}, your order #{{order_id}} has been cancelled.</p>"),
        ("order_cancelled", "es", "Tu pedido #{{order_id}} ha sido cancelado",
         "<p>Hola {{customer_name}}, tu pedido #{{order_id}} ha sido cancelado.</p>"),
        ("order_refunded", "en", "Refund processed for order #{{order_id}}",
         "<p>Hi {{customer_name}}, a refund of ${{refund_amount}} has been processed for order #{{order_id}}.</p>"),
        ("order_refunded", "es", "Reembolso procesado para el pedido #{{order_id}}",
         "<p>Hola {{customer_name}}, se procesó un reembolso de ${{refund_amount}} para el pedido #{{order_id}}.</p>"),
        ("payment_failed", "en", "Action required: Complete your order #{{order_id}}",
         "<p>Hi {{customer_name}}, your payment for order #{{order_id}} failed. Reason: {{fail_reason}}.</p><p><a href='{{retry_url}}'>Click here to retry payment</a></p>"),
        ("payment_failed", "es", "Acción requerida: Completa tu pedido #{{order_id}}",
         "<p>Hola {{customer_name}}, el pago del pedido #{{order_id}} falló. Motivo: {{fail_reason}}.</p><p><a href='{{retry_url}}'>Haz clic aquí para reintentar el pago</a></p>"),
        ("password_reset", "en", "Reset your password",
         "<p>Hi {{customer_name}}, click the link below to reset your password:</p><p><a href='{{reset_url}}'>Reset Password</a></p><p>This link expires in 1 hour.</p>"),
        ("password_reset", "es", "Restablece tu contraseña",
         "<p>Hola {{customer_name}}, haz clic en el enlace para restablecer tu contraseña:</p><p><a href='{{reset_url}}'>Restablecer Contraseña</a></p><p>Este enlace expira en 1 hora.</p>"),
    ]
    conn.execute(sa.text("""
        INSERT INTO email_templates (type, language_code, subject, body, is_active, created_at, updated_at)
        VALUES (:type, :lang, :subject, :body, 1, :now, :now)
    """), [{"type": t[0], "lang": t[1], "subject": t[2], "body": t[3], "now": now} for t in templates])

    # ── Cookie Consent Config ──────────────────────────────────────────────────
    cookie_configs = [
        ("en", "We use cookies", "We use cookies to improve your experience. By using our site, you agree to our cookie policy.",
         "Accept All", "Reject All", "Customize"),
        ("es", "Usamos cookies", "Usamos cookies para mejorar tu experiencia. Al usar nuestro sitio, aceptas nuestra política de cookies.",
         "Aceptar Todo", "Rechazar Todo", "Personalizar"),
    ]
    conn.execute(sa.text("""
        INSERT INTO cookie_consent_configs (language_code, title, description, accept_btn, reject_btn, customize_btn, is_active, created_at, updated_at)
        VALUES (:lang, :title, :desc, :accept, :reject, :customize, 1, :now, :now)
    """), [{"lang": c[0], "title": c[1], "desc": c[2], "accept": c[3], "reject": c[4], "customize": c[5], "now": now}
           for c in cookie_configs])

    # ── CMS Pages (placeholder) ───────────────────────────────────────────────
    cms_pages = [
        ("about_us",       "en", "About Us",        "<h1>About Us</h1><p>Edit this page in the admin panel.</p>"),
        ("about_us",       "es", "Sobre Nosotros",   "<h1>Sobre Nosotros</h1><p>Edita esta página en el panel admin.</p>"),
        ("return_policy",  "en", "Return Policy",    "<h1>Return Policy</h1><p>Edit this page in the admin panel.</p>"),
        ("return_policy",  "es", "Política de Devoluciones", "<h1>Política de Devoluciones</h1><p>Edita esta página.</p>"),
        ("shipping_policy","en", "Shipping Policy",  "<h1>Shipping Policy</h1><p>Edit this page in the admin panel.</p>"),
        ("shipping_policy","es", "Política de Envíos","<h1>Política de Envíos</h1><p>Edita esta página.</p>"),
        ("privacy_policy", "en", "Privacy Policy",   "<h1>Privacy Policy</h1><p>Edit this page in the admin panel.</p>"),
        ("privacy_policy", "es", "Política de Privacidad","<h1>Política de Privacidad</h1><p>Edita esta página.</p>"),
        ("terms_of_service","en","Terms of Service", "<h1>Terms of Service</h1><p>Edit this page in the admin panel.</p>"),
        ("terms_of_service","es","Términos de Servicio","<h1>Términos de Servicio</h1><p>Edita esta página.</p>"),
        ("terms_of_use",   "en", "Terms of Use",     "<h1>Terms of Use</h1><p>Edit this page in the admin panel.</p>"),
        ("terms_of_use",   "es", "Términos de Uso",  "<h1>Términos de Uso</h1><p>Edita esta página.</p>"),
        ("cookie_policy",  "en", "Cookie Policy",    "<h1>Cookie Policy</h1><p>Edit this page in the admin panel.</p>"),
        ("cookie_policy",  "es", "Política de Cookies","<h1>Política de Cookies</h1><p>Edita esta página.</p>"),
    ]
    conn.execute(sa.text("""
        INSERT INTO cms_pages (page_type, language_code, title, content, is_published, created_at, updated_at)
        VALUES (:type, :lang, :title, :content, 1, :now, :now)
    """), [{"type": p[0], "lang": p[1], "title": p[2], "content": p[3], "now": now} for p in cms_pages])

    # ── Default Language Packs (EN key stubs) ─────────────────────────────────
    lang_en = [
        ("nav.products", "Products"), ("nav.blog", "Blog"), ("nav.faq", "FAQ"),
        ("nav.about", "About Us"), ("nav.contact", "Contact"),
        ("cart.title", "Shopping Cart"), ("cart.empty", "Your cart is empty"),
        ("cart.add", "Add to Cart"), ("cart.checkout", "Checkout"),
        ("checkout.place_order", "Place Order"), ("checkout.shipping", "Shipping"),
        ("checkout.payment", "Payment"), ("checkout.summary", "Order Summary"),
        ("checkout.free_shipping", "Free shipping on orders over ${{threshold}}"),
        ("checkout.spend_more", "Spend ${{amount}} more for free shipping"),
        ("auth.sign_in", "Sign In"), ("auth.sign_up", "Create Account"),
        ("auth.sign_out", "Sign Out"), ("auth.email", "Email Address"),
        ("auth.password", "Password"), ("auth.forgot_password", "Forgot password?"),
        ("auth.agree_terms", "I agree to the Terms of Service and Privacy Policy"),
        ("product.reviews", "Reviews"), ("product.add_to_wishlist", "Save"),
        ("product.in_stock", "In Stock"), ("product.out_of_stock", "Out of Stock"),
        ("order.status.pending_payment", "Pending Payment"),
        ("order.status.pending_shipment", "Processing"),
        ("order.status.shipped", "Shipped"),
        ("order.status.completed", "Completed"),
        ("order.status.cancelled", "Cancelled"),
        ("order.status.refunded", "Refunded"),
        ("footer.newsletter_title", "Stay in the loop"),
        ("footer.newsletter_placeholder", "Your email address"),
        ("footer.newsletter_btn", "Subscribe"),
    ]
    lang_es = [
        ("nav.products", "Productos"), ("nav.blog", "Blog"), ("nav.faq", "Preguntas Frecuentes"),
        ("nav.about", "Sobre Nosotros"), ("nav.contact", "Contacto"),
        ("cart.title", "Carrito de Compras"), ("cart.empty", "Tu carrito está vacío"),
        ("cart.add", "Agregar al Carrito"), ("cart.checkout", "Pagar"),
        ("checkout.place_order", "Realizar Pedido"), ("checkout.shipping", "Envío"),
        ("checkout.payment", "Pago"), ("checkout.summary", "Resumen del Pedido"),
        ("checkout.free_shipping", "Envío gratis en pedidos mayores a ${{threshold}}"),
        ("checkout.spend_more", "Gasta ${{amount}} más para envío gratis"),
        ("auth.sign_in", "Iniciar Sesión"), ("auth.sign_up", "Crear Cuenta"),
        ("auth.sign_out", "Cerrar Sesión"), ("auth.email", "Correo Electrónico"),
        ("auth.password", "Contraseña"), ("auth.forgot_password", "¿Olvidaste tu contraseña?"),
        ("auth.agree_terms", "Acepto los Términos de Servicio y la Política de Privacidad"),
        ("product.reviews", "Reseñas"), ("product.add_to_wishlist", "Guardar"),
        ("product.in_stock", "En Stock"), ("product.out_of_stock", "Sin Stock"),
        ("order.status.pending_payment", "Pago Pendiente"),
        ("order.status.pending_shipment", "Procesando"),
        ("order.status.shipped", "Enviado"),
        ("order.status.completed", "Completado"),
        ("order.status.cancelled", "Cancelado"),
        ("order.status.refunded", "Reembolsado"),
        ("footer.newsletter_title", "Mantente informado"),
        ("footer.newsletter_placeholder", "Tu correo electrónico"),
        ("footer.newsletter_btn", "Suscribirse"),
    ]
    rows = []
    for key, val in lang_en:
        rows.append({"lang": "en", "key": key, "value": val, "now": now})
    for key, val in lang_es:
        rows.append({"lang": "es", "key": key, "value": val, "now": now})
    conn.execute(sa.text("""
        INSERT INTO language_packs (language_code, pack_key, pack_value, created_at, updated_at)
        VALUES (:lang, :key, :value, :now, :now)
    """), rows)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM language_packs"))
    conn.execute(sa.text("DELETE FROM cms_pages"))
    conn.execute(sa.text("DELETE FROM cookie_consent_configs"))
    conn.execute(sa.text("DELETE FROM email_templates"))
    conn.execute(sa.text("DELETE FROM site_settings"))
    conn.execute(sa.text("DELETE FROM country_states WHERE country_code = 'US'"))
    conn.execute(sa.text("DELETE FROM countries"))
    conn.execute(sa.text("DELETE FROM logistics_carriers"))
    conn.execute(sa.text("DELETE FROM shipping_regions"))
    conn.execute(sa.text("DELETE FROM shipping_rules"))
    conn.execute(sa.text("DELETE FROM shipping_zone_regions"))
    conn.execute(sa.text("DELETE FROM shipping_zones"))
    conn.execute(sa.text("DELETE FROM admins"))
