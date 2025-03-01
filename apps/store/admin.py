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


# admin.site.register(Product, ProductsAdmin)
admin.site.register(Category)
admin.site.register(Attribute)
admin.site.register(AttributeOption)
# admin.site.register(ProductAttribute)
# admin.site.register(VideoPart)
admin.site.register(Sell)
admin.site.register(Claim)
