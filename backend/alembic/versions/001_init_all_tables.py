"""init all tables

Revision ID: 001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── admins ───────────────────────────────────────────────────────────────
    op.create_table(
        "admins",
        sa.Column("id",            sa.Integer(),     primary_key=True, autoincrement=True),
        sa.Column("email",         sa.String(191),   nullable=False),
        sa.Column("password_hash", sa.String(255),   nullable=False),
        sa.Column("full_name",     sa.String(100),   nullable=True),
        sa.Column("role",          sa.String(20),    nullable=False, server_default="admin"),
        sa.Column("is_active",     sa.Boolean(),     nullable=False, server_default="1"),
        sa.Column("permissions",   sa.JSON(),        nullable=False),
        sa.Column("last_login_at", sa.DateTime(),    nullable=True),
        sa.Column("created_at",    sa.DateTime(),    server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",    sa.DateTime(),    server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_admins_email", "admins", ["email"])

    # ── countries ────────────────────────────────────────────────────────────
    op.create_table(
        "countries",
        sa.Column("id",         sa.Integer(),    primary_key=True, autoincrement=True),
        sa.Column("name",       sa.String(100),  nullable=False),
        sa.Column("code",       sa.String(3),    nullable=False),
        sa.Column("is_active",  sa.Boolean(),    nullable=False, server_default="1"),
        sa.Column("sort_order", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_countries_code", "countries", ["code"])

    op.create_table(
        "country_states",
        sa.Column("id",           sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("country_code", sa.String(3),   nullable=False),
        sa.Column("name",         sa.String(100), nullable=False),
        sa.Column("code",         sa.String(10),  nullable=False),
        sa.Column("is_active",    sa.Boolean(),   nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["country_code"], ["countries.code"], ondelete="CASCADE"),
    )
    op.create_index("ix_country_states_country_code", "country_states", ["country_code"])

    # ── users ────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id",            sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("email",         sa.String(191), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("full_name",     sa.String(100), nullable=True),
        sa.Column("phone",         sa.String(30),  nullable=True),
        sa.Column("language_code", sa.String(10),  nullable=False, server_default="en"),
        sa.Column("role",          sa.String(20),  nullable=False, server_default="customer"),
        sa.Column("is_guest",      sa.Boolean(),   nullable=False, server_default="0"),
        sa.Column("is_active",     sa.Boolean(),   nullable=False, server_default="1"),
        sa.Column("agree_terms",   sa.Boolean(),   nullable=False, server_default="0"),
        sa.Column("agreed_at",     sa.DateTime(),  nullable=True),
        sa.Column("avatar_url",    sa.String(500), nullable=True),
        sa.Column("created_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "user_addresses",
        sa.Column("id",            sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("user_id",       sa.Integer(),   nullable=False),
        sa.Column("full_name",     sa.String(100), nullable=False),
        sa.Column("phone",         sa.String(30),  nullable=True),
        sa.Column("country_code",  sa.String(3),   nullable=False),
        sa.Column("state_code",    sa.String(10),  nullable=True),
        sa.Column("state_name",    sa.String(100), nullable=True),
        sa.Column("city",          sa.String(100), nullable=False),
        sa.Column("address_line1", sa.String(255), nullable=False),
        sa.Column("address_line2", sa.String(255), nullable=True),
        sa.Column("postal_code",   sa.String(20),  nullable=False),
        sa.Column("is_default",    sa.Boolean(),   nullable=False, server_default="0"),
        sa.Column("created_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_user_addresses_user_id", "user_addresses", ["user_id"])

    op.create_table(
        "oauth_accounts",
        sa.Column("id",               sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("user_id",          sa.Integer(),   nullable=False),
        sa.Column("provider",         sa.String(20),  nullable=False),
        sa.Column("provider_user_id", sa.String(255), nullable=False),
        sa.Column("access_token",     sa.Text(),      nullable=True),
        sa.Column("refresh_token",    sa.Text(),      nullable=True),
        sa.Column("created_at",       sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",       sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "password_reset_tokens",
        sa.Column("id",         sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("user_id",    sa.Integer(),   nullable=False),
        sa.Column("token",      sa.String(191), nullable=False),
        sa.Column("expires_at", sa.DateTime(),  nullable=False),
        sa.Column("used",       sa.Boolean(),   nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_password_reset_tokens_token", "password_reset_tokens", ["token"])

    op.create_table(
        "guest_claim_tokens",
        sa.Column("id",         sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("user_id",    sa.Integer(),   nullable=False),
        sa.Column("token",      sa.String(191), nullable=False),
        sa.Column("expires_at", sa.DateTime(),  nullable=False),
        sa.Column("used",       sa.Boolean(),   nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token"),
    )

    # ── categories ────────────────────────────────────────────────────────────
    op.create_table(
        "categories",
        sa.Column("id",          sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("name",        sa.String(100), nullable=False),
        sa.Column("slug",        sa.String(120), nullable=False),
        sa.Column("description", sa.Text(),      nullable=True),
        sa.Column("parent_id",   sa.Integer(),   nullable=True),
        sa.Column("sort_order",  sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("is_active",   sa.Boolean(),   nullable=False, server_default="1"),
        sa.Column("created_at",  sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",  sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["categories.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"])

    # ── products ──────────────────────────────────────────────────────────────
    op.create_table(
        "products",
        sa.Column("id",              sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("name",            sa.String(255), nullable=False),
        sa.Column("slug",            sa.String(191), nullable=False),
        sa.Column("description",     sa.Text(),      nullable=True),
        sa.Column("short_desc",      sa.String(500), nullable=True),
        sa.Column("category_id",     sa.Integer(),   nullable=True),
        sa.Column("is_published",    sa.Boolean(),   nullable=False, server_default="0"),
        sa.Column("rating_avg",      sa.Float(),     nullable=False, server_default="0"),
        sa.Column("rating_count",    sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("seo_title",       sa.String(255), nullable=True),
        sa.Column("seo_description", sa.String(500), nullable=True),
        sa.Column("seo_slug",        sa.String(280), nullable=True),
        sa.Column("og_image",        sa.String(500), nullable=True),
        sa.Column("created_at",      sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",      sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_products_slug",         "products", ["slug"])
    op.create_index("ix_products_is_published", "products", ["is_published"])

    op.create_table(
        "product_skus",
        sa.Column("id",                  sa.Integer(),        primary_key=True, autoincrement=True),
        sa.Column("product_id",          sa.Integer(),        nullable=False),
        sa.Column("sku_code",            sa.String(100),      nullable=False),
        sa.Column("price",               sa.Numeric(10, 2),   nullable=False),
        sa.Column("compare_price",       sa.Numeric(10, 2),   nullable=True),
        sa.Column("stock",               sa.Integer(),        nullable=False, server_default="0"),
        sa.Column("low_stock_threshold", sa.Integer(),        nullable=False, server_default="5"),
        sa.Column("variant_attrs",       sa.JSON(),           nullable=True),
        sa.Column("is_active",           sa.Boolean(),        nullable=False, server_default="1"),
        sa.Column("free_shipping",       sa.Boolean(),        nullable=False, server_default="0"),
        sa.Column("weight_grams",        sa.Integer(),        nullable=True),
        sa.Column("created_at",          sa.DateTime(),       server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",          sa.DateTime(),       server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("sku_code"),
    )
    op.create_index("ix_product_skus_product_id", "product_skus", ["product_id"])

    op.create_table(
        "product_images",
        sa.Column("id",           sa.Integer(),    primary_key=True, autoincrement=True),
        sa.Column("product_id",   sa.Integer(),    nullable=False),
        sa.Column("url",          sa.String(500),  nullable=False),
        sa.Column("storage_type", sa.String(10),   nullable=False, server_default="local"),
        sa.Column("alt_text",     sa.String(255),  nullable=True),
        sa.Column("sort_order",   sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("created_at",   sa.DateTime(),   server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "wishlist",
        sa.Column("id",         sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id",    sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"],    ["users.id"],    ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_wishlist_user_id", "wishlist", ["user_id"])

    op.create_table(
        "inventory_logs",
        sa.Column("id",           sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("sku_id",       sa.Integer(),   nullable=False),
        sa.Column("change_qty",   sa.Integer(),   nullable=False),
        sa.Column("before_qty",   sa.Integer(),   nullable=False),
        sa.Column("after_qty",    sa.Integer(),   nullable=False),
        sa.Column("reason",       sa.String(50),  nullable=False),
        sa.Column("reference_id", sa.String(100), nullable=True),
        sa.Column("operator_id",  sa.Integer(),   nullable=True),
        sa.Column("created_at",   sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["sku_id"],      ["product_skus.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["operator_id"], ["admins.id"],       ondelete="SET NULL"),
    )
    op.create_index("ix_inventory_logs_sku_id", "inventory_logs", ["sku_id"])

    # ── shipping ──────────────────────────────────────────────────────────────
    op.create_table(
        "shipping_regions",
        sa.Column("id",           sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("country_code", sa.String(3), nullable=False),
        sa.Column("state_code",   sa.String(10), nullable=True),
        sa.Column("enabled",      sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at",   sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",   sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_shipping_regions_country", "shipping_regions", ["country_code"])

    op.create_table(
        "shipping_zones",
        sa.Column("id",         sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("name",       sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(),  server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "shipping_zone_regions",
        sa.Column("id",           sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("zone_id",      sa.Integer(), nullable=False),
        sa.Column("country_code", sa.String(3), nullable=False),
        sa.ForeignKeyConstraint(["zone_id"], ["shipping_zones.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_shipping_zone_regions_zone_id",      "shipping_zone_regions", ["zone_id"])
    op.create_index("ix_shipping_zone_regions_country_code", "shipping_zone_regions", ["country_code"])

    op.create_table(
        "shipping_rules",
        sa.Column("id",                      sa.Integer(),      primary_key=True, autoincrement=True),
        sa.Column("zone_id",                 sa.Integer(),      nullable=False),
        sa.Column("shipping_fee",            sa.Numeric(10, 2), nullable=False),
        sa.Column("free_shipping_threshold", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_active",               sa.Boolean(),      nullable=False, server_default="1"),
        sa.Column("created_at",              sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",              sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["zone_id"], ["shipping_zones.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "logistics_carriers",
        sa.Column("id",                    sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("name",                  sa.String(100), nullable=False),
        sa.Column("code",                  sa.String(30),  nullable=False),
        sa.Column("tracking_url_template", sa.String(500), nullable=True),
        sa.Column("applicable_countries",  sa.JSON(),      nullable=True),
        sa.Column("is_active",             sa.Boolean(),   nullable=False, server_default="1"),
        sa.Column("created_at",            sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",            sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("code"),
    )

    # ── tax ───────────────────────────────────────────────────────────────────
    op.create_table(
        "tax_rules",
        sa.Column("id",                sa.Integer(),      primary_key=True, autoincrement=True),
        sa.Column("country_code",      sa.String(3),      nullable=False),
        sa.Column("state_code",        sa.String(10),     nullable=True),
        sa.Column("tax_rate",          sa.Numeric(5, 4),  nullable=False),
        sa.Column("tax_name",          sa.String(50),     nullable=False, server_default="Sales Tax"),
        sa.Column("apply_to_shipping", sa.Boolean(),      nullable=False, server_default="0"),
        sa.Column("category_id",       sa.Integer(),      nullable=True),
        sa.Column("is_active",         sa.Boolean(),      nullable=False, server_default="1"),
        sa.Column("created_at",        sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",        sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_tax_rules_country", "tax_rules", ["country_code"])

    # ── marketing ─────────────────────────────────────────────────────────────
    op.create_table(
        "coupons",
        sa.Column("id",               sa.Integer(),      primary_key=True, autoincrement=True),
        sa.Column("code",             sa.String(50),     nullable=False),
        sa.Column("type",             sa.String(20),     nullable=False),
        sa.Column("value",            sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("min_order_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_uses",         sa.Integer(),      nullable=True),
        sa.Column("used_count",       sa.Integer(),      nullable=False, server_default="0"),
        sa.Column("starts_at",        sa.DateTime(),     nullable=True),
        sa.Column("ends_at",          sa.DateTime(),     nullable=True),
        sa.Column("is_active",        sa.Boolean(),      nullable=False, server_default="1"),
        sa.Column("description",      sa.String(255),    nullable=True),
        sa.Column("created_at",       sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",       sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_coupons_code", "coupons", ["code"])

    op.create_table(
        "banners",
        sa.Column("id",         sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("title",      sa.String(255), nullable=False),
        sa.Column("subtitle",   sa.String(500), nullable=True),
        sa.Column("coupon_id",  sa.Integer(),   nullable=True),
        sa.Column("link_url",   sa.String(500), nullable=True),
        sa.Column("starts_at",  sa.DateTime(),  nullable=True),
        sa.Column("ends_at",    sa.DateTime(),  nullable=True),
        sa.Column("is_active",  sa.Boolean(),   nullable=False, server_default="1"),
        sa.Column("sort_order", sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["coupon_id"], ["coupons.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "newsletter_subscribers",
        sa.Column("id",              sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("email",           sa.String(191), nullable=False),
        sa.Column("source",          sa.String(20),  nullable=False, server_default="footer"),
        sa.Column("status",          sa.String(20),  nullable=False, server_default="active"),
        sa.Column("language_code",   sa.String(10),  nullable=False, server_default="en"),
        sa.Column("unsub_token",     sa.String(191), nullable=True),
        sa.Column("subscribed_at",   sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("unsubscribed_at", sa.DateTime(),  nullable=True),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("unsub_token"),
    )
    op.create_index("ix_newsletter_subscribers_email", "newsletter_subscribers", ["email"])

    op.create_table(
        "marketing_channels",
        sa.Column("id",         sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("name",       sa.String(100), nullable=False),
        sa.Column("ref_code",   sa.String(50),  nullable=False),
        sa.Column("platform",   sa.String(50),  nullable=True),
        sa.Column("is_active",  sa.Boolean(),   nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("ref_code"),
    )
    op.create_index("ix_marketing_channels_ref_code", "marketing_channels", ["ref_code"])

    # ── orders ────────────────────────────────────────────────────────────────
    op.create_table(
        "orders",
        sa.Column("id",                 sa.Integer(),      primary_key=True, autoincrement=True),
        sa.Column("order_no",           sa.String(40),     nullable=False),
        sa.Column("user_id",            sa.Integer(),      nullable=True),
        sa.Column("status",             sa.String(30),     nullable=False, server_default="pending_payment"),
        sa.Column("subtotal",           sa.Numeric(10, 2), nullable=False),
        sa.Column("shipping_fee",       sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("tax_amount",         sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("discount_amount",    sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("total_amount",       sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_method",     sa.String(30),     nullable=True),
        sa.Column("payment_status",     sa.String(30),     nullable=False, server_default="unpaid"),
        sa.Column("coupon_code",        sa.String(50),     nullable=True),
        sa.Column("shipping_address",   sa.JSON(),         nullable=True),
        sa.Column("shipping_zone_name", sa.String(100),    nullable=True),
        sa.Column("shipping_rule_id",   sa.Integer(),      nullable=True),
        sa.Column("tax_rule_id",        sa.Integer(),      nullable=True),
        sa.Column("tax_rate_snapshot",  sa.Numeric(5, 4),  nullable=True),
        sa.Column("channel_ref",        sa.String(100),    nullable=True),
        sa.Column("channel_id",         sa.Integer(),      nullable=True),
        sa.Column("guest_email",        sa.String(255),    nullable=True),
        sa.Column("language_code",      sa.String(10),     nullable=False, server_default="en"),
        sa.Column("customer_note",      sa.Text(),         nullable=True),
        sa.Column("admin_note",         sa.Text(),         nullable=True),
        sa.Column("created_at",         sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",         sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"],         ["users.id"],            ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["shipping_rule_id"],["shipping_rules.id"],   ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tax_rule_id"],     ["tax_rules.id"],        ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["channel_id"],      ["marketing_channels.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("order_no"),
    )
    op.create_index("ix_orders_order_no", "orders", ["order_no"])
    op.create_index("ix_orders_user_id",  "orders", ["user_id"])
    op.create_index("ix_orders_status",   "orders", ["status"])

    op.create_table(
        "order_items",
        sa.Column("id",            sa.Integer(),      primary_key=True, autoincrement=True),
        sa.Column("order_id",      sa.Integer(),      nullable=False),
        sa.Column("sku_id",        sa.Integer(),      nullable=True),
        sa.Column("product_name",  sa.String(255),    nullable=False),
        sa.Column("sku_code",      sa.String(100),    nullable=False),
        sa.Column("variant_attrs", sa.JSON(),         nullable=True),
        sa.Column("quantity",      sa.Integer(),      nullable=False),
        sa.Column("unit_price",    sa.Numeric(10, 2), nullable=False),
        sa.Column("subtotal",      sa.Numeric(10, 2), nullable=False),
        sa.Column("product_image", sa.String(500),    nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"],      ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sku_id"],   ["product_skus.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])

    op.create_table(
        "order_status_logs",
        sa.Column("id",          sa.Integer(),  primary_key=True, autoincrement=True),
        sa.Column("order_id",    sa.Integer(),  nullable=False),
        sa.Column("from_status", sa.String(30), nullable=True),
        sa.Column("to_status",   sa.String(30), nullable=False),
        sa.Column("note",        sa.String(500), nullable=True),
        sa.Column("operator_id", sa.Integer(),  nullable=True),
        sa.Column("created_at",  sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"],    ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["operator_id"], ["admins.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "channel_events",
        sa.Column("id",         sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("channel_id", sa.Integer(),   nullable=False),
        sa.Column("order_id",   sa.Integer(),   nullable=True),
        sa.Column("event_type", sa.String(20),  nullable=False),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["channel_id"], ["marketing_channels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"],   ["orders.id"],             ondelete="SET NULL"),
    )
    op.create_index("ix_channel_events_channel_id", "channel_events", ["channel_id"])

    # ── payments ──────────────────────────────────────────────────────────────
    op.create_table(
        "payments",
        sa.Column("id",                  sa.Integer(),      primary_key=True, autoincrement=True),
        sa.Column("order_id",            sa.Integer(),      nullable=False),
        sa.Column("provider",            sa.String(20),     nullable=False),
        sa.Column("provider_payment_id", sa.String(191),    nullable=True),
        sa.Column("amount",              sa.Numeric(10, 2), nullable=False),
        sa.Column("currency",            sa.String(10),     nullable=False, server_default="USD"),
        sa.Column("status",              sa.String(30),     nullable=False),
        sa.Column("raw_response",        sa.JSON(),         nullable=True),
        sa.Column("created_at",          sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",          sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_payments_order_id",            "payments", ["order_id"])
    op.create_index("ix_payments_provider_payment_id", "payments", ["provider_payment_id"])

    op.create_table(
        "refunds",
        sa.Column("id",                 sa.Integer(),      primary_key=True, autoincrement=True),
        sa.Column("payment_id",         sa.Integer(),      nullable=False),
        sa.Column("provider_refund_id", sa.String(255),    nullable=True),
        sa.Column("amount",             sa.Numeric(10, 2), nullable=False),
        sa.Column("reason",             sa.String(255),    nullable=True),
        sa.Column("status",             sa.String(30),     nullable=False, server_default="pending"),
        sa.Column("processed_by",       sa.Integer(),      nullable=True),
        sa.Column("created_at",         sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",         sa.DateTime(),     server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["payment_id"],   ["payments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["processed_by"], ["admins.id"],   ondelete="SET NULL"),
    )

    op.create_table(
        "payment_webhooks",
        sa.Column("id",           sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("provider",     sa.String(20),  nullable=False),
        sa.Column("event_type",   sa.String(100), nullable=False),
        sa.Column("event_id",     sa.String(191), nullable=True),
        sa.Column("order_id",     sa.Integer(),   nullable=True),
        sa.Column("status",       sa.String(20),  nullable=False, server_default="received"),
        sa.Column("raw_payload",  sa.JSON(),      nullable=True),
        sa.Column("error_msg",    sa.Text(),      nullable=True),
        sa.Column("created_at",   sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("processed_at", sa.DateTime(),  nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index("ix_payment_webhooks_provider",   "payment_webhooks", ["provider"])
    op.create_index("ix_payment_webhooks_event_type", "payment_webhooks", ["event_type"])
    op.create_index("ix_payment_webhooks_order_id",   "payment_webhooks", ["order_id"])

    op.create_table(
        "payment_failed_email_logs",
        sa.Column("id",       sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("sent_at",  sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("order_id"),
    )

    # ── shipments ─────────────────────────────────────────────────────────────
    op.create_table(
        "shipments",
        sa.Column("id",          sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("order_id",    sa.Integer(),   nullable=False),
        sa.Column("carrier_id",  sa.Integer(),   nullable=False),
        sa.Column("tracking_no", sa.String(100), nullable=False),
        sa.Column("shipped_by",  sa.Integer(),   nullable=True),
        sa.Column("shipped_at",  sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("note",        sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(["order_id"],   ["orders.id"],            ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["carrier_id"], ["logistics_carriers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["shipped_by"], ["admins.id"],             ondelete="SET NULL"),
        sa.UniqueConstraint("order_id"),
    )
    op.create_index("ix_shipments_order_id", "shipments", ["order_id"])

    # ── product reviews ───────────────────────────────────────────────────────
    op.create_table(
        "product_reviews",
        sa.Column("id",                   sa.Integer(),    primary_key=True, autoincrement=True),
        sa.Column("product_id",           sa.Integer(),    nullable=False),
        sa.Column("user_id",              sa.Integer(),    nullable=False),
        sa.Column("order_id",             sa.Integer(),    nullable=True),
        sa.Column("rating",               sa.SmallInteger(), nullable=False),
        sa.Column("content",              sa.Text(),       nullable=True),
        sa.Column("status",               sa.String(20),   nullable=False, server_default="pending"),
        sa.Column("reject_reason",        sa.String(255),  nullable=True),
        sa.Column("reviewer_name",        sa.String(100),  nullable=True),
        sa.Column("is_verified_purchase", sa.Boolean(),    nullable=False, server_default="0"),
        sa.Column("created_at",           sa.DateTime(),   server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",           sa.DateTime(),   server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"],    ["users.id"],    ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"],   ["orders.id"],   ondelete="SET NULL"),
    )
    op.create_index("ix_product_reviews_product_id", "product_reviews", ["product_id"])
    op.create_index("ix_product_reviews_status",     "product_reviews", ["status"])

    op.create_table(
        "review_media",
        sa.Column("id",           sa.Integer(),    primary_key=True, autoincrement=True),
        sa.Column("review_id",    sa.Integer(),    nullable=False),
        sa.Column("url",          sa.String(500),  nullable=False),
        sa.Column("storage_type", sa.String(10),   nullable=False, server_default="local"),
        sa.Column("media_type",   sa.String(10),   nullable=False),
        sa.Column("sort_order",   sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("created_at",   sa.DateTime(),   server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["review_id"], ["product_reviews.id"], ondelete="CASCADE"),
    )

    # ── content ───────────────────────────────────────────────────────────────
    op.create_table(
        "blog_categories",
        sa.Column("id",         sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("name",       sa.String(100), nullable=False),
        sa.Column("slug",       sa.String(120), nullable=False),
        sa.Column("is_active",  sa.Boolean(),   nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "blog_posts",
        sa.Column("id",               sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("title",            sa.String(255), nullable=False),
        sa.Column("slug",             sa.String(191), nullable=False),
        sa.Column("excerpt",          sa.String(500), nullable=True),
        sa.Column("content",          sa.Text(),      nullable=True),
        sa.Column("author",           sa.String(100), nullable=True),
        sa.Column("cover_image_url",  sa.String(500), nullable=True),
        sa.Column("cover_storage_type", sa.String(10), nullable=False, server_default="local"),
        sa.Column("category_id",      sa.Integer(),   nullable=True),
        sa.Column("is_published",     sa.Boolean(),   nullable=False, server_default="0"),
        sa.Column("published_at",     sa.DateTime(),  nullable=True),
        sa.Column("seo_title",        sa.String(255), nullable=True),
        sa.Column("seo_description",  sa.String(500), nullable=True),
        sa.Column("og_image",         sa.String(500), nullable=True),
        sa.Column("created_at",       sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",       sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["blog_categories.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_blog_posts_is_published", "blog_posts", ["is_published"])

    op.create_table(
        "faqs",
        sa.Column("id",            sa.Integer(),    primary_key=True, autoincrement=True),
        sa.Column("question",      sa.Text(),       nullable=False),
        sa.Column("answer",        sa.Text(),       nullable=False),
        sa.Column("category",      sa.String(100),  nullable=True),
        sa.Column("sort_order",    sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("language_code", sa.String(10),   nullable=False, server_default="en"),
        sa.Column("is_active",     sa.Boolean(),    nullable=False, server_default="1"),
        sa.Column("created_at",    sa.DateTime(),   server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",    sa.DateTime(),   server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "cms_pages",
        sa.Column("id",            sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("page_type",     sa.String(50),  nullable=False),
        sa.Column("language_code", sa.String(10),  nullable=False, server_default="en"),
        sa.Column("title",         sa.String(255), nullable=False),
        sa.Column("content",       sa.Text(),      nullable=True),
        sa.Column("is_published",  sa.Boolean(),   nullable=False, server_default="1"),
        sa.Column("created_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cms_pages_page_type", "cms_pages", ["page_type"])

    op.create_table(
        "email_templates",
        sa.Column("id",            sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("type",          sa.String(50),  nullable=False),
        sa.Column("language_code", sa.String(10),  nullable=False, server_default="en"),
        sa.Column("subject",       sa.String(255), nullable=False),
        sa.Column("body",          sa.Text(),      nullable=False),
        sa.Column("is_active",     sa.Boolean(),   nullable=False, server_default="1"),
        sa.Column("created_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_email_templates_type", "email_templates", ["type"])

    op.create_table(
        "cookie_consent_configs",
        sa.Column("id",            sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("language_code", sa.String(10),  nullable=False, server_default="en"),
        sa.Column("title",         sa.String(255), nullable=False),
        sa.Column("description",   sa.Text(),      nullable=False),
        sa.Column("accept_btn",    sa.String(100), nullable=False),
        sa.Column("reject_btn",    sa.String(100), nullable=False),
        sa.Column("customize_btn", sa.String(100), nullable=True),
        sa.Column("is_active",     sa.Boolean(),   nullable=False, server_default="1"),
        sa.Column("created_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "site_settings",
        sa.Column("id",            sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("setting_key",   sa.String(100), nullable=False),
        sa.Column("setting_value", sa.Text(),      nullable=True),
        sa.Column("description",   sa.String(255), nullable=True),
        sa.Column("created_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("setting_key"),
    )
    op.create_index("ix_site_settings_key", "site_settings", ["setting_key"])

    op.create_table(
        "language_packs",
        sa.Column("id",            sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("language_code", sa.String(10),  nullable=False),
        sa.Column("pack_key",      sa.String(200), nullable=False),
        sa.Column("pack_value",    sa.Text(),      nullable=False),
        sa.Column("created_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",    sa.DateTime(),  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_language_packs_lang", "language_packs", ["language_code"])

    op.create_table(
        "media_files",
        sa.Column("id",           sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("filename",     sa.String(255), nullable=False),
        sa.Column("path",         sa.String(500), nullable=False),
        sa.Column("storage_type", sa.String(10),  nullable=False),
        sa.Column("file_type",    sa.String(20),  nullable=False),
        sa.Column("mime_type",    sa.String(100), nullable=True),
        sa.Column("size_bytes",   sa.Integer(),   nullable=True),
        sa.Column("width",        sa.Integer(),   nullable=True),
        sa.Column("height",       sa.Integer(),   nullable=True),
        sa.Column("uploaded_by",  sa.Integer(),   nullable=True),
        sa.Column("created_at",   sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",   sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["uploaded_by"], ["admins.id"], ondelete="SET NULL"),
    )


def downgrade() -> None:
    tables = [
        "media_files", "language_packs", "site_settings",
        "cookie_consent_configs", "email_templates", "cms_pages",
        "faqs", "blog_posts", "blog_categories",
        "review_media", "product_reviews",
        "shipments", "payment_failed_email_logs",
        "payment_webhooks", "refunds", "payments",
        "channel_events", "order_status_logs", "order_items", "orders",
        "marketing_channels", "newsletter_subscribers",
        "banners", "coupons",
        "tax_rules", "logistics_carriers",
        "shipping_rules", "shipping_zone_regions", "shipping_zones", "shipping_regions",
        "inventory_logs", "wishlist", "product_images", "product_skus", "products",
        "categories", "guest_claim_tokens", "password_reset_tokens",
        "oauth_accounts", "user_addresses", "users",
        "country_states", "countries", "admins",
    ]
    for t in tables:
        op.drop_table(t)
