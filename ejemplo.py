import spacy
import requests
import json
from dotenv import load_dotenv
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from spellchecker import SpellChecker
import re

load_dotenv()

# Configuración de spaCy
nlp = spacy.load("es_core_news_sm")

# Configuración de la cuenta de servicio
CREDENTIALS_PATH = "credencial.json"
SCOPES = ["https://www.googleapis.com/auth/generative-language"]
API_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'

PALABRAS_PROHIBIDAS = [
    r"ch[i1!][nñ][g9q][a4@]",
    r"tu m[a4@]dr[e3]",
    r"p[vb][t7][o0*@]",
    r"m[i1][e3]r[dcl][a4@]",
    r"m[a4@]lp[a4@]r[i1]d[o0]",
    r"p[e3]nd[e3]j[o0]",
    r"c[o0]j[o0]n[e3]s?",
    r"b[o0]l[a4@]s",
    r"v[a4@]g[o0]n[o0]",
    r"f[u0]t[a4@]n[o0]s?",
    r"put[o0]",
    r"mierd[a4@]",
    r"v[e3]rg[a4@]",
    r"m[a4@]ld[i1][t7][a4@]",
    r"h[i1]j[o0][dcl][a4@]",
    r"p[e3]r[r4]a",
    r"c[a4@]b[r3][o0]n[e3]s?",
    r"m[a4@]l[nñ][dcl][o0][s5]",
    r"t[a4@]r[a4@][dcl][o0][s5]",
    r"v[a4@][c9][o0][nñ][a4@]",
    r"h[o0]l[e3]r[a4@][s5]",
    r"p[a4@][t7]u[e3][r4][dcl][o0][s5]",
    r"h[o0]rr[a4@][dcl][o0][s5]",
]

# Diccionario de nombres y apellidos comunes
NOMBRES_APELLIDOS = {
    "veronica", "velasco", "jimenez", "maria", "jose", "lopez", "gonzalez", "perez", "martinez"
}

# Diccionario de combinaciones de palabras potenciales de albures
ALBORES_POTENCIALES = [
    "maria rosame elano",
    "juan cano gallego",
    "paco peña",
    "rosa melano",
    "luis pino",
    "paulino goloso",
    "ana gonzalez perez",
    "susana alvarez",
    "salvador navarro",
    "mario hermanos",
    "rosa mina",
    "diana caza",
    "alba raba",
    "juan sin pena",
    "alberto rivas",
    "carlos pinto",
    "isabel golosa",
    "elena rivas",
    "tomas hinchas",
    "fernando perez",
    "luis escroto",
    "manuel jara",
    "lina atencion",
    "sandra pasion",
    "natalia ganas",
    "miguel loma",
    "alejandro casas",
    "felipe pilar",
    "manuel salado",
    "juan la buena",
    "pablo amores",
    "cesar flores",
    "jose pinocho",
    "maria dolores",
    "raul pena",
    "jaime mas",
    "alberto roca",
    "carlos pino",
    "pablo cerda",
    "adriana luna",
    "lucia mesa",
    "manuel calderon",
    "julian espada",
    "olga fraga"
]

def filtrar_groserias(texto):
    for palabra in PALABRAS_PROHIBIDAS:
        if re.search(palabra, texto.lower()):
            return "Lo siento, no puedo procesar mensajes que incluyan palabras inapropiadas."
    return texto

def filtrar_albures(texto):
    for albur in ALBORES_POTENCIALES:
        if albur in texto.lower():
            return "Lo siento, no puedo procesar mensajes que incluyan combinaciones de palabras inapropiadas."
    return texto

def corregir_ortografia(texto):
    spell = SpellChecker(language='es')
    palabras = texto.split()
    palabras_corregidas = []
    
    for palabra in palabras:
        palabra_lower = palabra.lower()
        if palabra.isupper() or any(char.isdigit() for char in palabra) or palabra_lower in NOMBRES_APELLIDOS:
            palabras_corregidas.append(palabra)  # No corregir nombres o apellidos conocidos
        else:
            correccion = spell.correction(palabra_lower)
            palabras_corregidas.append(correccion.capitalize() if correccion else palabra)

    return ' '.join(palabras_corregidas)

# Función de lematización
def lematizar_texto(texto):
    doc = nlp(texto)
    return ' '.join([token.lemma_ for token in doc])

# Función de tokenización
def tokenizar_texto(texto):
    doc = nlp(texto)
    return [token.text for token in doc]

def procesar_mensaje(mensaje):
    # Filtrar groserías y albures
    mensaje_usuario_filtrado = filtrar_groserias(mensaje)
    if mensaje_usuario_filtrado.startswith("Lo siento"):
        return mensaje_usuario_filtrado
    
    mensaje_usuario_filtrado = filtrar_albures(mensaje_usuario_filtrado)
    if mensaje_usuario_filtrado.startswith("Lo siento"):
        return mensaje_usuario_filtrado

    mensaje_usuario_corregido = corregir_ortografia(mensaje_usuario_filtrado)
    mensaje_lema = lematizar_texto(mensaje_usuario_corregido)
    tokens = tokenizar_texto(mensaje_lema)

    return f"Mensaje procesado (Lematización): {mensaje_lema}\nTokens: {tokens}"

# Ejecutar el procesamiento de mensajes
if __name__ == "__main__":
    while True:
        mensaje = input("Ingresa un mensaje (o escribe 'salir' para terminar): ")
        if mensaje.lower() in ["salir", "exit"]:
            print("Hasta luego!")
            break
        respuesta = procesar_mensaje(mensaje)
        print(respuesta)
