from PIL import Image
import requests
from io import BytesIO

def __download(url, path):
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

def audio(url, path):
    __download(url, path)

def video(url, path):
    """
    Descarga un archivo multimedia desde la URL proporcionada y lo guarda con el nombre especificado en la ubicación especificada.
    
    Args:
        url (str): La URL del archivo multimedia.
        filename (str): El nombre de archivo para guardar.
        output_path (str): La ruta de salida donde se guardará el archivo. Por defecto, es el directorio actual.
    """
    extension = url.split('.')[-1]

    if extension == 'm3u8':
        raise Exception('Cant download m3u8 video.')
    else:
        if path.endswith(extension) == False:
            path += '.' + extension
            
        __download(url, path)

def image(url, path):
    __download(url, path)

def get_image_dimensions(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        image_data = BytesIO(response.content)
        image = Image.open(image_data)
        width, height = image.size
        return width, height
    else:
        return None, None