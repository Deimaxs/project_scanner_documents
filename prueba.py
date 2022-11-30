import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

image = cv2.imread('prueba9.jpg')
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
texto = pytesseract.image_to_string(image, lang='spa', config='--psm 6')
print(texto)
      
cv2.imshow('Image',image)
cv2.waitKey(0)
cv2.destroyAllWindows()