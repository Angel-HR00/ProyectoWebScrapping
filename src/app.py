import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# elijo la url de descarga
resource_url = "https://www.macrotrends.net/stocks/charts/TSLA/tesla/revenue"
data = requests.get(resource_url, time.sleep(10)).text

#Cabecera si no conectamos
if "403 Forbidden" in data:
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}
    request = requests.get(resource_url, headers = headers)
    time.sleep(10)
    data = request.text

print(data)

#Conversion a HTML y buscamos las etiquietas "table"
soup = BeautifulSoup(data,"html.parser")
tables = soup.find_all("table")


#Buscar la tabla que necesitamos 
for i, x in enumerate(tables):
    if ("Tesla Quarterly Revenue" in str(x)):
        table_index = x
        break

#Creacion del dataframe con la tabla
tesla_rev = pd.DataFrame(columns = ["Date", "Revenue"])
for row in tables[table_index].tbody.find_all("tr"):
    col = row.find_all("td")
    if (col != []):
        Date = col[0].text
        Revenue = col[1].text.replace("$", "").replace(",", "")
        tesla_rev = pd.concat([tesla_rev, pd.DataFrame({
            "Date": Date,
            "Revenue": Revenue
        }, index = [0])], ignore_index = True)


#Quitamos los datos del dataframe que están vacíos
tesla_rev = tesla_rev[tesla_rev["Revenue"] != ""]

#Conexion a la base de datos de SQLite
connection = sqlite3.connect("BDTesla.db")
cursor = connection.cursor()
cursor.execute("""CREATE TABLE revenue (Date, Revenue)""")

tesla_tuples = list(tesla_rev.to_records(index = False))
cursor.executemany("INSERT INTO revenue VALUES (?,?)", tesla_tuples)
for row in cursor.execute("SELECT * FROM revenue"):
    print(row)
    
#Visualizar datos
fig, axis = plt.subplots(figsize = (10, 5))

tesla_rev["Date"] = pd.to_datetime(tesla_rev["Date"])
tesla_rev["Revenue"] = tesla_rev["Revenue"].astype('int')
sns.lineplot(data = tesla_rev, x = "Date", y = "Revenue")

plt.tight_layout()
plt.show()