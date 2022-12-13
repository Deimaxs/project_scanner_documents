from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

from PIL import Image, ImageTk
import imutils
import cv2

import pytesseract

import pandas as pd
from itertools import zip_longest

from google.oauth2 import service_account
import pandas_gbq

import numpy as np

#Objeto usado para la conexión con BigQuery
bq_credentials=service_account.Credentials.from_service_account_file('python-bigquery/quiet-maxim-367218-64eeb5f73b71.json')
#Método usado por la librería
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

#Funciones utiles 
def extract(target, text, num_word=0):
    ext = list(filter(lambda x: target in x, text))[num_word]
    ext = ext[ext.find(target)+len(target)+1:]
    return ext

def position_search(target ,text):
    for i in enumerate(text):
        if i[1].startswith(target):
            break
    return i[0]

def ordenar_puntos(puntos):
	n_puntos = np.concatenate([puntos[0], puntos[1], puntos[2], puntos[3]]).tolist()
	y_order = sorted(n_puntos, key=lambda n_puntos: n_puntos[1])
	x1_order = y_order[:2]
	x1_order = sorted(x1_order, key=lambda x1_order: x1_order[0])
	x2_order = y_order[2:4]
	x2_order = sorted(x2_order, key=lambda x2_order: x2_order[0])
	return [x1_order[0], x1_order[1], x2_order[0], x2_order[1]]


#Clase donde se buscan, almacenan y envian los datos
class Datos:

    def __init__(self):
        self.data=[]

    def retriever(self, image):
        texto = pytesseract.image_to_string(image, lang='spa', config='--psm 6', output_type='dict')
        texto = texto.get("text").splitlines()

        fecha = extract("Fecha:", texto)
        orden = extract("orden:", texto)
        cliente = extract("ENVIAR A:", texto)
        sub_total = extract("Subtotal", texto)
        iva = extract("IVA", texto)
        envio = extract("Envío", texto)
        otro = extract("Otro", texto)
        total = extract("TOTAL", texto, 1)

        articulo = []
        producto = []
        cantidad = []
        precio = []
        costo = []

        art = position_search("ARTÍCULO", texto)
        sub = position_search("Subtotal", texto)

        for i in texto[art+1:sub]:
            articulo.append(i.split(" ", 1)[0])
            producto.append(i.split(" ")[::-1][4]+ " " +i.split(" ")[::-1][3]) if not i.startswith("ART") else producto.append(i.split(" ")[::-1][3])
            cantidad.append(i.split(" ")[::-1][2])
            precio.append(i.split(" ")[::-1][1])
            costo.append(i.split(" ")[::-1][0])
            
        self.data=[fecha, orden, cliente, sub_total, iva, envio, otro, total, articulo, producto, cantidad, precio, costo]
        
    def send(self):
        opt = messagebox.askquestion("Enviar data", "¿Desea enviar la data a la base de datos?") 

        if opt =="yes":
            sql = """SELECT orden FROM quiet-maxim-367218.conjuntobq.facturas WHERE orden = @orden"""
            query_config = {
                'query': {
                    'parameterMode': 'NAMED',
                    'queryParameters': [
                        {
                            'name': 'orden',
                            'parameterType': {'type': 'STRING'},
                            'parameterValue': {'value': self.data[1]}
                        },
                    ]
                }
            }
            df_bq = pd.read_gbq(sql, configuration=query_config, project_id='quiet-maxim-367218', credentials=bq_credentials, dialect='standard')

            if df_bq.empty:
                df_data = [(self.data[0], self.data[1], self.data[2], self.data[3], self.data[4], self.data[5], self.data[6], self.data[7], *x) for x in zip_longest(self.data[8], self.data[9], self.data[10], self.data[11], self.data[12])]
                df = pd.DataFrame(df_data, columns=["fecha", "orden", "cliente", "sub_total", "iva", "envio", "otro", "total", "articulo", "producto", "cantidad", "precio", "costo"])
                
                df = df.astype(str).apply(lambda x: x.str.replace(r"\.","", regex=True))
                df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True)
                df = df.astype({'orden': 'string', 'cliente': 'string', 'articulo': 'string', 'producto': 'string',
                                'sub_total': 'int', 'iva': 'int', 'envio': 'int', 'otro': 'int',
                                'total': 'int', 'cantidad': 'int', 'precio': 'int', 'costo': 'int'
                                })

                pandas_gbq.to_gbq(df, 'conjuntobq.facturas', project_id='quiet-maxim-367218', if_exists='append', credentials=bq_credentials)
                
                messagebox.showinfo("Información", "Carga terminada!")
            else:
                messagebox.showwarning("Información", "El número de orden ya se encuentra en la base de datos!")
            

#Clase que almacena y muestra la imagen seleccionada
class Imagen:
    image=None        

    def show_image(self, path_image):
        self.image = cv2.imread(path_image)
        area = (self.image.shape[0]*self.image.shape[1])
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray, 10, 150)
        canny = cv2.dilate(canny, None, iterations=1)
        cnts = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:1]
        for c in cnts:
            epsilon = 0.01*cv2.arcLength(c,True)
            approx = cv2.approxPolyDP(c,epsilon,True)
            if (cv2.contourArea(approx)/area) > 0.2:
                if len(approx)==4:
                    puntos = ordenar_puntos(approx)
                    pts1 = np.float32(puntos)
                    pts2 = np.float32([[0,0],[540,0],[0,620],[540,620]])
                    M = cv2.getPerspectiveTransform(pts1,pts2)
                    self.image = cv2.warpPerspective(gray,M,(540,620))
        imageToShow=imutils.resize(self.image, width=450)
        imageToShow=cv2.cvtColor(imageToShow, cv2.COLOR_BGR2RGB)
        im=Image.fromarray(imageToShow)
        self.img=ImageTk.PhotoImage(image=im)


#Clase que genera la ventana con sus labels y buttons, agregando la funcionalidad de abrir la imagen y 
# ejecutar los metodos de las clases Datos e Image
class Window():

    def __init__(self, image):
        self.image=image
        self.root=Tk()
        self.root.configure(width=680, height=900)
        self.root.title("OCR Facturas")
        self.label_image = Label(self.root)
        self.label_image.grid(column=1, row=0, rowspan=21)
        
        self.but_select = Button(self.root, text="Elegir imagen", font=(10), background="black", fg="white", width=25, padx=5, pady=5, command=self.open_file)
        self.but_select.grid(column=0, row=0, padx=5, pady=5)

        self.root.mainloop()

    def open_file(self):
        self.root.configure(width=680, height=900)
        path_image = filedialog.askopenfilename(filetypes = [('image files', ['*.jpg', ' *.jpeg', ' *.png'])]) 
        if len(path_image) > 0:
            self.image.show_image(path_image)
            
            self.label_image.configure(image=self.image.img, height=670, width=700)
            self.label_image.image=self.image.img

            datos = Datos()
            datos.retriever(path_image)

            Button(self.root, text="Enviar data", font=(10), width=25, padx=5, pady=5, background="black", fg="white", command=datos.send).grid(column=0, row=16)
            Label(text=("FECHA:     " + datos.data[0]), font=(9)).grid(column=0, row=18)
            Label(text=("ORDEN:     " + datos.data[1]), background="gray", fg="white", font=(9)).grid(column=0, row=17)
            Label(text=("CLIENTE:   " + datos.data[2]), font=(9)).grid(column=0, row=19)
            Label(text=("TOTAL:     " + datos.data[7]), font=(9)).grid(column=0, row=20)