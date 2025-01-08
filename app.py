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
    datos = {
        'title': title
    }
    return jsonify(datos)

# funciones que se usarán en las rutas

def crear_driver():
    chrome_options = webdriver.ChromeOptions()
    return chrome_options