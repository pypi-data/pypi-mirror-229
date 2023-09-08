import io
import typing
from PyQt5 import QtCore


class UploadWorker(QtCore.QThread):
    def __init__(
        self,
        domain: str,
        resolution: typing.Tuple[int, int],
        auth: typing.Optional[typing.Tuple[str, str]],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._domain = domain
        self._resolution = resolution
        self._auth = auth

    def upload(self, image_data: bytes, filename: str):
        try:
            import requests
            from requests.auth import HTTPDigestAuth
            from PIL import Image

            image = Image.open(io.BytesIO(image_data))
            image.thumbnail(self._resolution)
            buffer = io.BytesIO()
            image.save(buffer, "JPEG", exif=image.getexif())
            buffer.seek(0)

            auth = None
            if self._auth is not None:
                auth = HTTPDigestAuth(*self._auth)

            requests.put(
                self._domain,
                params=dict(filename=filename),
                data=buffer.getvalue(),
                auth=auth,
            )
        except Exception:
            pass
