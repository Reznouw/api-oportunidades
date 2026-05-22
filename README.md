# 🚀 API y Data Pipeline de Oportunidades - Comunidad Renzo Rey

¡Bienvenido al repositorio oficial del **Pipeline de Datos de Oportunidades** de la comunidad Renzo Rey! 

Este proyecto Open Source es un sistema de gestión y distribución de información sobre becas, empleos, concursos, pasantías y programas académicos a nivel global.

## 🎯 Objetivo del Proyecto

El propósito principal es democratizar el acceso a oportunidades de crecimiento profesional y académico. Utilizo una aplicación local en Python (Streamlit) para ingestar, validar y curar la información de diversas fuentes (LinkedIn, Instagram, webs universitarias), la cual se consolida y se distribuye automáticamente como una **API Pública y Gratuita** a través de este repositorio.

## ⚙️ ¿Cómo funciona? (Arquitectura Serverless)

El flujo de datos está diseñado como un pipeline simple, robusto y 100% gratuito sin depender de servidores de pago:

1.  **Ingesta Local:** A través de una app en `Streamlit`, extraigo la información e imágenes de las convocatorias utilizando librerías de scraping (`BeautifulSoup`, `Instaloader`, `yt-dlp`).
2.  **Validación Manual:** Las oportunidades pasan por un filtro de calidad para asegurar que los links sean válidos y la información sea clara.
3.  **Almacenamiento (GitHub como Backend):** Los datos curados se guardan localmente y se sincronizan con este repositorio en formatos estándar (`.json` y `.csv`).
4.  **Distribución Serverless:** GitHub sirve los archivos "crudos" (Raw) funcionando como una API estática en tiempo real.

---

## 🔌 Cómo consumir la API (¡Es gratis!)

Puedes integrar este pipeline de datos en tus propios proyectos, páginas web, bots de Discord, o aplicaciones. Tienes dos formatos disponibles:

### Opción 1: Consumo vía JSON (Ideal para Desarrolladores)
El archivo `oportunidades.json` contiene la estructura completa en formato de arreglo de objetos.
* **Endpoint API:** `https://raw.githubusercontent.com/TU-USUARIO/api-oportunidades/main/oportunidades.json` 

**Ejemplo de uso (Python/Requests):**

    import requests

    url_api = "https://raw.githubusercontent.com/TU-USUARIO/api-oportunidades/main/oportunidades.json"
    respuesta = requests.get(url_api)
    datos = respuesta.json()

    print(f"Hay {len(datos)} oportunidades disponibles.")


### Opción 2: Integración Directa con Google Sheets (No-Code)
Si no sabes programar y quieres ver la tabla en Excel, puedes jalar los datos del archivo `oportunidades.csv` directamente a tu hoja de cálculo.
1. Abre un Google Sheet vacío.
2. Colócate en la celda **A1**.
3. Pega la siguiente fórmula:
   `=IMPORTDATA("https://raw.githubusercontent.com/Reznouw/api-oportunidades/refs/heads/main/oportunidades.csv")`

---

## 🗂️ Estructura de Datos

La API retorna los siguientes campos por cada oportunidad:
* **Categoría**: (Ej. Beca, Internship, Pregrado, Maestría, etc.)
* **Área**: (Ej. STEM, Software / TI, Negocios, Salud, etc.)
* **Proceso**: Estado de la convocatoria.
* **Título de la Oportunidad**
* **Fecha de Publicación**
* **Fecha Límite**
* **País/Región**
* **Link Oficial**: Enlace directo para aplicar.
* **Público Objetivo**
* **Observaciones**: Descripción detallada o notas extraídas.

## 🛠️ Tecnologías Utilizadas

* **Python:** Lenguaje base del pipeline.
* **Streamlit:** Interfaz gráfica para la herramienta local de ingesta.
* **Pandas:** Manejo y limpieza de datos (exportación a CSV).
* **BeautifulSoup4 / Instaloader / yt-dlp:** Motores de extracción de datos y metadatos de redes cerradas y abiertas.
* **GitHub (Git):** Versionamiento y servicio de alojamiento de la API estática.

## 🤝 Contribuciones

Si quieres aportar nuevas fuentes de extracción, mejorar la aplicación de Streamlit, o construir un dashboard utilizando esta API, ¡los Pull Requests son bienvenidos! 

---
*Desarrollado y mantenido para la comunidad por Renzo Rey.*