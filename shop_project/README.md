# Loja de Impressão 3D — Django

Site de catálogo (ficheiros digitais + peças impressas), com painel de
administração para adicionar/editar produtos sem tocar em código.

## Como correr o projeto (primeira vez)

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # cria a conta de admin (nome de utilizador + password)

python manage.py runserver
```

Depois abre:
- **Site**: http://127.0.0.1:8000/
- **Painel de admin**: http://127.0.0.1:8000/admin/

## Guia rápido para quem gere o catálogo (sem código)

1. Entra em `/admin/` com o utilizador e password criados no `createsuperuser`.
2. Clica em **Produtos** → **Adicionar produto**.
3. Preenche:
   - **Nome** e **Tipo de produto** (ficheiro digital ou peça impressa)
   - **Preço**
   - Descrição curta/completa (opcional, mas ajuda o cliente)
   - Se for peça impressa: Material e Prazo de entrega
   - Se for ficheiro digital: Tempo de impressão, Peso, e o ficheiro STL/3MF
4. Mais abaixo, em **Fotos do produto**, clica em **Escolher ficheiro** para
   cada foto e carrega-as — a primeira foto (ordem mais baixa) é a que
   aparece no cartão do catálogo.
5. Confirma que **Visível no site** está marcado, e clica em **Guardar**.

O produto aparece imediatamente no site, sem precisares de mexer em
nenhum ficheiro. Para o esconder temporariamente (ex: esgotado), volta ao
produto e desmarca **Visível no site** — não precisas de o apagar.

Os pedidos enviados pelo formulário de contacto do site ficam guardados
em **Pedidos de contacto**, no mesmo painel.

## Antes de publicar o site a sério (produção)

- Troca `SECRET_KEY` em `shop_project/settings.py` por uma nova
  (gera uma em https://djecrety.ir/)
- Muda `DEBUG = False`
- Define `ALLOWED_HOSTS` com o domínio real
- Troca a base de dados SQLite por Postgres (recomendado para produção)
- Configura um serviço de storage (ex: S3) para as fotos e ficheiros
  digitais em vez do disco local
- Este README assume alojamento tipo Render/Railway/PythonAnywhere —
  qualquer um deles tem guias próprios para "deploy de um projeto Django"
