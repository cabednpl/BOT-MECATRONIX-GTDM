import os
import re
import math
import random
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# =====================================================================
# CONFIGURACIÓN MECATRONIX (Modo Libre Activado 🟢)
# =====================================================================
LINK_PAGO_MECATRONIX = "https://link.mercadopago.com.mx/mecatronix-suscripcion"

# =====================================================================
# INTERFAZ GRÁFICA TOTALMENTE ABIERTA
# =====================================================================
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mecatronix - Auditor Inteligente de Mermas</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; }
        body { background-color: #1e222b; color: #e1e4e6; margin: 0; padding: 0; }
        .navbar { background-color: #11141a; padding: 15px 30px; border-bottom: 3px solid #3b4252; display: flex; justify-content: space-between; align-items: center; }
        .brand { font-size: 20px; font-weight: bold; color: #eceff4; letter-spacing: 1px; }
        .brand span { color: #8892b0; }
        
        .container { max-width: 900px; margin: 40px auto; padding: 20px; position: relative; }
        .panel { background-color: #2e3440; border: 1px solid #3b4252; border-radius: 6px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 25px; position: relative; }
        
        h2 { margin-top: 0; color: #eceff4; font-size: 22px; border-left: 5px solid #8892b0; padding-left: 12px; }
        p { color: #d8dee9; line-height: 1.6; }
        
        textarea { width: 100%; height: 110px; background-color: #1b1f27; border: 2px solid #434c5e; border-radius: 4px; color: #fff; padding: 12px; font-size: 15px; resize: none; margin-top: 10px; }
        
        .btn { display: inline-block; background-color: #434c5e; color: #fff; border: none; padding: 12px 24px; font-size: 15px; font-weight: bold; border-radius: 4px; cursor: pointer; text-decoration: none; text-align: center; margin-top: 15px; transition: background 0.2s; }
        .btn:hover { background-color: #4c566a; }
        
        .result-box { display: none; background-color: #3b4252; border-left: 5px solid #a3be8c; padding: 20px; margin-top: 20px; border-radius: 0 4px 4px 0; }
        .result-grid { display: table; width: 100%; margin-top: 15px; }
        .result-row { display: table-row; }
        .result-cell { display: table-cell; padding: 10px; border-bottom: 1px solid #434c5e; }
        .cell-title { font-weight: bold; color: #e5e9f0; }
        
        .alert-danger { background-color: #bf616a; color: #eceff4; padding: 15px; border-radius: 4px; margin-top: 15px; font-weight: bold; }
    </style>
</head>
<body>

    <div class="navbar">
        <div class="brand">MECATRONIX<span> .IA</span></div>
        <div><span id="statusBadge" class="status-badge" style="color:#a3be8c; font-weight:bold;">🟢 ACCESO LIBRE Y GRATUITO</span></div>
    </div>

    <div class="container">
        <div id="mainPanel" class="panel">
            <h2>Auditor Avanzado de Mermas con Precisión Continua</h2>
            <p><strong>Modo de uso:</strong> Escribe los datos del flete (pesos y km/horas). El sistema auditará bajo la curva de estrés biológico y te dará un dictamen operativo inmediato.</p>
            
            <textarea id="inputDatos" placeholder="Escribe los datos aquí..."></textarea>
            <button class="btn" onclick="enviarAuditoria()">Procesar Datos con Precisión</button>

            <div id="errorBox" class="alert-danger" style="display: none;"></div>

            <div id="resultBox" class="result-box">
                <h3 style="margin-top:0; color: #eceff4;" id="resTitulo">✔ RESULTADO</h3>
                <div class="result-grid">
                    <div class="result-row">
                        <div class="result-cell cell-title" id="lblPesoOrigen">Peso Origen Enviado:</div>
                        <div class="result-cell" id="resPeso">0 kg</div>
                    </div>
                    <div class="result-row">
                        <div class="result-cell cell-title">Tiempo Estimado en Ruta:</div>
                        <div class="result-cell" id="resHoras">0 hrs</div>
                    </div>
                    <div class="result-row">
                        <div class="result-cell cell-title" id="lblAnalisis">Dictamen de Pérdida:</div>
                        <div class="result-cell" id="resMerma" style="color: #ebcb8b; font-weight:bold;">0%</div>
                    </div>
                    <div class="result-row">
                        <div class="result-cell cell-title" id="lblPesoDestino">Peso Esperado / Registrado:</div>
                        <div class="result-cell" id="resDestino" style="color: #a3be8c; font-weight:bold; font-size: 16px;">0 kg</div>
                    </div>
                </div>
                <p style="margin-top: 20px; font-size: 14px; color: #ebd4b4; background-color: #4c566a; padding: 15px; border-radius: 4px; line-height: 1.6;" id="resAlerta">
                    Aviso operativo Mecatronix.
                </p>
            </div>
        </div>
    </div>

    <script>
        function enviarAuditoria() {
            const detalles = document.getElementById("inputDatos").value;
            const errorBox = document.getElementById("errorBox");
            const resultBox = document.getElementById("resultBox");
            
            errorBox.style.display = "none";
            resultBox.style.display = "none";

            if(!detalles.trim()) {
                errorBox.innerText = "Por favor, ingresa los datos del flete.";
                errorBox.style.display = "block";
                return;
            }

            fetch("/auditar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ detalles: detalles })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById("resPeso").innerText = data.peso_origen.toLocaleString() + " kg";
                    document.getElementById("resHoras").innerText = data.horas;
                    document.getElementById("resMerma").innerText = data.reporte.porcentaje;
                    
                    const titulo = document.getElementById("resTitulo");
                    const alerta = document.getElementById("resAlerta");
                    const destinoCell = document.getElementById("resDestino");
                    
                    if (data.modo === "predictivo") {
                        titulo.innerText = "PROYECCIÓN PREDICTIVA DE ARRIBO";
                        titulo.style.color = "#ebcb8b";
                        resultBox.style.borderLeftColor = "#ebcb8b";
                        
                        destinoCell.innerHTML = data.reporte.peso_destino.toLocaleString() + " kg <span style='color:#8892b0; font-size:13px;'>(Estimado en base a " + data.reporte.porcentaje_ideal + "%)</span>";
                        
                        alerta.innerHTML = "💡 <strong>RECOMENDACIÓN OPERATIVA PREDICTIVA (" + data.horas + "):</strong><br>" +
                                           "• <strong>Para el Comprador:</strong> Basado en el tiempo exacto de ruta, la merma ideal calculada es del " + data.reporte.porcentaje_ideal + "%, esperando recibir: " + data.reporte.peso_destino.toLocaleString() + " kg.<br>" +
                                           "• <strong>🛑 UMBRAL CRÍTICO AJUSTADO (" + data.reporte.porcentaje_critico + "%):</strong> Si al pesar el camión el registro es **MENOR a " + data.reporte.limite_critico_kg.toLocaleString() + " kg**, detén la descarga inmediatamente. Se superó la tolerancia física permitida para esta distancia y se solicita formalmente una **verificación técnica y calibración de las básculas involucradas**.";
                    } else {
                        titulo.innerText = "✔ AUDITORÍA DE EMBARQUE COMPLETADA";
                        titulo.style.color = "#a3be8c";
                        resultBox.style.borderLeftColor = "#a3be8c";
                        
                        destinoCell.innerHTML = "<span style='color:#a3be8c; font-weight:bold;'>" + data.reporte.peso_destino.toLocaleString() + " kg</span> <span style='color:#eceff4;'>Registrado</span><br>" +
                                                "<span style='color:#8892b0; font-size:14px; font-weight:normal;'>Debió llegar en aprox: " + data.reporte.peso_estimado_ideal.toLocaleString() + " kg (Merma Ideal Precisa: " + data.reporte.porcentaje_ideal + "%)</span>";
                        
                        alerta.innerHTML = data.reporte.conclusion_rapida + "<br><br>" + data.reporte.alerta_mantenimiento;
                    }
                    
                    resultBox.style.display = "block";
                } else {
                    errorBox.innerText = "Error: " + data.mensaje;
                    errorBox.style.display = "block";
                }
            })
            .catch(() => {
                errorBox.innerText = "Error de comunicación con el servidor Mecatronix.";
                errorBox.style.display = "block";
            });
        }
    </script>
</body>
</html>
"""

# =====================================================================
# MATRIZ LOGÍSTICA DE CARRETERAS DE MÉXICO
# =====================================================================
MATRIZ_RUTAS_MEXICO = {
    ("veracruz", "puebla"): 280,
    ("veracruz", "ciudad de mexico"): 400,
    ("veracruz", "cdmx"): 400,
    ("veracruz", "san luis potosi"): 630,
    ("veracruz", "guadalajara"): 930,
    ("coatzacoalcos", "puebla"): 510,
    ("minatitlan", "puebla"): 500,
    ("chiapas", "puebla"): 680,
    ("tuxtla", "puebla"): 680,
    ("arriaga", "tecali"): 420,
    ("tecali", "arriaga"): 420,
    ("tabasco", "veracruz"): 480,
    ("villahermosa", "puebla"): 610,
    ("puebla", "ciudad de mexico"): 130,
    ("puebla", "san luis potosi"): 430,
    ("guadalajara", "monterrey"): 800,
}

def obtener_logistica_inteligente(texto_usuario, km_extraido):
    if km_extraido and km_extraido > 0:
        distancia_km = km_extraido
    else:
        texto_min = texto_usuario.lower()
        distancia_km = 300 
        for (origen, destino), kms in MATRIZ_RUTAS_MEXICO.items():
            if origen in texto_min and destino in texto_min:
                distancia_km = kms
                break
    tiempo_horas = round((distancia_km / 70) * 1.15, 1)
    return distancia_km, tiempo_horas

def interpretar_datos_locales(texto_usuario):
    texto_limpio = texto_usuario.replace(',', '')
    km_match = re.findall(r'(\d+(?:\.\d+)?)\s*(?:km|kilometro|kilómetros|kms)', texto_limpio.lower())
    km_detectado = float(km_match[0]) if km_match else 0.0
    
    todos_los_numeros = [float(n) for n in re.findall(r'\d+(?:\.\d+)?', texto_limpio) if float(n) >= 100]
    pesos = [n for n in todos_los_numeros if n != km_detectado]
    
    if not pesos:
        return None
        
    p1 = pesos[0]
    p2 = pesos[1] if len(pesos) > 1 else 0.0
    
    return {"peso_uno": p1, "peso_dos": p2, "km": km_detectado}

# =====================================================================
# CONTROLADORES SIN CANDADOS (TOTALMENTE ABIERTOS)
# =====================================================================
@app.route("/", methods=["GET"])
def inicio():
    return render_template_string(HTML_LAYOUT)

@app.route("/auditar", methods=["POST"])
def auditar_embarque():
    # Eliminamos cualquier validación de llaves, el pase es directo 🟢
    datos = request.get_json()
    texto_detalles = datos.get("detalles", "")
    
    datos_embarque = interpretar_datos_locales(texto_detalles)
    
    if not datos_embarque:
        return jsonify({"success": False, "mensaje": "No se encontraron números de kilos válidos."})
        
    try:
        p1 = datos_embarque["peso_uno"]
        p2 = datos_embarque["peso_dos"]
        km_detectado = datos_embarque["km"]
        
        distancia_carretera, horas_viaje = obtener_logistica_inteligente(texto_detalles, km_detectado)
        
        h_calc = max(horas_viaje, 1.0)
        porcentaje_ideal = round(1.5 + (1.35 * math.log(h_calc)), 2)
        porcentaje_critico = round(porcentaje_ideal + 1.50, 2)
        
        if p1 > 0 and p2 == 0:
            peso_origen = p1
            peso_destino_estimado = int(peso_origen * (1 - (porcentaje_ideal / 100)))  
            limite_critico_kg = int(peso_origen * (1 - (porcentaje_critico / 100)))       
            
            return jsonify({
                "success": True,
                "modo": "predictivo",
                "peso_origen": int(peso_origen),
                "horas": f"{horas_viaje} hrs ({distancia_carretera} km)",
                "reporte": {
                    "porcentaje": f"📉 Merma Científica Ideal: {porcentaje_ideal}%",
                    "porcentaje_ideal": porcentaje_ideal,
                    "porcentaje_critico": porcentaje_critico,
                    "peso_destino": peso_destino_estimado,
                    "limite_critico_kg": limite_critico_kg
                }
            })
            
        else:
            peso_origen = max(p1, p2)
            peso_destino = min(p1, p2)
            kilos_perdidos = peso_origen - peso_destino
            porcentaje_real = round((kilos_perdidos / peso_origen) * 100, 2)
            
            peso_estimado_ideal = int(peso_origen * (1 - (porcentaje_ideal / 100)))
            
            if porcentaje_real > porcentaje_critico:
                estatus = f"🚨 ALERTA CRÍTICA ({porcentaje_real}%): Supera el límite de la ruta ({porcentaje_critico}%)."
                conclusion_rapida = "<span style='color:#bf616a; font-size:16px; font-weight:bold;'>❌ DICTAMEN OPERATIVO: ¡EMBARQUE RECHAZADO!</span><br><strong>Acción:</strong> No des el visto bueno al flete. Los números están fuera de rango."
                alerta_mantenimiento = f"⚠️ <strong>DESVIACIÓN CRÍTICA DETECTADA:</strong> El viaje de {horas_viaje} hrs debió reportar máximo {porcentaje_critico}% de merma. La pérdida real de {porcentaje_real}% apunta a un problema. Se solicita formalmente **verificación física y calibración técnica en las básculas involucradas**."
            
            elif (porcentaje_ideal - 0.5) <= porcentaje_real <= (porcentaje_ideal + 0.5):
                estatus = f"✅ MERMA AJUSTADA ({porcentaje_real}%): Rango óptimo científico."
                conclusion_rapida = "<span style='color:#a3be8c; font-size:16px; font-weight:bold;'>🟢 DICTAMEN OPERATIVO: EMBARQUE AUTORIZADO</span><br><strong>Acción:</strong> Puedes firmar de conformidad. Los kilos cuadran a la perfección."
                alerta_mantenimiento = "✓ Los valores cuadran perfectamente con la curva biológica del trayecto."
            
            else:
                estatus = f"⚠️ CONTROL DE TOLERANCIA ({porcentaje_real}%): Variación fuera de la curva."
                conclusion_rapida = "<span style='color:#ebcb8b; font-size:16px; font-weight:bold;'>🟡 DICTAMEN OPERATIVO: PROCEDER CON PRECAUCIÓN</span><br><strong>Acción:</strong> El embarque se puede recibir, pero queda bajo observación."
                alerta_mantenimiento = f"• Desviación moderada. El promedio ideal científico para esta ruta es de {porcentaje_ideal}%."
                
            return jsonify({
                "success": True,
                "modo": "auditoria",
                "peso_origen": int(peso_origen),
                "horas": f"{horas_viaje} hrs ({distancia_carretera} km)",
                "reporte": {
                    "porcentaje": estatus,
                    "porcentaje_ideal": porcentaje_ideal,
                    "peso_destino": int(peso_destino),
                    "peso_estimado_ideal": peso_estimado_ideal,
                    "conclusion_rapida": conclusion_rapida,
                    "alerta_mantenimiento": alerta_mantenimiento
                }
            })
            
    except Exception:
        return jsonify({"success": False, "mensaje": "Error al procesar las mermas."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)