from pathlib import Path

from django.conf import settings


class FileStore:
    def __init__(self):
        self.root = Path(settings.FILES_BASE_PATH).absolute()

    def path(self, relative_path: str) -> Path:
        path = Path(relative_path)

        if path.is_absolute() or '..' in path.parts:
            raise ValueError('File paths must be relative and must not traverse')

        return self.root / path

    def relative(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            raise ValueError('File path is not below FILES_BASE_PATH') from None



