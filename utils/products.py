from account.models import UserProduct
from store.models import Sell
from store.tasks import send_sell_receipt_to_user_email

from helpers.choices import ProductTypes


def assign_product_to_user(sell: Sell):
    """Assign a product to a user."""

    user = sell.user
    products = sell.products.all()
    user_products = []
    for product in products:
        if product.type == ProductTypes.PACKAGE:
            # If the product is a package, add its items instead
            package_items = product.items.all()
            user_products.extend(
                [UserProduct(user=user, product=item) for item in package_items]
            )
        else:
            # Add non-package products directly
            user_products.append(UserProduct(user=user, product=product))

    UserProduct.objects.bulk_create(user_products)
    sell.generate_receipt()
    sell.save()
    send_sell_receipt_to_user_email(sell)
