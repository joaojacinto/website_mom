# Website de design e impressão 3D

Este repositório contém um website de catálogo para apresentar modelos de
design e impressão 3D. O catálogo distingue entre ficheiros digitais e peças
impressas, permitindo mostrar informação, imagens e preços dos produtos e
receber pedidos de contacto ou orçamento.

## Funcionalidades principais

- Catálogo público de produtos ativos, ordenados pela configuração do
  catálogo.
- Classificação dos produtos como ficheiro digital ou peça impressa.
- Informação específica por tipo: tempo de impressão e peso para ficheiros
  digitais; material e prazo de entrega para peças físicas.
- Galeria de imagens com visualização ampliada dos produtos.
- Formulário de contacto para pedidos de orçamento, encomendas ou peças
  personalizadas.
- Painel de administração Django para gerir produtos, fotografias e pedidos
  de contacto, sem editar o código.
- Página de apresentação do projeto e uma animação 3D demonstrativa baseada
  em Three.js.

## Stack

- **Python** e **Django 5** para a aplicação web, rotas, modelos e
  administração.
- **SQLite** como base de dados configurada para desenvolvimento.
- **Pillow** para suporte às imagens dos produtos.
- **HTML**, **CSS** e **JavaScript** no frontend.
- **Three.js**, carregado por CDN através de um `importmap`, para a
  visualização 3D demonstrativa.

A aplicação Django encontra-se em `shop_project/`. O ficheiro `index.html` e
`styles.css` na raiz correspondem à interface estática original; a versão
integrada com catálogo e administração está em `shop_project/catalog/`.

## Desenvolvimento local

Os ficheiros do projeto documentam a execução local com um ambiente virtual
Python. A partir da raiz do repositório:

```bash
cd shop_project
python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Depois, aceda a `http://127.0.0.1:8000/` para o site e a
`http://127.0.0.1:8000/admin/` para o painel de administração.
