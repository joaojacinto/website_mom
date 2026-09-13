from django.contrib import messages
from django.shortcuts import redirect, render

from .models import ContactRequest, Product


def home(request):
    products = Product.objects.filter(is_active=True).prefetch_related("images")
    return render(request, "catalog/index.html", {"products": products})


def submit_contact(request):
    if request.method != "POST":
        return redirect("/#contact")

    name = request.POST.get("name", "").strip()
    contact_info = request.POST.get("contact_info", "").strip()
    if not name or not contact_info:
        messages.error(request, "Indica o teu nome e um email ou WhatsApp para enviar o pedido.")
        return redirect("/#contact")

    ContactRequest.objects.create(
        name=name,
        contact_info=contact_info,
        product_interest=request.POST.get("product", "").strip(),
        message=request.POST.get("message", "").strip(),
    )
    messages.success(request, "Pedido enviado! Vamos responder brevemente.")
    return redirect("/#contact")
