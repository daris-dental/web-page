# apps/common/imgbb_storage.py
import base64
import requests
from django.core.files.storage import Storage
from django.conf import settings
from django.utils.deconstruct import deconstructible


@deconstructible
class ImgBBStorage(Storage):
    """
    Backend de almacenamiento que sube imágenes a ImgBB y devuelve la URL pública.
    Compatible con el campo ImageField de Django.
    """

    def __init__(self, api_key=None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or settings.IMGBB_API_KEY
        self.api_url = "https://api.imgbb.com/1/upload"

    def _save(self, name, content):
        """Sube el archivo a ImgBB y devuelve la URL de la imagen."""
        content.seek(0)
        image_b64 = base64.b64encode(content.read()).decode('utf-8')

        payload = {
            "key": self.api_key,
            "image": image_b64,
            "name": name.split('/')[-1],  # nombre del archivo sin ruta
        }

        response = requests.post(self.api_url, data=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        # ImgBB devuelve una estructura con 'data' -> 'url'
        url = data.get('data', {}).get('url')
        if not url:
            raise Exception(f"ImgBB no devolvió URL: {data}")

        return url  # Django guardará esta URL en el campo

    def _open(self, name, mode='rb'):
        """Abre la imagen remota (necesario para el campo ImageField)."""
        import requests
        response = requests.get(name, stream=True)
        response.raise_for_status()
        return response.raw

    def exists(self, name):
        """Indica si el archivo ya existe (siempre False, ImgBB genera nombre único)."""
        return False

    def url(self, name):
        """Devuelve la URL de la imagen."""
        return name

    def delete(self, name):
        """ImgBB no expone una API de borrado directo; se omite."""
        pass