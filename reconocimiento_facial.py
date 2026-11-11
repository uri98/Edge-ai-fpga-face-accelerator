import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F

# =====================================================================
# 1. ARQUITECTURA DE RED NEURONAL EN PYTORCH (DISEÑADA PARA FPGA)
# =====================================================================
class HardwareMicroFaceNet(nn.Module):
    def __init__(self, embedding_dim=32):
        super(HardwareMicroFaceNet, self).__init__()
        # Entrada: rostro en escala de grises de 32x32 píxeles
        self.features = nn.Sequential(
            # Bloque 1: 32x32x1 -> 16x16x8
            nn.Conv2d(1, 8, kernel_size=3, padding=1, bias=False),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Bloque 2: 16x16x8 -> 8x8x16
            nn.Conv2d(8, 16, kernel_size=3, padding=1, bias=False),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Bloque 3: 8x8x16 -> 4x4x32
            nn.Conv2d(16, 32, kernel_size=3, padding=1, bias=False),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
        # Promedio espacial (en hardware será sumar 16 números y desplazar bits)
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        # Vector facial final de 32 números
        self.fc = nn.Linear(32, embedding_dim, bias=False)

    def forward(self, x):
        x = self.features(x)
        x = self.gap(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return F.normalize(x, p=2, dim=1)

# =====================================================================
# 2. INICIALIZACIÓN DEL SISTEMA Y CÁMARA
# =====================================================================
device = torch.device("cpu")
modelo = HardwareMicroFaceNet(embedding_dim=32).to(device)
modelo.eval()  # Modo inferencia

# Detector de rostros rápido de OpenCV
detector_rostros = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def extraer_vector_facial(rostro_gris_32):
    # Convertimos la imagen de [0, 255] a [-1.0, 1.0] (ideal para aritmética con signo)
    tensor = torch.tensor(rostro_gris_32, dtype=torch.float32)
    tensor = (tensor / 127.5 - 1.0).unsqueeze(0).unsqueeze(0).to(device)
    with torch.no_grad():
        vector = modelo(tensor)
    return vector

# Abrimos la cámara web
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

vector_autorizado = None

print("\n========================================================")
print(" SISTEMA LISTO:")
print(" - Presiona 'r' para REGISTRAR tu rostro como autorizado")
print(" - Presiona 'q' para SALIR")
print("========================================================\n")

# =====================================================================
# 3. BUCLE PRINCIPAL DE RECONOCIMIENTO EN VIVO
# =====================================================================
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo leer la cámara.")
        break

    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostros = detector_rostros.detectMultiScale(gris, scaleFactor=1.2, minNeighbors=5)

    # Leemos el teclado una vez por fotograma
    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord('q'):
        break

    for (x, y, w, h) in rostros:
        # Recortamos la cara y la ajustamos a 32x32 píxeles
        recorte = gris[y:y+h, x:x+w]
        rostro_32 = cv2.resize(recorte, (32, 32))

        # Pasamos el rostro por la red neuronal de PyTorch
        vector_actual = extraer_vector_facial(rostro_32)

        # Si presionas 'r', guardamos este vector como el dueño
        if tecla == ord('r'):
            vector_autorizado = vector_actual.clone()
            print("-> ¡Rostro registrado con éxito!")

        # Evaluamos identidad
        if vector_autorizado is None:
            color = (0, 165, 255)  # Naranja
            etiqueta = "Sin registro - Presiona 'r'"
        else:
            similitud = F.cosine_similarity(vector_autorizado, vector_actual).item()
            if similitud > 0.85:
                color = (0, 255, 0)  # Verde
                etiqueta = f"AUTORIZADO ({similitud*100:.1f}%)"
            else:
                color = (0, 0, 255)  # Rojo
                etiqueta = f"DESCONOCIDO ({similitud*100:.1f}%)"

        # Dibujamos el cuadro y el texto en pantalla
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, etiqueta, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow("Edge AI - Reconocimiento Facial PyTorch", frame)

cap.release()
cv2.destroyAllWindows()
