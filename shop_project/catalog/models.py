from django.db import models
from django.utils.text import slugify


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("digital", "Ficheiro digital (download)"),
        ("physical", "Peça impressa (enviada por correio)"),
    ]

    name = models.CharField(
        "Nome do produto",
        max_length=200,
        help_text="Ex: Vaso geométrico",
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text="Preenchido automaticamente a partir do nome. Não precisas de mexer aqui.",
    )
    category = models.CharField(
        "Tipo de produto",
        max_length=10,
        choices=CATEGORY_CHOICES,
        default="physical",
    )
    short_description = models.CharField(
        "Descrição curta",
        max_length=160,
        blank=True,
        help_text="Uma frase curta que aparece no cartão do catálogo (opcional).",
    )
    description = models.TextField(
        "Descrição completa",
        blank=True,
        help_text="Texto mais longo, mostrado quando o cliente abre a janela de detalhes.",
    )
    price = models.DecimalField(
        "Preço (€)",
        max_digits=8,
        decimal_places=2,
    )
    price_note = models.CharField(
        "Nota de preço",
        max_length=40,
        blank=True,
        help_text='Ex: "desde", para mostrar "desde 10,50 €". Deixa em branco se não for preciso.',
    )

    # Campos específicos para modelos digitais
    print_time = models.CharField(
        "Tempo de impressão",
        max_length=40,
        blank=True,
        help_text='Só para ficheiros digitais. Ex: "4h30".',
    )
    weight = models.CharField(
        "Peso",
        max_length=40,
        blank=True,
        help_text='Só para ficheiros digitais. Ex: "68g".',
    )
    digital_file = models.FileField(
        "Ficheiro para download",
        upload_to="digital_files/",
        blank=True,
        null=True,
        help_text="Só para ficheiros digitais. O ficheiro STL/3MF que o cliente vai descarregar.",
    )

    # Campos específicos para peças físicas
    material = models.CharField(
        "Material",
        max_length=60,
        blank=True,
        help_text='Só para peças impressas. Ex: "PLA", "PETG".',
    )
    lead_time = models.CharField(
        "Prazo de entrega",
        max_length=60,
        blank=True,
        help_text='Só para peças impressas. Ex: "3-5 dias".',
    )

    is_active = models.BooleanField(
        "Visível no site",
        default=True,
        help_text="Desmarca para esconder o produto do site sem o apagar.",
    )
    order = models.PositiveIntegerField(
        "Ordem",
        default=0,
        help_text="Produtos com número mais baixo aparecem primeiro no catálogo.",
    )
    created_at = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            i = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def display_price(self):
        if self.price_note:
            return f"{self.price_note} {self.price:.2f}\u00a0€".replace(".", ",")
        return f"{self.price:.2f}\u00a0€".replace(".", ",")


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE,
        verbose_name="Produto",
    )
    image = models.ImageField(
        "Foto",
        upload_to="product_images/",
    )
    order = models.PositiveIntegerField(
        "Ordem",
        default=0,
        help_text="A foto com número mais baixo aparece primeiro (é a foto principal).",
    )

    class Meta:
        verbose_name = "Foto do produto"
        verbose_name_plural = "Fotos do produto"
        ordering = ["order", "id"]

    def __str__(self):
        return f"Foto de {self.product.name}"


class ContactRequest(models.Model):
    """Regista os pedidos enviados pelo formulário de contacto do site."""

    name = models.CharField("Nome", max_length=120)
    contact_info = models.CharField("Email ou WhatsApp", max_length=120)
    product_interest = models.CharField("Peça de interesse", max_length=200, blank=True)
    message = models.TextField("Mensagem", blank=True)
    created_at = models.DateTimeField("Recebido em", auto_now_add=True)
    handled = models.BooleanField("Já respondido", default=False)

    class Meta:
        verbose_name = "Pedido de contacto"
        verbose_name_plural = "Pedidos de contacto"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.created_at:%d/%m/%Y}"
