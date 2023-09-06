import cv2
import pytesseract 

def extract_text(image_path):
    #Usar a lib opencv para abrir a imagem
    imagem = cv2.imread(image_path)

    #Usar o pytesseract para extrair o texto da imagem:
    text= pytesseract.image_to_string(imagem)
    
    return (text)
