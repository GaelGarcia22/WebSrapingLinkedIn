# WebScraping de Vacantes en LinkedIn

Este proyecto realiza la extracción automatizada de vacantes laborales publicadas en LinkedIn por empresas del sector energético, tecnológico y de análisis de datos. Utiliza Selenium, Python y pandas para recopilar, filtrar y guardar los resultados en archivos .xlsx.

## Características

- Automatiza el inicio de sesión en LinkedIn.
- Busca empresas previamente definidas.
- Aplica filtros de experiencia ("Sin experiencia", "Algo de responsabilidad").
- Limpia y estructura la información de vacantes: título, empresa, ubicación, estado y enlace directo.
- Guarda la información en un archivo Excel.
- Detecta vacantes nuevas con respecto a ejecuciones anteriores.
- Identifica vacantes relevantes para perfiles de datos y energía.

## Tecnologías usadas

- Python 3.11
- Selenium
- pandas
- dotenv
- ChromeDriver
- VS Code

## Estructura del proyecto

```
Linkedin/
├── WebScraping.py
├── Listas_empresas.py
├── .gitignore
├── .env
├── Vacantes_LinkedIn.xlsx
├── Nuevos_Trabajos_LinkedIn_YYYY-MM-DD_HH-MM-SS.xlsx
└── Vacantes_Relevantes_LinkedIn_YYYY-MM-DD_HH-MM-SS.xlsx
```

## Variables de entorno

Crea un archivo `.env` con tus credenciales de LinkedIn:

```
LINKEDIN_USER=tu_correo@ejemplo.com
LINKEDIN_PASS=tu_contraseña_segura
```

Este archivo no se sube al repositorio. Está listado en `.gitignore`.

## Cómo ejecutar

1. Clona el repositorio:

```
git clone https://github.com/tu_usuario/linkedin-webscraper.git
cd linkedin-webscraper
```

2. Crea un entorno virtual y actívalo:

```
python -m venv .venv
.venv\Scripts\activate
```

3. Instala dependencias:

```
pip install -r requirements.txt
```

4. Crea tu `.env` y corre el script:

```
python WebScraping.py
```

## Autor

Desarrollado por Leonardo Gael, apasionado por la energía, los datos y la automatización.
