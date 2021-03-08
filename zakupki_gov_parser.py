import ftplib
import os
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd



path = 'C:\\sw\\'
customer = 'УПРАВЛЕНИЕ ФЕДЕРАЛЬНОЙ СЛУЖБЫ ИСПОЛНЕНИЯ НАКАЗАНИЙ ПО РЕСПУБЛИКЕ МАРИЙ ЭЛ'
find_customer = './/{http://zakupki.gov.ru/oos/export/1}contract/{http://zakupki.gov.ru/oos/types/1}customer/{http://zakupki.gov.ru/oos/types/1}fullName'
os.chdir(path)


def download_xml(directory):           # Подключаюсь к FTP, к определенной папке, беру и скачиваю данные
    ftp = ftplib.FTP()
    ftp.connect('ftp.zakupki.gov.ru')
    ftp.login('free', 'free')
    ftp.cwd(f'/fcs_regions/{directory}/contracts/prevMonth') # Республика Марий Эл - Marij_El_Resp (prevMonth - предыдущий месяц, currMonth - текущий месяц) 
    files = ftp.nlst()
    for file in files:
        fn = open(file, 'wb')
        ftp.retrbinary('RETR ' + file, fn.write)



def search_zip_file(path):    # Ищу архивы в папке переменной Path
    zip_files = []
    view_zipfile = os.listdir(path)
    for file in view_zipfile:
        if zipfile.is_zipfile(file) == True:
            zip_files.append(file)
    return zip_files


def extract_xml(path):       # Беру найденные архивы и разархивирую только XML файлы  
    for file in search_zip_file(path):       
        my_zip = zipfile.ZipFile(path + file, 'r')
        info_zip = my_zip.namelist()
        for name in info_zip:
            if name[-3:] == 'xml' and name[0:9] == 'contract_':
                my_zip.extract(name)
        my_zip.close()


def sort_xml_by_customer(xml_path):
    sorted_xml = []
    for file in os.listdir():
        if file[-3:] == 'xml':
            tree = ET.parse(xml_path+file)
            root = tree.getroot()
            if root.find(find_customer).text == customer:
                sorted_xml.append(file)
    return sorted_xml
    

def make_df():
    contract_data = []
    cd = []

    for contract in sort_xml_by_customer(path):
        tree = ET.parse(path + contract)
        root = tree.getroot()


        customer_name = root.find('.//{http://zakupki.gov.ru/oos/types/1}shortName').text


        contractSubject = root.find('.//{http://zakupki.gov.ru/oos/types/1}contractSubject').text
        

        products = []
        for code in root.findall('.//{http://zakupki.gov.ru/oos/types/1}product'):
            product = code.find('{http://zakupki.gov.ru/oos/types/1}name').text
            products.append(product)


        nationalCode = []
        for code in root.findall('.//{http://zakupki.gov.ru/oos/types/1}OKEI'):
            okei = code.find('{http://zakupki.gov.ru/oos/types/1}nationalCode').text
            nationalCode.append(okei)


        supplier = []
        for code in root.findall('.//{http://zakupki.gov.ru/oos/types/1}suppliers/'):
            name = code.find('.//{http://zakupki.gov.ru/oos/types/1}shortName').text
            supplier.append(name)
        

        signDate = root.find('.//{http://zakupki.gov.ru/oos/types/1}signDate').text


        number = root.find('.//{http://zakupki.gov.ru/oos/types/1}number').text


        quantity = []
        for code in root.findall('.//{http://zakupki.gov.ru/oos/types/1}product'):
            quant = code.find('{http://zakupki.gov.ru/oos/types/1}quantity').text
            quantity.append(quant)

        
        priceRUR = []
        for code in root.findall('.//{http://zakupki.gov.ru/oos/types/1}product'):
            price = code.find('{http://zakupki.gov.ru/oos/types/1}priceRUR').text
            priceRUR.append(price)    


        priceInfo = root.find('.//{http://zakupki.gov.ru/oos/types/1}priceInfo/{http://zakupki.gov.ru/oos/types/1}price').text
        
        href = root.find('.//{http://zakupki.gov.ru/oos/types/1}href').text


        i = 0
        while i <= len(products)-1:
            cd.append(customer_name)
            cd.append(contractSubject)
            cd.append(products[i])
            cd.append(nationalCode[i])
            cd.extend(supplier)
            cd.append(number)
            cd.append(signDate)
            cd.append(quantity[i])
            cd.append(priceRUR[i])
            cd.append(priceInfo)
            cd.append(href)
            i += 1

    return cd





columns = [
'Наименование государственного заказчика', # customer ##### Customer organization
'Наименование объекта закупки', # contractSubject     ##### Object of contract
'Наименование товара', # products                     ##### Product name 
'Единицы измерения', # nationalCode                   ##### unit name
'Поставщик', # supplier                               ##### Supplier organization
'Номер контрака', # number                            ##### Number of contract
'Дата заключения контракта', # signDate               ##### Data of sign contact
'Количество', # quantity                              ##### Quantity of product
'Цена за ед., руб', # sumRUR                          ##### Unit price
'Сумма', # priceInfo                                  ##### Contract amount
'Ссылка на контракт в ЕИС'] #href                     ##### link to contract (https://zakupki.gov.ru/)






# В функцию download_xml(directory) необходимо передавать директорию региона, расположенного на ftp сервере zakupki.gov.ru 
# из реестра контрактов, тоесть ftp://ftp.zakupki.gov.ru/fcs_regions/(наменование региона из файла Regions.txt)/(при необходимости 
# определенный месяц (prevMonth - предыдущий месяц, currMonth - текущий месяц))
# 

def delete_data():
    for file in os.listdir(path):
        if not file[-4:] == 'xlsx':
            os.remove(path+file)



def parser():
    download_xml('Marij_El_Resp')
    extract_xml(path=path)
    contracts = make_df()
    data = [contracts[i:i + len(columns)] for i in range(0, len(contracts), len(columns))]
    df = pd.DataFrame(columns = columns, data = data)
    df.to_excel('Реестр контрактов.xlsx')
    delete_data()

parser()



