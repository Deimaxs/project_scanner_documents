import cv2
import pytesseract
import utils

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

image = cv2.imread('prueba11.jpg')
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

texto = pytesseract.image_to_string(image, lang='spa', config='--psm 6', output_type='dict')
texto = texto.get("text").splitlines()

fecha = utils.extract("Fecha:", texto)
orden = utils.extract("orden:", texto)
cliente = utils.extract("ENVIAR A:", texto)
sub_total = utils.extract("Subtotal", texto)
iva = utils.extract("IVA", texto)
envio = utils.extract("Envío", texto)
otro = utils.extract("Otro", texto)
total = utils.extract("TOTAL", texto, 1)

articulo = []
producto = []
cantidad = []
precio = []
costo = []

art = utils.position_search("ARTÍCULO", texto)
sub = utils.position_search("Subtotal", texto)

for i in texto[art:sub]:
    articulo.append(i.split(" ", 1)[0])
    producto.append(i.split(" ")[::-1][4]+ " " +i.split(" ")[::-1][3]) if not i.startswith("ART") else producto.append(i.split(" ")[::-1][3])
    cantidad.append(i.split(" ")[::-1][2])
    precio.append(i.split(" ")[::-1][1])
    costo.append(i.split(" ")[::-1][0])


print(fecha)
print(orden)
print(cliente)
print(sub_total)
print(iva)
print(envio)
print(otro)
print(total)

print(articulo)
print(producto)
print(cantidad)
print(precio)
print(costo)


# cv2.imshow('Image',image)
cv2.waitKey(0)
cv2.destroyAllWindows()
