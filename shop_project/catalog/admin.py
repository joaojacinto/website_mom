from django.contrib import admin
from django.utils.html import format_html

from .models import Product, ProductImage, ContactRequest


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("preview", "image", "order")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="height:70px;border-radius:6px;object-fit:cover;" />',
                obj.image.url,
            )
        return "(sem foto ainda)"

    preview.short_description = "Pré-visualização"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "thumbnail",
        "name",
        "category",
        "display_price",
        "is_active",
        "order",
    )
    list_display_links = ("thumbnail", "name")
    list_editable = ("is_active", "order")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]

    fieldsets = (
        ("Informação principal", {
            "fields": ("name", "slug", "category", "is_active", "order"),
        }),
        ("Descrição e preço", {
            "fields": ("short_description", "description", "price", "price_note"),
        }),
        ("Detalhes — só para ficheiros digitais", {
            "fields": ("print_time", "weight", "digital_file"),
            "description": "Preenche esta secção apenas se o produto for do tipo \"Ficheiro digital\".",
        }),
        ("Detalhes — só para peças impressas", {
            "fields": ("material", "lead_time"),
            "description": "Preenche esta secção apenas se o produto for do tipo \"Peça impressa\".",
        }),
    )

    def thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            return format_html(
                '<img src="{}" style="height:50px;width:50px;border-radius:6px;object-fit:cover;" />',
                first_image.image.url,
            )
        return "—"

    thumbnail.short_description = "Foto"

    def display_price(self, obj):
        return obj.display_price

    display_price.short_description = "Preço"


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_info", "product_interest", "created_at", "handled")
    list_editable = ("handled",)
    list_filter = ("handled",)
    search_fields = ("name", "contact_info", "message")
    readonly_fields = ("name", "contact_info", "product_interest", "message", "created_at")


admin.site.site_header = "Administração da Loja"
admin.site.site_title = "Loja — Admin"
admin.site.index_title = "Gerir catálogo e pedidos"
