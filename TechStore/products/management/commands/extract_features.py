from django.core.management.base import BaseCommand
from products.models import ProductImage
import os
import pickle
from image_search.yolo.image_feature import extract_feature


class Command(BaseCommand):
    help = "Extract image features for product images"

    def handle(self, *args, **kwargs):
        qs = ProductImage.objects.filter(
            image__isnull=False
        ).select_related("product")

        self.stdout.write(f"Found {qs.count()} images")

        success = 0
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

                # 2️⃣ Pickle → bytes
                img.image_feature = pickle.dumps(feature)

                # 3️⃣ Save vào ProductImage ✅
                img.save(update_fields=["image_feature"])

                success += 1
                self.stdout.write(
                    self.style.SUCCESS(f"OK image {img.id} of {img.product.id}")
                )

            except Exception as e:
                fail += 1
                self.stdout.write(
                    self.style.ERROR(f"ERROR image {img.id}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Success: {success}, Failed: {fail}"
            )
        )
