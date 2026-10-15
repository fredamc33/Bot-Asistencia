import os
import time
import random
import sys
from datetime import datetime

def log(mensaje):
    print(mensaje)
    sys.stdout.flush()  # Muestra el mensaje inmediatamente en los registros de GitHub

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
    hoy = datetime.now()
    
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
        log("Turno Tarde: Procediendo al registro de salida...")
        texto_boton = "FINALIZAR TURNO"

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    
    # Evitar que se quede colgado indefinidamente si la web tarda en cargar
    driver.set_page_load_timeout(30)
    
    try:
        log("1. Abriendo la página de acceso...")
        driver.get("https://registrar.asistencia.work/sistema/acceso/panel")
        
        log("2. Ingresando credenciales...")
        usuario_input = WebDriverWait(driver, 20).until(
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
        
        # Forzar clic en el botón principal
        driver.execute_script("arguments[0].click();", btn_turno)
        log("Clic realizado en el botón principal. Buscando la ventana emergente...")
        
        # 5. Si es el turno de la tarde, esperar y presionar el botón CONTINUAR de la advertencia
        if texto_boton == "FINALIZAR TURNO":
            btn_continuar = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='CONTINUAR']"))
            )
            driver.execute_script("arguments[0].click();", btn_continuar)
            log("¡Botón 'CONTINUAR' presionado con éxito en la ventana emergente!")

        # Pausa final para asegurar que el servidor procese el guardado completo
        time.sleep(6)
        log(f"¡Proceso de '{texto_boton}' completado con éxito!")

    except Exception as e:
        log(f"Ocurrió un error durante la ejecución: {e}")
        try:
            log(f"URL al fallar: {driver.current_url}")
        except:
            pass
        raise e
        
    finally:
        driver.quit()

if __name__ == "__main__":
    registrar_asistencia()