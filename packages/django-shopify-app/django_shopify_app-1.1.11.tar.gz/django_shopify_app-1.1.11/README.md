# django-shopify-app

Add the app in settings.py

```plain

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'shopify_app',
        'shops',
    ]

```

Add the required configurations in settings.py

```plain

    SHOPIFY_API_KEY = config('SHOPIFY_API_KEY')
    SHOPIFY_API_SECRET = config('SHOPIFY_API_SECRET')
    SHOPIFY_APP_SCOPES = ['read_products', 'read_orders']
    SHOPIFY_APP_HOST = 'https://moship.ngrok.io'

    SHOPIFY_SHOP_MODEL = 'shops.Shop'

    SHOPIFY_WEBHOOK_HOST = 'https://moship.ngrok.io'
    SHOPIFY_WEBHOOK_TOPICS = [
        'products/update',
        'orders/updated',
        'app/uninstalled'
    ]

    SHOPIFY_WEBHOOK_CALLBACK = 'shops.webhooks.webhook_entry'
    SHOPIFY_GDPR_WEBHOOK_CALLBACK = 'shops.webhooks.gdpr_webhook_entry'

    SHOPIFY_GOOGLE_PUBSUB_PROJECT_ID = config('SHOPIFY_GOOGLE_PUBSUB_PROJECT_ID')
    SHOPIFY_GOOGLE_PUBSUB_TOPIC_ID = config('SHOPIFY_GOOGLE_PUBSUB_TOPIC_ID')
    SHOPIFY_GOOGLE_PUBSUB_SUB_NAME = config('SHOPIFY_GOOGLE_PUBSUB_SUB_NAME')
    SHOPIFY_GOOGLE_PUBSUB_SERVICE_ACCOUNT_STRING = config(
        'SHOPIFY_GOOGLE_PUBSUB_SERVICE_ACCOUNT_STRING'
    )

    SHOPIFY_DEV_SHOPIFY_DOMAIN = None

```

Create a path to init the access token request and another path to end the token request

```plain

    from django.urls import path

    from shopify_app.views import InitTokenRequestView, EndTokenRequestView

    app_name = 'my_shopify_app'


    urlpatterns = [
        path(
            'login-online/',
            InitTokenRequestView.as_view(
                redirect_path_name='my_shopify_app:end-token-request',
            ),
        ),
        path(
            'confirm/',
            EndTokenRequestView.as_view(
                redirect_path_name='embed_admin:dashboard',
            ),
            name='end-token-request'
        ),
    ]

```
