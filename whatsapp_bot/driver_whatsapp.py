import time
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


from .df_utils import *

def callbell_login(driver_ser, url_service, user=None, pass_user=None, delay=None):
    # Navigate to the Callbell login page
    driver_ser.get(url_service)
    # Wait for the page to load
    time.sleep(delay[0])
    
    # Find the input fields and enter the necessary login information
    email_input = driver_ser.find_element(By.ID,'user_email')
    email_input.clear()
    email_input.send_keys(user)
    time.sleep(delay[1])

    password_input = driver_ser.find_element(By.ID, 'user_password')
    password_input.clear()
    password_input.send_keys(pass_user)
    
    time.sleep(delay[2])
    password_input.send_keys(Keys.RETURN)

    # Wait for the dashboard page to load
    time.sleep(delay_list(8, 12, 1)[0])
    
    return driver_ser

def enter_phone_number(driver_ser, phone_number, delay_l, index_loop):   
    ## new message
    messaging_icon = driver_ser.find_element(By.XPATH,"//div[@class='fullwidth-container chat-container']//div[@class='mr-4']").click()
    time.sleep(delay_l[0])
    number_s = driver_ser.find_element(By.ID, 'phone-form-control')
    number_s.clear()
    if index_loop==0:
        number_s.send_keys('51'+str(phone_number))
    else:
        number_s.send_keys(str(phone_number))
    time.sleep(delay_l[1])
    
    return

def send_each_text(html, sms_to_send, delay):
    html.send_keys(sms_to_send)
    time.sleep(delay[5])

def type_message(driver_ser, delay_list, df_sms):
    ## the main windown to send a message is hidden, so it has to be made visible 
    hidden_element = driver_ser.find_element(By.XPATH,"//div[@class='flex-grow h-screen main-content']/div[@class='fullwidth-container chat-container']/div[@data-react-class='v2/Chat']")
    driver_ser.execute_script("arguments[0].style.visibility = 'visible';", hidden_element)
    
    try:
        text_m=hidden_element.find_element(By.XPATH,"//textarea[@placeholder='Type a message']")
    except:
        text_m=hidden_element.find_element(By.XPATH,"//textarea[@placeholder='Escribe un mensaje']")
      
    text_m.clear()
    time.sleep(delay_list[4])
    
    for p in range(0, df_sms.count()[0]):
        sms_un=df_sms.iloc[p,0]
        send_each_text(html=text_m, sms_to_send=sms_un, delay=delay_list)

def select_tag(driver_ser, estado=None):
    short_delay_loop = delay_list(1.5, 2.5, 4)
    time.sleep(short_delay_loop[0])
    close_notification= driver_ser.find_element(By.XPATH,"//div[@class='flex-grow h-screen main-content']//button[@class='Toastify__close-button Toastify__close-button--default']").click()
    # clinking on the tags
    hidden_element = driver_ser.find_element(By.XPATH,"//div[@class='flex-grow h-screen main-content']/div[@class='fullwidth-container chat-container']/div[@data-react-class='v2/Chat']")
    driver_ser.execute_script("arguments[0].style.visibility = 'visible';", hidden_element)
    
    tag1=driver_ser.find_elements(By.XPATH,"//div[@class='chat-container_tags-top-bar shadow rounded-t-lg bg-white dark:bg-dark-800 px-4 py-4']//div[@class='flex flex-row']/div[@class='mx-1']")[1]
    
    time.sleep(short_delay_loop[1])
    tag_click=tag1.find_elements(By.XPATH,"//div[@class='mx-1']")[1].click()
    #tag_click2=tag_click.find_element(By.XPATH,"//span[@class=' text-gray-400 dark:text-dark-100 text  ']").click()
    time.sleep(short_delay_loop[2])
    
    if estado=="PENDIENTE":
        tag="SE_PENDIENTE"
        tag_name="//body//div[@class='css-10xsswj-menu select__menu']//div[text()='"+tag+"']"        
    else:
        tag="SE_PROCESO"
        tag_name="//body//div[@class='css-10xsswj-menu select__menu']//div[text()='"+tag+"']"
    
    tag2=tag1.find_element(By.XPATH,tag_name).click()
    time.sleep(short_delay_loop[3])        
        


def execute_bot(url_bd, url_sms, dre_name=None, ugel_cod=None, var_start=None, var_end=None, user=None, pass_user=None, google_drive=False, test=False, seguimiento=False, estado_segui=None, tipologia_segui=None, first_report=False):
    '''
  #Docstring:
    Ejecuta el bot para el envio automático de mensajes de whatsapp usando el servicio de Callbell y los usuarios creados para Matrícula Digital.
    Ejecutado de forma local, abre una nuevo navegador de google Chrome en modo incognito.
    Ejecutado desde google Drive, ejecuta el código en modo 'headless', sin necesidad de abrir una ventana del navegador.
  
  Parameters
    ----------            
    url_bd: str, url de la base de datos (BD) de directores alojada en el drive del proyecto.
        Si se desea utilizar otra BD de números telefónicos, la base de datos debe tener como mínimo las siguientes variables:
        ['DRE', 'UGEL', 'phone_numbers','codooii']
    url_sms: str, url de la BD de los textos que serán envíados
    dre_name: str, default None. Es el nombre de la DRE por la cual se quiere filtrar. El nombre deber ser igual al de la BD de url_bd.
        En caso no se introduzca un valor, se carga toda la BD.
    ugel_cod: str, default None. Es el código de identificación (codooii) de la UGEL por la cual se quiere filtra la BD.
        Esta variable debe estar en formato texto. Además, el código de la UGEL debe ser igual al de la BD de url_bd.
        En caso no se introduzca un valor, se carga toda la BD.
    var_start: int, default None. Es la fila de inicio por la cual se quiere filtra la BD.
        Tener en consideración que en Python la primera fila de una BD corresponde al valor 0 y no al valor 1.
        Por lo tanto, si se desea filtrar desde la fila 10, el valor de var_start será 9.
    var_end: int, default None. Es la fila de término por la cual se quiere filtra la BD.
        Tener en consideración que en Python la primera fila de una BD corresponde al valor 0 y no al valor 1.
        Si se desea filtrar desde la fila 50 hasta la fila 100 los valores de var_start y var_end serán:
            var_start=49, var_end=99
    user: str, default None. Es el correo electrónico con el que se ingresará a la web de Callbell.
    pass_user: str, default None. Es el password con el que se ingresará a la web de Callbell.
    google_drive: boolen, default False. Es True cuando el bot se ejecute desde la aplicación colab de google drive.
    test: boolen, default False. Aplica en caso se desea hacer un test usando una BD de teléfonos de prueba.
    
    '''
    if seguimiento==True:
        estado_c=estado_segui.upper().strip().replace("EN ","")
        df=cleaning_report_status_df(url=url_bd, estado=estado_c, tipologia=tipologia_segui,var_start=var_start, var_end=var_end,test=test,first_rep=first_report)
        print("El número de filas de la BD es: ", df.count()[0])
        ## getting the messages from data located on google drive
        df1=get_excel_txt(url=url_sms, seguimiento_text=seguimiento, estado=estado_c, tipologia=tipologia_segui)
        
    else:
        ## directivos' data
        df=open_directivos_EBR(url=url_bd, dre_name=dre_name, ugel_cod=ugel_cod, var_start=var_start, var_end=var_end, test=test)
        print("El número de filas de la BD es: ", df.count()[0])
        ## getting the messages from data located on google drive
        df1=get_excel_txt(url_sms)
    
    #setting the delay
    delay1=delay_list(3, 9, 4)

    # Initialize the web driver
    options = webdriver.ChromeOptions() #carga configuración del webdriver
    
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_argument('--no-sandbox')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    if google_drive==True:
        from fake_useragent import UserAgent
        ua = UserAgent()
        user_agent = ua.chrome
        options.add_argument(f'user-agent={user_agent}') 
        options.add_argument('--headless') 
    
    driver=webdriver.Chrome('chromedriver',options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    url_service='https://dash.callbell.eu/users/sign_in'

    ##logging on callbell
    callbell_login(driver_ser=driver, url_service=url_service, delay=delay1, user=user, pass_user=pass_user)

    ##opening the message windown
    messaging_icon = driver.find_element(By.XPATH,"//a[@href='/chat']").click()
    time.sleep(delay1[3])

    ## create a loop to itterate through the phone number list
    for index, phone_number in df.phone_numbers.items():
        ## set a delay list for each itteration
        delay2=delay_list(2.5, 5.5, 7)

        enter_phone_number(driver_ser=driver,phone_number=phone_number, delay_l=delay2, index_loop=index)
        
        try:
            open_wi= driver.find_element(By.XPATH,"//div[@class='modal overflow-visible']//div[@class='modal_content-body']//span[@class='mr-2  text  ']").click()
        except:
            if user in ["gestionmatricula@gmail.com","whatsappoperador1@gmail.com","whatsappoperador2@gmail.com"]: ## only the head account can open an existing chat
                open_wi= driver.find_element(By.XPATH,"//div[@class='modal overflow-visible']//div[@class='modal_content-body']//div[@class='text-sm']").click()
            else:                                  ## for everyone else if the chat is created bot'd skip this step and it will continue with the next phone_number
                open_wi= driver.find_element(By.XPATH,"//div[@class='modal overflow-visible']//div[@class='flex flex-row items-center w-full justify-between mb-4']//div[@class='items-center   ']").click()
                time.sleep(delay2[2])
                continue

        time.sleep(delay2[2])

        type_message(driver_ser=driver, delay_list=delay2, df_sms=df1)
        
        if seguimiento==True:
            select_tag(driver_ser=driver, estado=estado_c)
            
        df.loc[index, 'envio'] = 1
        
    driver.quit()
    return df