from decimal import Decimal
import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from product.models import Product


class Command(BaseCommand):
    help = "Import products from a CSV. Columns: name,description,price,stock"

    def add_arguments(self, parser):
        parser.add_argument("csvfile", type=str, help="Path to CSV file to import")
        parser.add_argument(
            "--dry-run", action="store_true", help="Parse file but do not save changes"
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing products (matched by name) instead of creating duplicates",
        )

    def handle(self, *args, **options):
        path = options["csvfile"]
        dry_run = options["dry_run"]
        update = options["update"]

        try:
            with open(path, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)
        except Exception as exc:
            raise CommandError(f"Failed to read CSV: {exc}")

        if not rows:
            self.stdout.write("No rows found in CSV.")
            return

        created = updated = skipped = 0

        with transaction.atomic():
            for row in rows:
                name = (row.get("name") or row.get("Name") or "").strip()
                if not name:
                    skipped += 1
                    continue

                description = row.get("description") or row.get("Description") or ""
                price_raw = (row.get("price") or row.get("Price") or "0").strip()
                stock_raw = (row.get("stock") or row.get("Stock") or "0").strip()

                try:
                    price = Decimal(price_raw)
                except Exception:
                    price = Decimal("0.00")

                try:
                    stock = int(float(stock_raw))
                except Exception:
                    stock = 0

                existing = Product.objects.filter(name=name).first()
                if existing:
                    if update:
                        existing.description = description
                        existing.price = price
                        existing.stock = stock
                        if not dry_run:
                            existing.save()
                        updated += 1
                    else:
                        skipped += 1
                else:
                    if not dry_run:
                        Product.objects.create(
                            name=name, description=description, price=price, stock=stock
                        )
                    created += 1

        suffix = " (dry run)" if dry_run else ""
        self.stdout.write(f"Imported: created={created}, updated={updated}, skipped={skipped}{suffix}")