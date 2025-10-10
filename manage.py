#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import debugpy


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainapp.settings')

      # --- Debugging section ---
    # Only activate when you want to debug
    if os.environ.get("DJANGO_DEBUGPY") == "1":
        debugpy.listen(("0.0.0.0", 5678))
        print("Waiting for debugger attach on port 5678...")
        debugpy.wait_for_client()  # Blocks until debugger is attached
    # ---------------------------

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
