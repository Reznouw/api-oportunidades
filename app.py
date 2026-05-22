import streamlit as st
import pandas as pd
import json
import os
import subprocess
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import instaloader
import re
import yt_dlp

# --- CONFIGURACIÓN DE CARPETAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "imagenes_oportunidades")
JSON_FILE = os.path.join(BASE_DIR, "oportunidades.json")
CSV_FILE = os.path.join(BASE_DIR, "oportunidades.csv")

os.makedirs(IMAGE_DIR, exist_ok=True)

# --- LISTAS DESPLEGABLES OPTIMIZADAS ---
CATEGORIAS = [
    "Beca", "Internship / Pasantía", "Pregrado", "Maestría", "Doctorado", 
    "Posdoctorado", "Intercambio", "Curso / Bootcamp", "Programa / Escuela de Verano", 
    "Programa Corto", "Fellowship", "Competencia / Hackathon", "Taller", 
    "Mentoría", "Secundaria", "Professional Training", "Evento / Fórum", "Conferencia / Travel Grant",
    "Otro (Escribir)"
]

AREAS = [
    "Todos", "STEM", "Software / TI / CS", "Ciencia de Datos / IA", "Ingeniería", 
    "Biología", "Biomedicina / Medicina", "Salud", "Neurociencias", "Matemáticas", 
    "Física", "Química", "Aeroespacial", "Robótica", "Telecomunicaciones", "Océanos", 
    "Negocios", "Liderazgo", "Inglés", "Otros",
    "Otro (Escribir)"
]

PROCESOS = [
    "Pendiente", "En revisión", "Aceptado", "Denegado", "Abierta (Pública)", "Cerrada"
]

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def guardar_datos(datos):
    # 1. Guardar JSON
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
    
    # 2. Guardar CSV limpio (sin ruta local de imagen) para Google Sheets
    df = pd.DataFrame(datos)
    df_clean = df.drop(columns=["Ruta Imagen Local"], errors="ignore")
    df_clean.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

def descargar_imagen(url_img, headers=None):
    try:
        response = requests.get(url_img, headers=headers, timeout=10)
        if response.status_code == 200:
            nombre = f"img_{int(time.time())}.jpg"
            ruta = os.path.join(IMAGE_DIR, nombre)
            with open(ruta, "wb") as f:
                f.write(response.content)
            return ruta
    except:
        pass
    return ""

def extraer_info_enlace(url):
    titulo, descripcion, ruta_img = "", "", ""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # MÉTODO 1: INSTAGRAM
    if "instagram.com" in url:
        try:
            L = instaloader.Instaloader(quiet=True)
            match = re.search(r'instagram\.com/(?:p|reel)/([^/?#&]+)', url)
            if match:
                post = instaloader.Post.from_shortcode(L.context, match.group(1))
                descripcion = post.caption if post.caption else ""
                titulo = f"Post de Instagram - {post.owner_username}"
                ruta_img = descargar_imagen(post.url)
                if descripcion or ruta_img: return titulo, descripcion, ruta_img
        except: pass

    # MÉTODO 2: OPEN GRAPH (Webs estándar)
    try:
        response = requests.get(url, headers=headers, timeout=7)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            og_title = soup.find("meta", property="og:title")
            titulo_og = og_title["content"] if og_title else (soup.title.string if soup.title else "")
            og_desc = soup.find("meta", property="og:description")
            desc_og = og_desc["content"] if og_desc else ""
            og_img = soup.find("meta", property="og:image")
            ruta_img_og = descargar_imagen(og_img["content"], headers) if og_img else ""

            if titulo_og or desc_og:
                if len(desc_og) > 20: return titulo_og.strip(), desc_og.strip(), ruta_img_og
                titulo, descripcion, ruta_img = titulo_og, desc_og, ruta_img_og
    except: pass

    # MÉTODO 3: FALLBACK YT-DLP
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not titulo: titulo = info.get('title', 'Oportunidad Extraída')
            if not descripcion: descripcion = info.get('description', '')
            if not ruta_img and info.get('thumbnail'): ruta_img = descargar_imagen(info.get('thumbnail'))
    except: pass

    return titulo.strip(), descripcion.strip(), ruta_img

# ---- INTERFAZ DE STREAMLIT ----
st.set_page_config(page_title="Renzo Rey - Oportunidades", layout="wide")
st.title("🚀 Panel de Control de Oportunidades")

# Inicializar variables en sesión para autocompletado
if "titulo_auto" not in st.session_state: st.session_state.titulo_auto = ""
if "desc_auto" not in st.session_state: st.session_state.desc_auto = ""
if "img_auto" not in st.session_state: st.session_state.img_auto = ""
if "url_auto" not in st.session_state: st.session_state.url_auto = ""

# SECCIÓN 1: EXTRACCIÓN OPCIONAL
st.subheader("1. Extracción Automática (Opcional)")
st.info("💡 Si ya tienes los datos a la mano, ignora este paso y llena directamente el formulario.")

col_link, col_btn = st.columns([4, 1])
with col_link:
    url_input = st.text_input("Link para autocompletar:", label_visibility="collapsed", placeholder="Pega un link aquí y presiona extraer...")
with col_btn:
    if st.button("🔍 Extraer Datos"):
        if url_input:
            st.session_state.url_auto = url_input
            with st.spinner("Descargando información..."):
                t, d, i = extraer_info_enlace(url_input)
                st.session_state.titulo_auto = t
                st.session_state.desc_auto = d
                st.session_state.img_auto = i
                if t or d or i: st.success("¡Datos extraídos! Se han llenado abajo.")
                else: st.warning("No se pudo extraer automáticamente. Llena los datos manual.")
        else:
            st.error("Ingresa un link primero.")

if st.session_state.img_auto and os.path.exists(st.session_state.img_auto):
    st.image(st.session_state.img_auto, width=200, caption="Imagen extraída")

# SECCIÓN 2: FORMULARIO PRINCIPAL
st.subheader("2. Datos de la Oportunidad (Llenado Manual / Automático)")

with st.form("formulario_oportunidad", clear_on_submit=True):
    c1, c2 = st.columns(2)
    
    with c1:
        cat_seleccion = st.selectbox("Categoría*", CATEGORIAS)
        cat_otra = st.text_input("Categoría Personalizada (Solo si elegiste 'Otro')", placeholder="Escribe aquí tu nueva categoría")
        
        area_seleccion = st.selectbox("Área*", AREAS)
        area_otra = st.text_input("Área Personalizada (Solo si elegiste 'Otro')", placeholder="Escribe aquí tu nueva área")
        
        proceso = st.selectbox("Proceso*", PROCESOS)
        titulo_oportunidad = st.text_input("Título de la Oportunidad*", value=st.session_state.titulo_auto)

    with c2:
        público_objetivo = st.text_input("Público Objetivo*")
        fecha_publicacion = st.date_input("Fecha de Publicación", value=datetime.today())
        fecha_limite = st.date_input("Fecha Límite")
        pais_region = st.text_input("País/Región*")
        link_oficial = st.text_input("Link Oficial*", value=st.session_state.url_auto)
        
    observaciones = st.text_area("Observaciones / Detalles", value=st.session_state.desc_auto, height=130)

    submit_button = st.form_submit_button("💾 Guardar y Generar CSV")

# LÓGICA DE GUARDADO
if submit_button:
    # Lógica para determinar si se usa la lista o el texto manual
    categoria_final = cat_otra if (cat_seleccion == "Otro (Escribir)" and cat_otra) else cat_seleccion
    area_final = area_otra if (area_seleccion == "Otro (Escribir)" and area_otra) else area_seleccion

    if not titulo_oportunidad or not link_oficial or not pais_region or not público_objetivo or categoria_final == "Otro (Escribir)" or area_final == "Otro (Escribir)":
        st.error("Por favor, completa los campos obligatorios (*) o las opciones personalizadas de 'Otro'.")
    else:
        db = cargar_datos()
        nueva_oportunidad = {
            "Categoría": categoria_final,
            "Área": area_final,
            "Proceso": proceso,
            "Título de la Oportunidad": titulo_oportunidad,
            "Fecha de Publicación": str(fecha_publicacion),
            "Fecha límite": str(fecha_limite),
            "País/Región": pais_region,
            "Link Oficial": link_oficial,
            "Público Objetivo": público_objetivo,
            "Observaciones": observaciones,
            "Ruta Imagen Local": st.session_state.img_auto
        }
        db.append(nueva_oportunidad)
        guardar_datos(db)
        
        st.success(f"¡Oportunidad guardada con éxito! Archivo CSV actualizado.")
        
        # Limpiar estados tras guardar
        st.session_state.titulo_auto = ""
        st.session_state.desc_auto = ""
        st.session_state.img_auto = ""
        st.session_state.url_auto = ""
        
        st.subheader("📢 Plantilla para WhatsApp:")
        st.code(f"""*¡NUEVA OPORTUNIDAD!* 🚀
📌 *{titulo_oportunidad}* ({categoria_final})
💼 *Área:* {area_final}
🌍 *Ubicación:* {pais_region}
🎯 *Para:* {público_objetivo}
⏳ *Fecha límite:* {fecha_limite}

🔗 *Aplica aquí:* {link_oficial}""", language="markdown")

# SECCIÓN 3: VISTA DE BASE DE DATOS
st.subheader("📊 Base de Datos Local")
actuales = cargar_datos()
if actuales:
    st.dataframe(pd.DataFrame(actuales).drop(columns=["Ruta Imagen Local"], errors="ignore"))

# SECCIÓN 4: PANEL DE CONTROL LATERAL (SIDEBAR PARA GITHUB)
with st.sidebar:
    st.header("⚙️ Sincronización a la Nube")
    st.write("Presiona este botón para subir los últimos cambios a tu repositorio público de GitHub y actualizar tu Google Sheets.")
    
    if st.button("🔄 Subir a GitHub (Git Push)"):
        with st.spinner("Empaquetando y subiendo archivos..."):
            try:
                # Ejecuta los comandos de consola desde Python
                subprocess.run(["git", "add", "."], check=True, capture_output=True)
                
                # El commit puede fallar intencionalmente si no hay cambios, por eso no usamos check=True aquí
                subprocess.run(["git", "commit", "-m", f"Actualización automática - {datetime.now().strftime('%Y-%m-%d %H:%M')}"], capture_output=True)
                
                # Push a GitHub
                proceso_push = subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True)
                
                st.success("¡Subido con éxito! Tu Google Sheets se actualizará pronto.")
            except subprocess.CalledProcessError as e:
                st.error(f"Error al subir: {e.stderr}")
            except Exception as e:
                st.error(f"Error inesperado: {str(e)}")