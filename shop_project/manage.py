#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não consegui importar o Django. Confirma que o ambiente virtual "
            "está ativo e que instalaste os requirements (pip install -r requirements.txt)."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
