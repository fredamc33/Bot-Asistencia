import os
import time
import random
from datetime import datetime

def es_feriado(fecha):
    # Lista de feriados oficiales en Perú (Formato Mes-Día: MM-DD)
    feriados_2026 = [
        "01-01", # Año Nuevo
        "04-02", # Jueves Santo
        "04-03", # Viernes Santo
        "05-01", # Día del Trabajo
        "06-07", # Batalla de Arica y Día de la Bandera
        "06-29", # San Pedro y San Pablo
        "07-23", # Día de la Fuerza Aérea del Perú
        "07-28", # Fiestas Patrias
        "07-29", # Fiestas Patrias
        "08-06", # Batalla de Junín
        "08-30", # Santa Rosa de Lima
        "10-08", # Combate de Angamos
        "11-01", # Día de Todos los Santos
        "12-08", # Inmaculada Concepción
        "12-09", # Batalla de Ayacucho
        "12-25"  # Navidad
    ]
    
    # Verificar si es fin de semana (Sábado = 5, Domingo = 6)
    if fecha.weekday() >= 5:
        return True
        
    # Verificar si coincide con algún feriado
    mes_dia = fecha.strftime("%m-%d")
    if mes_dia in feriados_2026:
        return True
        
    return False

def registrar_asistencia():
    hoy = datetime.now()
    
    # Validar si hoy es feriado o fin de semana
    if es_feriado(hoy):
        print("Hoy es fin de semana o feriado oficial. No se registrará asistencia.")
        return

    # Esperar un tiempo aleatorio entre 0 y 10 minutos (0 a 600 segundos)
    # para caer dentro del intervalo de 08:55 a 09:05 si se ejecuta a las 08:55 a.m.
    retraso_aleatorio = random.randint(0, 600)
    print(f"Esperando {retraso_aleatorio} segundos antes de proceder...")
    time.sleep(retraso_aleatorio)

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # 1. Ir a la página de acceso
        driver.get("https://registrar.asistencia.work/sistema/acceso/panel")
        
        # 2. Ingresar el usuario
        usuario_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "usuario"))
        )
        usuario_input.clear()
        usuario_input.send_keys(os.environ.get("ASISTENCIA_USER"))
        
        # 3. Ingresar la clave
        password_input = driver.find_element(By.ID, "clave")
        password_input.clear()
        password_input.send_keys(os.environ.get("ASISTENCIA_PASSWORD"))
        
        # 4. Hacer clic en el botón "Ingresar"
        btn_login = driver.find_element(By.XPATH, "//button[contains(text(), 'Ingresar')]")
        btn_login.click()
        
        # 5. Esperar a que cargue el panel interno y hacer clic en "INICIAR TURNO"
        btn_turno = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'INICIAR TURNO')]"))
        )
        btn_turno.click()
        
        time.sleep(5)
        print("¡Turno y asistencia registrados con éxito!")

    except Exception as e:
        print(f"Ocurrió un error durante la ejecución: {e}")
        raise e
        
    finally:
        driver.quit()

if __name__ == "__main__":
    registrar_asistencia()