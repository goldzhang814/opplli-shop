# Import all models so SQLAlchemy / Alembic can discover them
from app.models.admin    import Admin                                           # noqa
from app.models.user     import User, UserAddress, OAuthAccount                 # noqa
from app.models.user     import PasswordResetToken, GuestClaimToken             # noqa
from app.models.product  import (                                               # noqa
    Category, Product, ProductSku, ProductImage,
    InventoryLog, ProductReview, ReviewMedia, Wishlist,
)
from app.models.order    import Order, OrderItem, OrderStatusLog                # noqa
from app.models.payment  import Payment, Refund, PaymentWebhook                 # noqa
from app.models.payment  import PaymentFailedEmailLog                           # noqa
from app.models.shipping import (                                               # noqa
    ShippingRegion, ShippingZone, ShippingZoneRegion,
    ShippingRule, LogisticsCarrier, Shipment,
)
from app.models.tax      import TaxRule                                         # noqa
from app.models.marketing import (                                              # noqa
    Coupon, Banner, NewsletterSubscriber,
    MarketingChannel, ChannelEvent,
)
from app.models.content  import (                                               # noqa
    BlogCategory, BlogPost, Faq, CmsPage,
    EmailTemplate, CookieConsentConfig,
    SiteSetting, LanguagePack,
    Country, CountryState, MediaFile,
)
