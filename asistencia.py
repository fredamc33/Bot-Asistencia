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
    
    if hora_actual < 14:
        retraso_aleatorio = random.randint(0, 600)
        log(f"Turno Mañana: Esperando {retraso_aleatorio} segundos...")
        time.sleep(retraso_aleatorio)
        texto_boton = "INICIAR TURNO"
    else:
        retraso_aleatorio = random.randint(0, 300)
        log(f"Turno Tarde: Esperando {retraso_aleatorio} segundos para el registro de salida...")
        time.sleep(retraso_aleatorio)
        texto_boton = "FINALIZAR TURNO"

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
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(45)
        
        try:
            log("1. Abriendo la página de acceso...")
            driver.get("https://registrar.asistencia.work/sistema/acceso/panel")
            
            log("2. Ingresando credenciales...")
            # Aumentamos a 30 segundos la espera inicial para evitar fallos por lentitud del servidor
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
            
            driver.execute_script("arguments[0].click();", btn_turno)
            log("Clic realizado en el botón principal.")
            
            log("Esperando la ventana emergente de confirmación...")
            time.sleep(2)
            
            try:
                btn_continuar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(normalize-space(), 'continuar', 'CONTINUAR'), 'CONTINUAR')]"))
                )
                driver.execute_script("arguments[0].click();", btn_continuar)
                log("¡Botón 'CONTINUAR' presionado con éxito en la ventana emergente!")
            except Exception as modal_error:
                log(f"Aviso: No se pudo hacer clic en el modal automáticamente ({modal_error}). Verificando estado...")

            time.sleep(6)
            log(f"¡Proceso de '{texto_boton}' completado con éxito!")
            
            driver.quit()
            break  # Si llega hasta aquí sin errores, rompe el bucle y finaliza exitosamente
            
        except Exception as e:
            log(f"Ocurrió un error en el intento {intento}: {e}")
            try:
                log(f"URL al fallar: {driver.current_url}")
            except:
                pass
                
            driver.quit() # Cierra el navegador de este intento fallido
            
            if intento < max_intentos:
                log("Esperando 60 segundos antes de reintentar...")
                time.sleep(60)
            else:
                log("Se agotaron todos los intentos. El proceso finalizó con error.")
                raise e # Lanza el error final para que GitHub Actions marque la tarea como fallida

if __name__ == "__main__":
    registrar_asistencia()