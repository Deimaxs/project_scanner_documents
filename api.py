from google.oauth2 import service_account
from utils import position_search, extract

from itertools import zip_longest

bq_credentials=service_account.Credentials.from_service_account_file('python-bigquery/quiet-maxim-367218-64eeb5f73b71.json')

import cv2
import pytesseract
import utils
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

image = cv2.imread('prueba11.jpg')

texto = pytesseract.image_to_string(image, lang='spa', config='--psm 6', output_type='dict')
texto = texto.get("text").splitlines()

# fecha = extract("Fecha:", texto)
# orden = extract("orden:", texto)
# cliente = extract("ENVIAR A:", texto)
# sub_total = extract("Subtotal", texto)
# iva = extract("IVA", texto)
# envio = extract("Envío", texto)
# otro = extract("Otro", texto)
# total = extract("TOTAL", texto, 1)

# articulo = []
# producto = []
# cantidad = []
# precio = []
# costo = []

# art = position_search("ARTÍCULO", texto)
# sub = position_search("Subtotal", texto)

# for i in texto[art+1:sub]:
#     articulo.append(i.split(" ", 1)[0])
#     producto.append(i.split(" ")[::-1][4]+ " " +i.split(" ")[::-1][3]) if not i.startswith("ART") else producto.append(i.split(" ")[::-1][3])
#     cantidad.append(i.split(" ")[::-1][2])
#     precio.append(i.split(" ")[::-1][1])
#     costo.append(i.split(" ")[::-1][0])

# data=[fecha, orden, cliente, sub_total, iva, envio, otro, total, articulo, producto, cantidad, precio, costo]
# test = [(fecha, orden, cliente, sub_total, iva, envio, otro, total, *x) for x in zip_longest(articulo, producto, cantidad, precio, costo)]

# df=pd.DataFrame(test, columns=["fecha", "orden", "cliente", "sub_total", "iva", "envio", "otro", "total", "articulo", "producto", "cantidad", "precio", "costo"])


# df = df.astype(str).apply(lambda x: x.str.replace("\.",""))

# df['fecha'] = pd.to_datetime(df['fecha'])
# df = df.astype({'orden': 'string', 'cliente': 'string', 'articulo': 'string', 'producto': 'string',
#                 'sub_total': 'int', 'iva': 'int', 'envio': 'int', 'otro': 'int',
#                 'total': 'int', 'cantidad': 'int', 'precio': 'int', 'costo': 'int'
#                 })
# print(df.dtypes)



fecha = utils.extract("Fecha:", texto)
orden = utils.extract("orden:", texto)
cliente = utils.extract("ENVIAR A:", texto)

df = []
df.append(["12/1/2021", "a20", "cente2", 1, 1, 1,1, 1, "cente2","fe", 1, 1, 1])

df = pd.DataFrame(df, columns=["fecha", "orden", "cliente", "sub_total", "iva", "envio", "otro", "total", "articulo", "producto", "cantidad", "precio", "costo"])

import pandas_gbq

pandas_gbq.to_gbq(df, 'conjuntobq.facturas', project_id='quiet-maxim-367218', if_exists='replace', credentials=bq_credentials)

# sql = """SELECT orden FROM quiet-maxim-367218.conjuntobq.facturas WHERE orden = @orden"""
# df_bq= pd.read_gbq(sql, project_id='quiet-maxim-367218', credentials=bq_credentials, dialect='standard')
# if not df_bq.empty: print(df_bq) 