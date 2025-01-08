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

@app.route('/buscar', methods=['POST'])
def buscar():
    title = request.form.get('title')

    driver = crear_driver()
    datos = {
        'status': 'success',
        'titulo': title,
        'buscaLibre': buscar_libre_libreria(driver, title)
    }
    return jsonify(datos)

# funciones que se usarán en las rutas

def crear_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def buscar_libre_libreria(driver, titulo):
    driver.get('https://www.buscalibre.com.co/')

    # Encuentre el input con name="q" y escriba el titulo
    input_busqueda = driver.find_element(By.NAME, 'q')
    input_busqueda.send_keys(titulo)
    input_busqueda.send_keys(Keys.ENTER)

    time.sleep(3)

    # Validar si el section con el ID "noEncontrado" existe
    no_encontrado = driver.find_element(By.ID, 'noEncontrado')
    if no_encontrado:
        return []

    # Encuentre todos los div con la clase CSS "div.box-producto"
    divs = driver.find_elements(By.CSS_SELECTOR, 'div.box-producto')

    libros = []

    for div in divs:
        # Extraer el valor del atributo "src" de la primera etiqueta img y clase " lazyloaded"
        img_url = div.find_element(By.TAG_NAME, 'img').get_attribute('src')
        # Extraer el valor de este selector CSS "h3.nombre"
        titulo_libro = div.find_element(By.CSS_SELECTOR, 'h3.nombre').text
        # Extraer el valor de este selector "div.autor"
        autor_libro = div.find_element(By.CSS_SELECTOR, 'div.autor').text
        # # Extraer el valor del div con clases "autor color-dark-grey metas hide-on-hover"
        otros_datos = div.find_element(By.CSS_SELECTOR, 'div.autor.color-dark-gray.metas.hide-on-hover').text
        # # Extraer el valor del elemento p con clases "precio-ahora hide-on-hover margin-0 font-size-medium"
        precio = div.find_element(By.CSS_SELECTOR, 'p.precio-ahora.hide-on-hover.margin-0.font-size-medium').text


        libros.append({
            'img_url': img_url,
            'titulo': titulo_libro,
            'autor': autor_libro,
            'otros_datos': otros_datos,
            'precio': precio,
        })

    return libros