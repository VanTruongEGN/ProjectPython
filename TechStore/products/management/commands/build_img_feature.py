# products/management/commands/build_img_feature.py

from django.core.management.base import BaseCommand
from products.models import ProductImage
import os
import pickle

from image_search.yolo.image_feature import extract_feature


class Command(BaseCommand):
    help = "Build image feature for all product images"

    def handle(self, *args, **options):
        qs = ProductImage.objects.filter(
            image__isnull=False
        ).select_related("product")

        self.stdout.write(f"Found {qs.count()} images")

        ok = 0
        fail = 0

        for img in qs:
            try:
                path = img.image.path

                if not os.path.exists(path):
                    self.stdout.write(
                        self.style.WARNING(f"Missing file: {path}")
                    )
                    continue

                # 1️⃣ Extract feature (numpy array)
                feature = extract_feature(path)

                # 2️⃣ Convert → bytes
                feature_bytes = pickle.dumps(feature)

                # 3️⃣ Save vào ProductImage (QUAN TRỌNG)
                img.image_feature = feature_bytes
                img.save(update_fields=["image_feature"])

                ok += 1
                self.stdout.write(
                    self.style.SUCCESS(f"OK: {img.id}")
                )

            except Exception as e:
                fail += 1
                self.stdout.write(
                    self.style.ERROR(f"ERROR {img.id}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Success={ok}, Failed={fail}"
            )
        )
