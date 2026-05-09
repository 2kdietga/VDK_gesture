import subprocess
import sys
from pathlib import Path

from django.core.management.base import BaseCommand


BASE_DIR = Path(__file__).resolve().parents[3]


class Command(BaseCommand):
    help = "Run Django dashboard and CoAP server together."

    def add_arguments(self, parser):
        parser.add_argument(
            "addrport",
            nargs="?",
            default="0.0.0.0:8000",
            help="Django address and port, for example 0.0.0.0:8000",
        )
        parser.add_argument(
            "--coap-host",
            default="0.0.0.0",
            help="CoAP host to bind, default: 0.0.0.0",
        )
        parser.add_argument(
            "--coap-port",
            default="5683",
            help="CoAP UDP port to bind, default: 5683",
        )

    def handle(self, *args, **options):
        coap_process = None
        django_process = None

        try:
            coap_process = subprocess.Popen(
                [
                    sys.executable,
                    str(BASE_DIR / "coap_server.py"),
                    options["coap_host"],
                    str(options["coap_port"]),
                ],
                cwd=BASE_DIR,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"CoAP server: udp://{options['coap_host']}:{options['coap_port']}"
                )
            )

            django_process = subprocess.Popen(
                [
                    sys.executable,
                    str(BASE_DIR / "manage.py"),
                    "runserver",
                    options["addrport"],
                    "--noreload",
                ],
                cwd=BASE_DIR,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Django dashboard: http://{options['addrport']}")
            )

            django_process.wait()

        except KeyboardInterrupt:
            self.stdout.write("")
            self.stdout.write("Dang tat Django va CoAP...")

        finally:
            for process in (django_process, coap_process):
                if process and process.poll() is None:
                    process.terminate()

            for process in (django_process, coap_process):
                if process:
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
