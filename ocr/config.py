import pytesseract

# Windows-specific configuration for Tesseract OCR
# This tells Python exactly where to find tesseract.exe

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# If your Tesseract is installed in a different location, update the path above
# Common alternative locations:
# r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
# r'C:\Users\YourName\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
