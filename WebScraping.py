import os
import re
import time
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException , StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import pandas as pd
import glob
from dotenv import load_dotenv
from Listas_empresas import empresas, PalabrasClave_Datos, PalabrasClave_Energía, keywords_data, keywords_Energy,empresas_pequeñas, empresas_sin_filtros

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver(download_path):
    """Configura el driver de Chrome para descargas automatizadas."""
    prefs = {
        'download.default_directory': download_path,
        'directory_upgrade': True,
        'safebrowsing.enabled': False,
        'credentials_enable_service': False,
        'profile.password_manager_enabled': False,
        'autofill.profile_enabled': False,
        'autofill.credit_card_enabled': False,
        'autofill.address_enabled': False
    }
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('prefs', prefs)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-password-generation')
    options.add_argument('--disable-automatic-password-saving')
    options.add_argument('--disable-features=AutofillServerCommunication')
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        logging.exception("Error al configurar el driver")
        return None

def start_driver_and_login(driver, url,username, password):
    """Carga la página y espera que el elemento principal esté presente."""
    driver.get(url)
    try:
        #Esperar a que aparezca el campo de usuario
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="username"]'))
        )
        logging.info("La página ha cargado correctamente.")

        email_input  = driver.find_element(By.XPATH, '//*[@id="username"]')
        password_input = driver.find_element(By.XPATH, '//*[@id="password"]')

        email_input.clear()
        email_input.send_keys(username)
        logging.info("Email ingresado...")
        time.sleep(0.5)

        password_input.clear()
        password_input.send_keys(password)
        logging.info("Password Ingresada...")
        time.sleep(0.5)

        driver.find_element(By.XPATH, '//button[contains(text(), "Iniciar sesión")]').click()
        logging.info("Inicio de sesión...")
        time.sleep(0.5)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="global-nav-typeahead"]/input')))
        logging.info("Inicio de sesión exitoso.")

    except TimeoutException:
        logging.error("Tiempo de espera agotado al cargar la página.")
    
    return driver

def buscar_empresa(driver, nombre_empresa):
    # Espera la barra de búsqueda global
        barra_busqueda = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH,  '//*[@id="global-nav-typeahead"]/input'))
        )

        # Insertar el texto usando JavaScript
        barra_busqueda.clear()
        barra_busqueda.send_keys(nombre_empresa)
        # Presionar Enter manualmente
        barra_busqueda.send_keys(Keys.RETURN)

        logging.info(f"Búsqueda de empresa '{nombre_empresa}'.")

        time.sleep(2)
        
        botones = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, '//button[contains(normalize-space(.), "Empleos")]'))
        )
        
        if botones:
            botones[0].click()
            logging.info("Botón 'Empleos' encontrado y clickeado.")
        else:
            logging.warning("No se encontraron botones 'Empleos'.")
        time.sleep(2)

def Filtros(driver):
    time.sleep(1)
    WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Mostrar todos los filtros. Al hacer clic en este botón, se muestran todas las opciones de filtros disponibles."]')))
    todos_los_filtros= driver.find_element(By.XPATH, '//button[@aria-label="Mostrar todos los filtros. Al hacer clic en este botón, se muestran todas las opciones de filtros disponibles."]')
    todos_los_filtros.click()
    time.sleep(1)


    WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, '//label[@for="advanced-filter-experience-2"]')))
    filtro_Sin_Experiencia = driver.find_element(By.XPATH, '//label[@for="advanced-filter-experience-2"]')
    filtro_Sin_Experiencia.click()
    time.sleep(1)

    WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, '//label[@for="advanced-filter-experience-3"]')))
    filtro_Algo_De_Responsabilidad=driver.find_element(By.XPATH, '//label[@for="advanced-filter-experience-3"]')
    filtro_Algo_De_Responsabilidad.click()
    time.sleep(1)
    
    try:
        boton = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test-reusables-filters-modal-show-results-button="true"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
        time.sleep(0.5)
        boton.click()
        logging.info("Click exitoso en 'Mostrar resultados'.")

    except StaleElementReferenceException:
        logging.warning("Elemento obsoleto. Reintentando...")
        try:
            boton = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test-reusables-filters-modal-show-results-button="true"]'))
            )
            driver.execute_script("arguments[0].click();", boton)
            logging.info("Click exitoso tras recapturar el botón.")
        except Exception as e:
            logging.error("Fallo definitivo al hacer click en 'Mostrar resultados'.")
            logging.exception(e)

def extraer_informacion_vacante(driver):

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "job-card-container")]'))
    )

    vacantes = driver.find_elements(By.XPATH, '//div[contains(@class, "job-card-container")]')

    datos= []
    
    for vacante in vacantes:
        try:
            titulo = vacante.find_element(By.XPATH, './/a[contains(@class,"job-card-container__link")]//strong').text.strip()
        except:
            titulo = ""

        try:
            empresa = vacante.find_element(By.XPATH, './/div[contains(@class,"artdeco-entity-lockup__subtitle")]//span').text.strip()
        except:
            empresa = ""

        try:
            ubicacion = vacante.find_element(By.XPATH, './/ul[contains(@class,"job-card-container__metadata-wrapper")]/li/span').text.strip()
        except:
            ubicacion = ""

        try:
            link = vacante.find_element(By.XPATH, './/a[contains(@class,"job-card-container__link")]').get_attribute('href')
            if link.startswith('/'):
                link = 'https://www.linkedin.com' + link
        except:
            link = ""

        try:
            estado = vacante.find_element(By.XPATH, './/li[contains(@class, "job-card-container__footer-job-state")]').text.strip()
        except:
            estado = ""

        datos.append ({
            'Título': titulo,
            'Empresa': empresa,
            'Ubicación': ubicacion,
            'Link': link,
            'Estado': estado
        })
        
    return datos

def empresa_sin_vacantes(driver,empresa):
    try:
        # Detectar el mensaje de "No se han encontrado empleos para esta búsqueda"
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "jobs-search-no-results-banner")]')
            )
        )
        logging.warning(f"La empresa {empresa} no tiene vacantes abiertas.")
        return True
    except:
        return False
    
def back(driver,n):
    for _ in range(n):
        driver.back()

def to_excel(archivo_existente,fecha_hoy,archivo_nuevos):
# Nombre del archivo principal

    # 1. Cargar archivo anterior si existe
    if os.path.exists(archivo_existente):
        df_anterior = pd.read_excel(archivo_existente)
        titulos_anteriores = set(df_anterior["Título"].dropna().str.lower().str.strip())
    else:
        df_anterior = pd.DataFrame()
        titulos_anteriores = set()

    # 2. Crear nuevo DataFrame limpio
    df_vacantes = pd.DataFrame(df)
    df_vacantes = df_vacantes.dropna(subset=["Título"])
    df_vacantes = df_vacantes[df_vacantes["Título"].str.strip() != ""]
    df_vacantes = df_vacantes[df_vacantes["Empresa"].str.lower().str.strip() == df_vacantes["EmpresaBuscada"].str.lower().str.strip()]


    # 3. Detectar nuevas vacantes
    df_nuevas = df_vacantes[~df_vacantes["Título"].str.lower().str.strip().isin(titulos_anteriores)]

    # 4. Informar nuevas vacantes
    if not df_nuevas.empty:
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print(f" Se encontraron {len(df_nuevas)} vacantes nuevas:")
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        for i, titulo in enumerate(df_nuevas['Título'], 1):
            print(f"{i}. {titulo}")

        # 5. Guardar archivo de nuevas vacantes
        df_nuevas.to_excel(archivo_nuevos, index=False)
        logging.info(f"Nuevas vacantes guardadas en: {archivo_nuevos}")
    else:
        print("No se encontraron vacantes nuevas.")

    # 6. Eliminar archivos viejos si deseas (excepto el nuevo que acabas de guardar)
    for archivo in glob.glob("Vacantes*.xlsx"):
        if archivo != archivo_existente:
            try:
                os.remove(archivo)
                logging.info(f"Eliminado: {archivo}")
            except Exception as e:
                logging.warning(f"Error al eliminar {archivo}: {e}")

    # 7. Guardar el archivo actualizado
    df_vacantes.to_excel(archivo_existente, index=False)
    logging.info(f"Archivo actualizado guardado como: {archivo_existente}")

    keywords =  PalabrasClave_Datos + PalabrasClave_Energía + keywords_data + keywords_Energy

    vacantes_relevantes = df_vacantes[df_vacantes["Título"].str.lower().apply(
        lambda titulo: any(kw in titulo for kw in keywords)
    )]

    archivo_vacantes_relevantes = f"Vacantes_Relevantes_LinkedIn_{fecha_hoy}.xlsx"
    vacantes_relevantes.to_excel(archivo_vacantes_relevantes, index= False)
    logging.info(f'{len(vacantes_relevantes)} vacantes relevantes guardadas en {archivo_vacantes_relevantes}')


if __name__ == "__main__":

    load_dotenv("credenciales.env")
    username = os.getenv("LINKEDIN_USER")
    password = os.getenv("LINKEDIN_PASSWORD")

    df = []
    Empresas_sin_vacantes = []
    archivo_existente = "Vacantes_LinkedIn.xlsx"
    fecha_hoy = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archivo_nuevos = f"Nuevos_Trabajos_LinkedIn_{fecha_hoy}.xlsx"

    if os.path.isdir("C:\\Users\\lgael\\OneDrive\\Documentos\\Python\\WebScrapingLinkedln"):
        path = "C:\\Users\\lgael\\OneDrive\\Documentos\\Python\\WebScrapingLinkedln"
        logging.info("Directorio de G.G. encontrado.")
    else:
        logging.error("Verificar directorio raíz del script y archivos")
        
    url = 'https://www.linkedin.com/login/es'


    driver = setup_driver(path)

    start_driver_and_login(driver, url,username,password)

    print("Proceso de extracción de datos de empresas grandes comenzado....")
    for empresa in empresas:
        buscar_empresa(driver,empresa)
    
        Filtros(driver)

        if empresa_sin_vacantes(driver,empresa):
            Empresas_sin_vacantes.append(empresa)
            back(driver,2)
            continue

        Info = extraer_informacion_vacante(driver)
        back(driver,2)
        for vacante in Info:
            vacante["EmpresaBuscada"] = empresa
            df.append (vacante)

    logging.info("Proceso de extracción de datos empresas grandes completado.")   
    back(driver,1)
    print("----------------------------------------------------------------------------------------------------------------------------------------")
    logging.info("Proceso de extración de datos de empresas pequeñas comenzado....")
   
    for empresa_pequeña in empresas_pequeñas:
        buscar_empresa(driver,empresa_pequeña)

        if empresa_sin_vacantes(driver,empresa_pequeña):
            Empresas_sin_vacantes.append(empresa_pequeña)
            back(driver,2)
            continue

        Filtros(driver)

        if empresa_sin_vacantes(driver,empresa_pequeña):
            Empresas_sin_vacantes.append(empresa_pequeña)
            back(driver,2)
            continue

        Info = extraer_informacion_vacante(driver)
        back(driver,2)
        for vacante in Info:
            vacante["EmpresaBuscada"] = empresa_pequeña
            df.append (vacante)
    print("Proceso de extración de datos de empresas pequeñas finalizado")
    print("-----------------------------------------------------------------------------------------------------------------------------------------")
    logging.info("Proceso de extración de datos de empresas sin filtros comenzado....")
    for empresa_sin_filtros in empresas_sin_filtros:
        buscar_empresa(driver,empresa_sin_filtros)

        if empresa_sin_vacantes(driver,empresa_sin_filtros):
            Empresas_sin_vacantes.append(empresa_sin_filtros)
            back(driver,2)
            continue

        Info = extraer_informacion_vacante(driver)
        back(driver,2)
        for vacante in Info:
            vacante["EmpresaBuscada"] = empresa_sin_filtros
            df.append (vacante)

    print("---------------------------------------------------------------------------------------------------------------------------------------------")
    logging.info("Empresas sin vacantes:")
    for nombre in Empresas_sin_vacantes:
        print(f"- {nombre}")

    to_excel(archivo_existente, fecha_hoy, archivo_nuevos)

