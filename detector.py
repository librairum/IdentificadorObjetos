from roboflow import Roboflow
import cv2
from collections import Counter
import os

# 🎯 CONFIGURACIÓN
API_KEY = "VmrbtYS8UdbyJEjROGxV"
CONFIDENCE = 25  # Sensibilidad: menor valor = más detecciones (ajústalo si hay falsos positivos)
OVERLAP = 30
RESULTS_DIR = "results"
OUTPUT_IMAGE = os.path.join(RESULTS_DIR, "imagen_detectada.png")

# 🔠 Mapeo de clases a etiquetas finales
CLASES = {
    "0": "árbol",
    "1": "casa",
    "arbol": "árbol",
    "árbol": "árbol",
    "tree": "árbol",
    "??rbol": "árbol",
    "casa": "casa",
    "house": "casa",
    "casa-estandar": "casa",
    "casa-de-adobe": "casa"
}

# 🎨 Colores por clase
COLORES = {
    "árbol": (0, 255, 0),   # Verde
    "casa": (255, 0, 0)     # Rojo
}

# 🔐 Inicializa Roboflow una sola vez
rf = Roboflow(api_key=API_KEY)

# ✅ Usa las versiones 5 de tus modelos entrenados recientemente
modelo_casas = rf.workspace("jhosua").project("housedetection-qev1y-y03hc").version(5).model
modelo_arboles = rf.workspace("jhosua").project("objdet1-xb21r").version(5).model

def detectar_objetos(img_path: str):
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {img_path}")

    # 🧠 Ejecutar detección con ambos modelos
    preds_casas = modelo_casas.predict(img_path, confidence=CONFIDENCE, overlap=OVERLAP).json()['predictions']
    preds_arboles = modelo_arboles.predict(img_path, confidence=CONFIDENCE, overlap=OVERLAP).json()['predictions']
    todas_preds = preds_casas + preds_arboles

    conteo = Counter()

    for pred in todas_preds:
        clase_raw = pred['class'].strip().lower()
        clase = CLASES.get(clase_raw, "desconocido")
        conteo[clase] += 1

        x, y, w, h = pred['x'], pred['y'], pred['width'], pred['height']
        x1, y1 = int(x - w / 2), int(y - h / 2)
        x2, y2 = int(x + w / 2), int(y + h / 2)

        color = COLORES.get(clase, (0, 255, 255))  # Amarillo si clase desconocida
        etiqueta = f"{clase.capitalize()}" if clase != "desconocido" else "?"
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, etiqueta, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    cv2.imwrite(OUTPUT_IMAGE, img)

    return OUTPUT_IMAGE, conteo
