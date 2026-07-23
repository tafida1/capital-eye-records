import os
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management import call_command


def create_system_backup():
    backup_dir = Path(settings.BACKUP_ROOT)
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"database_backup_{timestamp}.json"
    zip_filename = f"capital_eye_backup_{timestamp}.zip"

    json_path = backup_dir / json_filename
    zip_path = backup_dir / zip_filename

    with open(json_path, "w", encoding="utf-8") as f:
        call_command(
            "dumpdata",
            "--natural-foreign",
            "--natural-primary",
            "--indent",
            "2",
            stdout=f,
        )

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as backup_zip:
        backup_zip.write(json_path, arcname=json_filename)

        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists():
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    file_path = Path(root) / file
                    arcname = Path("media") / file_path.relative_to(media_root)
                    backup_zip.write(file_path, arcname=arcname)

    json_path.unlink(missing_ok=True)

    return zip_path