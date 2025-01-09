import time
from flask import Flask, jsonify, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Ruta post pra generar una busqueda a partir de un titulo que se envia desde el cliente

@app.route('/buscarLibre', methods=['POST'])
def buscarLibre():
    title = request.form.get('title')

    driver = crear_driver()
    datos = {
        'status': 'success',
        'titulo': title,
        'buscaLibre': buscar_libre_libreria(driver, title)
    }
    return jsonify(datos)

@app.route('/buscarNacional', methods=['POST'])
def buscarNacional():
    title = request.form.get('title')

    driver = crear_driver()
    datos = {
        'status': 'success',
        'titulo': title,
        'buscaNacional': buscar_nacional_libreria(driver, title)
    }
    return jsonify(datos)

# funciones que se usarán en las rutas

def crear_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def buscar_nacional_libreria(driver, titulo):
    driver.get('https://www.librerianacional.com/')

    # Encuentre el input con el placeholder "Busca títulos, autores, categorías..." y escriba el titulo
    input_busqueda = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Busca títulos, autores, categorías..."]')
    input_busqueda.send_keys(titulo)
    input_busqueda.send_keys(Keys.ENTER)

    time.sleep(4)

    # # Validar si el section con el ID "noEncontrado" existe
    # # no_encontrado = driver.find_element(By.ID, 'noEncontrado')
    # # if no_encontrado:
    # #     return []

    # # Encuentre todos los div con la clase CSS "vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4"
    libros_encontrados = driver.find_elements(By.CSS_SELECTOR, 'div.vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4')
    # libros_encontrados = driver.find_elements(By.CSS_SELECTOR, 'div.box-producto')
    return libros_encontrados
    # libros = []

    # for libro in libros_encontrados:
    #     libros.append(extraerDatosLibre(libro))
    
    # # Buscar los elementos span que tengan la clase "pagnLink"
    # paginas = driver.find_elements(By.CSS_SELECTOR, 'span.pagnLink')
    
    # if len(paginas):
    #     for i, p in enumerate(paginas):
    #         titulo_modificado = titulo.replace(' ', '+').lower()
    #         url = f"https://www.buscalibre.com.co/libros/search?q={titulo_modificado}&page={i + 2}"
    #         driver.get(url)
    #         time.sleep(2)

    #         libros_encontrados = driver.find_elements(By.CSS_SELECTOR, 'div.box-producto')
    #         for libro in libros_encontrados:
    #             libros.append(extraerDatosLibre(libro))

    # return libros

def buscar_libre_libreria(driver, titulo):
    driver.get('https://www.buscalibre.com.co/')

    # Encuentre el input con name="q" y escriba el titulo
    input_busqueda = driver.find_element(By.NAME, 'q')
    input_busqueda.send_keys(titulo)
    input_busqueda.send_keys(Keys.ENTER)

    time.sleep(2)

    # Validar si el section con el ID "noEncontrado" existe
    # no_encontrado = driver.find_element(By.ID, 'noEncontrado')
    # if no_encontrado:
    #     return []

    # Encuentre todos los div con la clase CSS "div.box-producto"
    libros_encontrados = driver.find_elements(By.CSS_SELECTOR, 'div.box-producto')

    libros = []

    for libro in libros_encontrados:
        libros.append(extraerDatosLibre(libro))
    
    # Buscar los elementos span que tengan la clase "pagnLink"
    paginas = driver.find_elements(By.CSS_SELECTOR, 'span.pagnLink')
    
    if len(paginas):
        for i, p in enumerate(paginas):
            titulo_modificado = titulo.replace(' ', '+').lower()
            url = f"https://www.buscalibre.com.co/libros/search?q={titulo_modificado}&page={i + 2}"
            driver.get(url)
            time.sleep(2)

            libros_encontrados = driver.find_elements(By.CSS_SELECTOR, 'div.box-producto')
            for libro in libros_encontrados:
                libros.append(extraerDatosLibre(libro))

    return libros

def extraerDatosLibre(libro):
    # Extraer el valor del atributo href de la primera etiqueta a
    url_libro = libro.find_element(By.TAG_NAME, 'a').get_attribute('href')
    # Extraer el valor del atributo "src" de la primera etiqueta img y clase " lazyloaded"
    img_url = libro.find_element(By.TAG_NAME, 'img').get_attribute('src')
    # Extraer el valor de este selector CSS "h3.nombre"
    titulo_libro = libro.find_element(By.CSS_SELECTOR, 'h3.nombre').text
    # Extraer el valor de este selector "div.autor"
    autor_libro = libro.find_element(By.CSS_SELECTOR, 'div.autor').text
    # # Extraer el valor del div con clases "autor color-dark-grey metas hide-on-hover"
    otros_datos = libro.find_element(By.CSS_SELECTOR, 'div.autor.color-dark-gray.metas.hide-on-hover').text
    # # Extraer el valor del elemento p con clases "precio-ahora hide-on-hover margin-0 font-size-medium"
    try:
        precio = libro.find_element(By.CSS_SELECTOR, 'p.precio-ahora.hide-on-hover.margin-0.font-size-medium').text
    except:
        precio = -1


    return{
        'url_libro': url_libro,
        'img_url': img_url if img_url else 'https://statics.cdn1.buscalibre.com/no_image/ni9.__RS180x180__.jpg',
        'titulo': titulo_libro,
        'autor': autor_libro,
        'otros_datos': otros_datos,
        'precio': precio,
    }