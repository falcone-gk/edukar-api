from django.contrib import admin
from django.utils.html import format_html
from store.models import (
    Attribute,
    AttributeOption,
    Category,
    Claim,
    Product,
    ProductAttribute,
    Sell,
    VideoPart,
)

# Register your models here.


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


class VideoPartInline(admin.TabularInline):
    model = VideoPart
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "type",
        "show",
        "identifier",
    )
    list_filter = ("category", "type", "show")
    search_fields = ("name", "slug", "identifier", "category__name")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("identifier", "display_image")
    list_editable = ("price", "show")

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "price",
                    "category",
                    "type",
                    "source",
                    "show",
                ),
            },
        ),
        (
            "Media",
            {
                "fields": ("product_image", "display_image"),
            },
        ),
        (
            "Advanced",
            {
                "fields": ("identifier", "items"),
                "classes": ("collapse",),
            },
        ),
    )

    filter_horizontal = ("items",)  # Makes ManyToMany field more user-friendly

    def display_image(self, obj):
        """Show a small thumbnail of the product image in admin."""
        if obj.product_image:
            return format_html(
                f'<img src="{obj.product_image.url}" width="50" height="50" style="border-radius:5px;" />'
            )
        return "No Image"

    inlines = [ProductAttributeInline, VideoPartInline]


@admin.register(Sell)
class SellAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_number",
        "user",
        "status",
        "total_cost",
        "paid_at",
        "order_id",
    )
    list_filter = ("status", "paid_at")
    search_fields = (
        "user__username",
        "user_name",
        "user_last_name",
        "user_email",
        "sell_identifier",
        "order_id",
    )
    ordering = ("-receipt_number", "-paid_at")
    readonly_fields = ("order_id", "order_number", "receipt_number")


admin.site.register(Category)
admin.site.register(Attribute)
admin.site.register(AttributeOption)
admin.site.register(Claim)
