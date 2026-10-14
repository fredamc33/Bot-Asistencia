import os
import time
import random
from datetime import datetime

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
    
    # Validar si hoy es feriado o fin de semana
    if es_feriado(hoy):
        print("Hoy es fin de semana o feriado oficial. No se registrará asistencia.")
        return

    # Determinar si es turno de mañana o tarde según la hora actual
    hora_actual = hoy.hour
    if hora_actual < 14:
        # Turno mañana: Aplicar retraso aleatorio (0 a 10 minutos) si se ejecuta a las 8:55 a.m.
        retraso_aleatorio = random.randint(0, 600)
        print(f"Turno Mañana: Esperando {retraso_aleatorio} segundos...")
        time.sleep(retraso_aleatorio)
        texto_boton = "INICIAR TURNO"
    else:
        # Turno tarde: Ejecución a las 6:30 p.m.
        print("Turno Tarde: Procediendo al registro de salida...")
        texto_boton = "FINALIZAR TURNO"

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
        
        # 5. Esperar el botón correspondiente (INICIAR TURNO o FINALIZAR TURNO)[cite: 4]
        btn_turno = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{texto_boton}')]"))
        )
        btn_turno.click()
        
        time.sleep(5)
        print(f"¡Acción '{texto_boton}' registrada con éxito!")

    except Exception as e:
        print(f"Ocurrió un error durante la ejecución: {e}")
        raise e
        
    finally:
        driver.quit()

if __name__ == "__main__":
    registrar_asistencia()