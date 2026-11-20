import os
import time
import random
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

def log(mensaje):
    print(mensaje)
    sys.stdout.flush()

def es_feriado(fecha):
    feriados_2026 = [
        "01-01", "04-02", "04-03", "05-01", "06-07", "06-29", 
        "07-23", "07-28", "07-29", "08-06", "08-30", "10-08", 
        "11-01", "12-08", "12-09", "12-25"
    ]
    if fecha.weekday() >= 5:
        return True
    mes_dia = fecha.strftime("%m-%d")
    if mes_dia in feriados_2026:
        return True
    return False

def registrar_asistencia():
    zona_peru = ZoneInfo("America/Lima")
    hoy = datetime.now(zona_peru)
    
    log(f"Hora actual detectada en Perú: {hoy.strftime('%Y-%m-%d %H:%M:%S')}")

    if es_feriado(hoy):
        log("Hoy es fin de semana o feriado oficial. No se registrará asistencia.")
        return

    hora_actual = hoy.hour
    minuto_actual = hoy.minute
    
    if hora_actual < 14:
        texto_boton = "INICIAR TURNO"
        # Si ya pasaron las 09:05, ejecutar sin espera aleatoria
        if hora_actual > 9 or (hora_actual == 9 and minuto_actual >= 5):
            log("Turno Mañana (pasadas las 09:05): Ejecutando registro de inmediato sin espera...")
        else:
            retraso_aleatorio = random.randint(0, 600)
            log(f"Turno Mañana: Esperando {retraso_aleatorio} segundos...")
            time.sleep(retraso_aleatorio)
    else:
        texto_boton = "FINALIZAR TURNO"
        # Si ya pasaron las 18:35, ejecutar sin espera aleatoria
        if hora_actual > 18 or (hora_actual == 18 and minuto_actual >= 35):
            log("Turno Tarde (pasadas las 18:35): Ejecutando registro de salida de inmediato sin espera...")
        else:
            retraso_aleatorio = random.randint(0, 300)
            log(f"Turno Tarde: Esperando {retraso_aleatorio} segundos para el registro de salida...")
            time.sleep(retraso_aleatorio)

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    max_intentos = 7
    
    for intento in range(1, max_intentos + 1):
        log(f"\n--- Iniciando intento {intento} de {max_intentos} ---")
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        # Opciones Anti-Bot y Evasión de Firewall
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=options)
        
        # Ocultar la bandera de "webdriver" mediante JavaScript interno
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        driver.set_page_load_timeout(45)
        
        try:
            log("1. Abriendo la página de acceso...")
            driver.get("https://registrar.asistencia.work/sistema/acceso/panel")
            
            log("2. Ingresando credenciales...")
            usuario_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "usuario"))
            )
            usuario_input.clear()
            usuario_input.send_keys(os.environ.get("ASISTENCIA_USER"))
            
            password_input = driver.find_element(By.ID, "clave")
            password_input.clear()
            password_input.send_keys(os.environ.get("ASISTENCIA_PASSWORD"))
            
            log("3. Haciendo clic en el botón Ingresar...")
            btn_login = driver.find_element(By.XPATH, "//button[contains(text(), 'Ingresar')]")
            btn_login.click()
            
            time.sleep(5)
            log(f"URL actual tras login: {driver.current_url}")
            
            log(f"4. Buscando el botón '{texto_boton}'...")
            btn_turno = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[normalize-space()='{texto_boton}']"))
            )
            
            # Pausa breve para asegurar que los eventos JS del modal estén cargados
            time.sleep(2)
            driver.execute_script("arguments[0].click();", btn_turno)
            log("Clic JS realizado en el botón principal.")
            
            log("Esperando la ventana emergente de confirmación...")
            btn_continuar = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, "//button[contains(translate(normalize-space(), 'continuar', 'CONTINUAR'), 'CONTINUAR')]"))
            )
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_continuar)
                
            log("Botón 'CONTINUAR' presionado. Verificando que el registro se haya guardado...")
            
            # Esperar a que el modal desaparezca por completo
            WebDriverWait(driver, 15).until(
                EC.invisibility_of_element_located((By.XPATH, "//button[contains(translate(normalize-space(), 'continuar', 'CONTINUAR'), 'CONTINUAR')]"))
            )
            
            # Pausa para que el servidor procese el guardado y recarga para confirmar en BD
            time.sleep(5)
            driver.refresh()
            time.sleep(4)
            
            # Verificación estricta: si el botón original sigue existiendo en pantalla, el registro NO se guardó
            botones_restantes = driver.find_elements(By.XPATH, f"//a[normalize-space()='{texto_boton}']")
            if len(botones_restantes) > 0 and botones_restantes[0].is_displayed():
                raise Exception(f"Falso positivo detectado: el botón '{texto_boton}' sigue visible tras confirmar.")
                
            log(f"¡Verificado en plataforma! Proceso de '{texto_boton}' guardado correctamente.")
            
            driver.quit()
            break
            
        except Exception as e:
            log(f"Ocurrió un error en el intento {intento}: {e}")
            try:
                log(f"URL al fallar: {driver.current_url}")
            except:
                pass
                
            driver.quit()
            
            if intento < max_intentos:
                log("Esperando 60 segundos antes de reintentar...")
                time.sleep(60)
            else:
                log("Se agotaron todos los intentos. El proceso finalizó con error.")
                raise e

if __name__ == "__main__":
    registrar_asistencia()
