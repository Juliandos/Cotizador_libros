import math
import re
import time
from flask import Flask, jsonify, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Ruta post pra generar una busqueda a partir de un titulo que se envia desde el cliente

# Petición realizada a Librería Libre
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

# Petición realizada a Librería Nacional
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

# Petición realizada a Librería Lerner
@app.route('/buscarLerner', methods=['POST'])
def buscarLerner():
    title = request.form.get('title')

    driver = crear_driver()
    datos = {
        'status': 'success',
        'titulo': title,
        'buscaLerner': buscar_lerner_libreria(driver, title)
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

    time.sleep(3)
    
    libros = []
    # Ciclo while para verificar continuamente la presencia del botón
    while True:
        try:
            # Intentar encontrar el botón 'Mostrar más'
            mostrar_mas = driver.find_element(By.CSS_SELECTOR, "a.vtex-button[rel='next']")
            mostrar_mas.click()
            time.sleep(3)
        except:
            libros_encontrados = driver.find_elements(By.CSS_SELECTOR, 'section.vtex-product-summary-2-x-container.vtex-product-summary-2-x-container--cardsLibros.vtex-product-summary-2-x-containerNormal.vtex-product-summary-2-x-containerNormal--cardsLibros.overflow-hidden.br3.h-100.w-100.flex.flex-column.justify-between.center.tc')

            for libro in libros_encontrados:
                libros.append(extraerDatosNacional(libro))
            break 

    return libros

def buscar_libre_libreria(driver, titulo):
    driver.get('https://www.buscalibre.com.co/')

    # Encuentre el input con name="q" y escriba el titulo
    input_busqueda = driver.find_element(By.NAME, 'q')
    input_busqueda.send_keys(titulo)
    input_busqueda.send_keys(Keys.ENTER)

    time.sleep(2)

    # Encontrar el div con estas clases "cantidadProductos"
    cantidad_libros = driver.find_element(By.CSS_SELECTOR, 'div.cantidadProductos h2').text
    numero_paginas = int(re.search(r'\d+', cantidad_libros).group())/50
    if numero_paginas > int(numero_paginas):
        numero_paginas = math.ceil(numero_paginas)

    libros_encontrados = driver.find_elements(By.CSS_SELECTOR, 'div.box-producto')

    libros = []

    for libro in libros_encontrados:
        libros.append(extraerDatosLibre(libro))
    
    for i in range(0, numero_paginas - 1):
        titulo_modificado = titulo.replace(' ', '+').lower()
        url = f"https://www.buscalibre.com.co/libros/search?q={titulo_modificado}&page={i + 2}"
        driver.get(url)
        time.sleep(2)

        libros_encontrados = driver.find_elements(By.CSS_SELECTOR, 'div.box-producto')
        for libro in libros_encontrados:
            libros.append(extraerDatosLibre(libro))

    return libros

def buscar_lerner_libreria(driver, titulo):
    driver.get('https://www.librerialerner.com.co/')

    # Encuentre el input con placeholder "Buscar libros"
    input_busqueda = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Buscar libros"]')
    input_busqueda.send_keys(titulo)
    input_busqueda.send_keys(Keys.ENTER)

    time.sleep(10)

    libros = []
    # Ciclo while para verificar continuamente la presencia del botón Mostrar Más
    while True:
        try:
            mostrar_mas = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Mostrar más"))
            )
            mostrar_mas.click()
        except:
            time.sleep(10)
            try:
                # Encuentra múltiples elementos
                elementos = driver.find_elements(By.CSS_SELECTOR, "section.vtex-product-summary-2-x-container.vtex-product-summary-2-x-containerNormal")
                
                if elementos:
                    for idx, elemento in enumerate(elementos):
                        # Obtén el texto del elemento
                        texto = elemento.text
                        
                        enlace = elemento.find_element(By.CSS_SELECTOR, 'a').get_attribute('href') if elemento.find_elements(By.CSS_SELECTOR, 'a') else None

                        src_imagen = obtener_imagen(elemento)
                        
                        partes = texto.split('\n')
                        if len(partes) >= 3:
                            autor = partes[2]
                            precio = partes[0] 
                            titulo = partes[1]
                            if autor == 'Agotado':
                                precio = autor
                                autor = partes[0]
                            
                            libros.append({
                                'url_libro': enlace,
                                'img_url': src_imagen,
                                'titulo': titulo,
                                'autor': autor,
                                'precio': precio,
                                })
                else:
                    print("No se encontraron elementos.")
            except Exception as e:
                print("Error al procesar los elementos:", e)
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

def extraerDatosNacional(libro):
    # Extraer el valor del atributo href de la primera etiqueta a
    url_libro = libro.find_element(By.TAG_NAME, 'a').get_attribute('href')
    # Extraer el valor del atributo "src" de la primera etiqueta img y clase " lazyloaded"
    img_url = libro.find_element(By.TAG_NAME, 'img').get_attribute('src')
    # Extraer el valor de este selector CSS "h3.nombre"
    titulo_libro = libro.find_element(By.CSS_SELECTOR, "h3.vtex-product-summary-2-x-productNameContainer span.vtex-product-summary-2-x-productBrand").text
    # Extraer el valor de este selector "div.autor"
    autor_libro = libro.find_element(By.CSS_SELECTOR, 'span.vtex-product-specification-badges-0-x-badgeText.vtex-product-specification-badges-0-x-badgeText--autorCardLibros').text
    # Extraer el valor del elemento p con clases "precio-ahora hide-on-hover margin-0 font-size-medium"
    try:
        # Encuentra los elementos que componen el precio
        currency_code = libro.find_element(By.CSS_SELECTOR, "span.vtex-product-price-1-x-currencyCode").text
        currency_integer = libro.find_element(By.CSS_SELECTOR, "span.vtex-product-price-1-x-currencyInteger").text
        currency_group = libro.find_element(By.CSS_SELECTOR, "span.vtex-product-price-1-x-currencyGroup").text
        currency_literal = libro.find_element(By.CSS_SELECTOR, "span.vtex-product-price-1-x-currencyLiteral").text

        # Verificar si el espacio está vacío y reemplazarlo por "00"
        if currency_literal.strip() == "":
            currency_literal = "00"
        # Componer el precio completo
        precio = f"{currency_code}{currency_integer}{currency_group}{currency_literal}"
    except:
        precio = -1


    return {
        'url_libro': url_libro,
        'img_url': img_url if img_url else 'https://statics.cdn1.buscalibre.com/no_image/ni9.__RS180x180__.jpg',
        'titulo': titulo_libro,
        'autor': autor_libro,
        'precio': precio,
    }

def obtener_imagen(elemento):
    try:
        # Encuentra la imagen dentro del elemento
        imagen = elemento.find_element(By.CSS_SELECTOR, 'img.vtex-product-summary-2-x-imageNormal')
        # Obtener la URL de la imagen
        src_imagen = imagen.get_attribute('src')
        return src_imagen
    except Exception as e:
        print(f"Error al obtener la imagen: {e}")
        return None