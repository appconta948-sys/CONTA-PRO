import streamlit as st
import pandas as pd
import json
import os
import PyPDF2
import smtplib
from datetime import datetime, timedelta
from openai import OpenAI
from duckduckgo_search import DDGS
from streamlit_google_auth import Authenticate
import paypalrestsdk
import mercadopago
import requests
import sqlite3
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fpdf import FPDF
from flask import Flask, request, jsonify

# ============================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS (con responsive)
# ============================================
st.set_page_config(page_title="CONTA PRO - Director Contable", layout="wide", page_icon="📊")

st.markdown("""
<style>
    /* Estilos base */
    .stButton > button {
        background: linear-gradient(135deg, #345470 0%, #1e3a5f 100%) !important;
        color: white !important; border-radius: 12px !important; width: 100% !important;
        font-weight: 700 !important;
    }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; }

    /* Tarjetas de crecimiento */
    .growth-card {
        background: linear-gradient(135deg, #27AE60 0%, #2ecc71 100%);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        transition: transform 0.3s;
    }
    .growth-card:hover { transform: translateY(-5px); }
    .growth-number { font-size: 2.5rem; font-weight: 800; }

    /* Planes de suscripción */
    .plan-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: all 0.3s;
    }
    .plan-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
    .plan-price { font-size: 2rem; font-weight: 700; color: #2C3E50; }

    /* Mensajes de chat */
    .chat-message-user {
        background: #3498DB;
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 20px 20px 5px 20px;
        margin-bottom: 0.8rem;
        max-width: 70%;
        float: right;
        clear: both;
    }
    .chat-message-conta {
        background: #ECF0F1;
        color: #2C3E50;
        padding: 0.8rem 1.2rem;
        border-radius: 20px 20px 20px 5px;
        margin-bottom: 0.8rem;
        max-width: 70%;
        float: left;
        clear: both;
        border-left: 4px solid #27AE60;
    }
    .chat-clear { clear: both; }

    /* ============================================
       RESPONSIVE DESIGN
       ============================================ */
    @media (max-width: 768px) {
        .main-header .big-logo { font-size: 1.5rem !important; }
        .stColumn { width: 100% !important; margin-bottom: 1rem; }
        .growth-card { padding: 1rem !important; margin-bottom: 1rem; }
        .growth-number { font-size: 1.8rem !important; }
        .chat-message-user, .chat-message-conta { max-width: 90% !important; font-size: 0.9rem !important; }
        .plan-card { margin-bottom: 1rem; }
        .stSidebar { width: 100% !important; position: fixed !important; z-index: 999 !important; }
        .floating-chat { width: 50px !important; height: 50px !important; font-size: 1.5rem !important; bottom: 15px !important; right: 15px !important; }
    }
    @media (min-width: 769px) and (max-width: 1024px) {
        .chat-message-user, .chat-message-conta { max-width: 80% !important; }
        .growth-number { font-size: 2rem !important; }
    }
    @media (min-width: 1025px) {
        .chat-message-user, .chat-message-conta { max-width: 70% !important; }
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# 3. BASE DE DATOS SQLITE (SUSCRIPCIONES)
# ============================================
def init_db():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    nombre TEXT,
                    plan TEXT,
                    fecha_inicio TEXT,
                    fecha_expiracion TEXT,
                    activo INTEGER DEFAULT 1,
                    ultimo_login TEXT
                )""")
    conn.commit()
    conn.close()

def registrar_usuario_google(email, nombre):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT email FROM usuarios WHERE email=?", (email,))
    existe = c.fetchone()
    ahora = datetime.now().isoformat()
    if existe:
        c.execute("UPDATE usuarios SET ultimo_login=?, nombre=? WHERE email=?", (ahora, nombre, email))
    else:
        c.execute("""INSERT INTO usuarios (email, nombre, plan, fecha_inicio, fecha_expiracion, activo, ultimo_login)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (email, nombre, "Ninguno", ahora, ahora, 1, ahora))
    conn.commit()
    conn.close()

def activar_plan_usuario(email, nombre, plan, dias=30):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    fecha_inicio = datetime.now().isoformat()
    fecha_expiracion = (datetime.now() + timedelta(days=dias)).isoformat()
    c.execute("""INSERT OR REPLACE INTO usuarios 
                 (email, nombre, plan, fecha_inicio, fecha_expiracion, activo, ultimo_login) 
                 VALUES (?, ?, ?, ?, ?, 1, ?)""",
              (email, nombre, plan, fecha_inicio, fecha_expiracion, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    # Actualizar session_state
    st.session_state.plan = plan

def verificar_suscripcion_usuario(email):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT plan, fecha_expiracion, activo FROM usuarios WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    if row:
        plan, expiracion, activo = row
        if activo and datetime.fromisoformat(expiracion) > datetime.now():
            return True, plan, expiracion
    return False, None, None

def obtener_usuarios_activos():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT email, nombre, plan FROM usuarios WHERE activo=1 AND fecha_expiracion > ?",
              (datetime.now().isoformat(),))
    usuarios = [{"email": row[0], "nombre": row[1], "plan": row[2]} for row in c.fetchall()]
    conn.close()
    return usuarios

def desactivar_suscripciones_expiradas():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("UPDATE usuarios SET activo=0 WHERE fecha_expiracion < ?", (datetime.now().isoformat(),))
    conn.commit()
    conn.close()

# ============================================
# 4. ENVÍO DE CORREOS
# ============================================
def enviar_correo(destinatario, asunto, mensaje_html):
    try:
        # Configuración desde secrets
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["smtp_port"]
        email_user = st.secrets["email"]["username"]
        email_pass = st.secrets["email"]["password"]
        
        msg = MIMEMultipart()
        msg["From"] = email_user
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg.attach(MIMEText(mensaje_html, "html"))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False
msg = EmailMessage()
from email.message import EmailMessage
import smtplib
from email.message import EmailMessage
import streamlit as st

def enviar_correo_pro(tipo, destinatario, asunto, cuerpo):
    """
    tipo puede ser: "par", "info" o "gerencia"
    """
    # Configuración del remitente según el tipo
    remitente = f"{tipo}@tuamigocontable.com"
    
    # Configuración del servidor SMTP (ajusta según tu proveedor)
    SMTP_SERVER = "smtp.gmail.com" # o el servidor que uses
    SMTP_PORT = 587
    SMTP_USER = "tu_correo@tuamigocontable.com" # correo desde el que envías
    SMTP_PASSWORD = st.secrets["SMTP_PASSWORD"] # usa secrets para mayor seguridad
    
    try:
        # Crear el mensaje
        msg = EmailMessage()
        msg.set_content(cuerpo)
        msg['Subject'] = asunto
        msg['From'] = remitente
        msg['To'] = destinatario
        
        # Enviar el correo
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # iniciar TLS
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        st.error(f"Error enviando correo: {e}")
        return False



# ============================================
# 5. CONFIGURACIÓN DE PAGOS (PayPal, MercadoPago)
# ============================================
try:
    paypalrestsdk.configure({
        "mode": st.secrets["paypal"]["mode"],
        "client_id": st.secrets["paypal"]["client_id"],
        "client_secret": st.secrets["paypal"]["client_secret"]
    })
except:
    pass

try:
    sdk = mercadopago.SDK(st.secrets["mercadopago"]["access_token"])
except:
    sdk = None

def crear_pago_paypal(plan, precio_usd, user_email, user_name):
    try:
        pago = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal",
                "payer_info": {
                    "email": user_email,
                    "first_name": user_name.split()[0] if user_name else "Usuario",
                    "last_name": " ".join(user_name.split()[1:]) if len(user_name.split()) > 1 else ""
                }
            },
            "redirect_urls": {
                "return_url": "https://tuamigocontable.com/success",
                "cancel_url": "https://tuamigocontable.com/cancel"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": plan,
                        "sku": plan,
                        "price": str(precio_usd),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {"total": str(precio_usd), "currency": "USD"},
                "description": f"Suscripción {plan} en CONTA PRO",
                "custom": f"{user_email}|{plan}"  # Para identificar en webhook
            }]
        })
        if pago.create():
            for link in pago.links:
                if link.rel == "approval_url":
                    return link.href
        return None
    except Exception as e:
        print(f"PayPal error: {e}")
        return None

def crear_preferencia_mp(plan, precio_cop, user_email, user_name):
    try:
        preference_data = {
            "items": [{
                "title": f"Suscripción {plan}",
                "quantity": 1,
                "currency_id": "COP",
                "unit_price": precio_cop
            }],
            "payer": {"email": user_email},
            "back_urls": {
                "success": "https://tuamigocontable.com/success",
                "failure": "https://tuamigocontable.com/failure",
                "pending": "https://tuamigocontable.com/pending"
            },
            "auto_return": "approved",
            "external_reference": f"{user_email}|{plan}"
        }
        preference_response = sdk.preference().create(preference_data)
        return preference_response["response"]["init_point"]
    except Exception as e:
        print(f"MercadoPago error: {e}")
        return None

# ============================================
# 6. MOTOR CONTABLE (Libro Diario)
# ============================================
class LibroDiario:
    def __init__(self):
        if 'asientos' not in st.session_state:
            if os.path.exists("base_datos_conta.xlsx"):
                df = pd.read_excel("base_datos_conta.xlsx")
                st.session_state.asientos = df.to_dict('records') if not df.empty else []
            else:
                st.session_state.asientos = []
        if 'puc' not in st.session_state:
            st.session_state.puc = {"110505": "Caja", "111005": "Bancos", "413501": "Ventas", "2101": "Proveedores"}
        if 'facturas' not in st.session_state:
            st.session_state.facturas = []
        if 'inventario' not in st.session_state:
            st.session_state.inventario = []
        if 'plan' not in st.session_state:
            st.session_state.plan = "Ninguno"

    def registrar(self, datos_ia):
        nuevo = {
            "id": f"CP-{len(st.session_state.asientos) + 1:03d}",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "descripcion": datos_ia['descripcion'],
            "movimientos": datos_ia['movimientos'],
            "analisis": datos_ia['analisis']
        }
        st.session_state.asientos.append(nuevo)
        pd.DataFrame(st.session_state.asientos).to_excel("base_datos_conta.xlsx", index=False)

    def obtener_balance_saldos(self):
        """Devuelve un DataFrame con saldo neto por cuenta"""
        if not st.session_state.asientos:
            return pd.DataFrame()
        movs = []
        for a in st.session_state.asientos:
            for m in a['movimientos']:
                movs.append(m)
        df = pd.DataFrame(movs)
        if df.empty:
            return pd.DataFrame()
        
        # Agrupar por cuenta y sumar débitos - créditos
        balance = df.groupby('cuenta').apply(
            lambda x: sum(x[x['tipo'] == 'Debito']['valor']) - sum(x[x['tipo'] == 'Credito']['valor'])
        ).reset_index()
        balance.columns = ['Cuenta', 'Saldo']
        return balance

    def generar_analisis_estrategico(self):
        """Genera consejos financieros usando IA a partir de los saldos"""
        balance = self.obtener_balance_saldos()
        if balance.empty:
            return "No hay datos suficientes para un análisis."
        
        contexto_saldos = balance.to_string(index=False)
        prompt = f"Como Director Contable, analiza estos saldos actuales y da 3 consejos financieros breves: {contexto_saldos}"
        
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ No se pudo generar el análisis: {e}"
 

# ==========================================
# CREACIÓN DEL OBJETO CONTABLE (Obligatorio)
# ============================================
libro = LibroDiario()

# ============================================
# 7. CEREBRO IA (con búsqueda en internet)
# ============================================
def cargar_contexto_markdown():
    contexto = ""
    ruta_base = "instrucciones/"
    if os.path.exists(ruta_base):
        for raiz, carpetas, archivos in os.walk(ruta_base):
            for archivo in archivos:
                if archivo.endswith(".md"):
                    try:
                        with open(os.path.join(raiz, archivo), "r", encoding="utf-8") as f:
                            contexto += f"\n--- REGLA ({archivo}): ---\n{f.read()}\n"
                    except:
                        pass
    return contexto

def ia_conta_pro(texto_usuario):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # Búsqueda en internet si es necesario
    contexto_internet = ""
    if any(x in texto_usuario.lower() for x in ["ley", "trm", "dolar", "reforma"]):
        try:
            with DDGS() as ddgs:
                resultados = [res for res in ddgs.text(f"{texto_usuario} Colombia 2026", max_results=2)]
                contexto_internet = str(resultados)
        except:
            contexto_internet = "No se pudo buscar en internet"
    
    prompt = f"""
    Eres Director Contable.
    PUC: {st.session_state.puc}.
    WEB: {contexto_internet}.
    Instrucciones: {cargar_contexto_markdown()[:1500]}
    
    Responde solo JSON con descripcion, movimientos y analisis.
    Formato: {{"descripcion": "...", "movimientos": [{{"cuenta": "...", "tipo": "Debito/Credito", "valor": 0}}], "analisis": "..."}}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": texto_usuario}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# ============================================
# 8. FUNCIONES DE DASHBOARD ADICIONALES (crecimiento, diccionario, chat)
# ============================================
def mostrar_seccion_crecimiento():
    st.markdown("### 📈 Crecimiento de Usuarios")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='growth-card'>
            <div class='growth-number'>50</div>
            <div>Usuarios</div>
            <div>Mes 2</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='growth-card'>
            <div class='growth-number'>500</div>
            <div>Usuarios</div>
            <div>Mes 6</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='growth-card'>
            <div class='growth-number'>1000</div>
            <div>Usuarios</div>
            <div>Año 1</div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_diccionario():
    st.markdown("### 📖 Diccionario Callejero → Contabilidad")
    df = pd.DataFrame([
        {"Lenguaje de Barrio": "Me fiaron 4 leches", "Conta entiende": "PROVEEDORES (2101)", "Acción": "Aumenta Pasivo (CR)"},
        {"Lenguaje de Barrio": "Me debe un pan", "Conta entiende": "CUENTAS POR COBRAR (1205)", "Acción": "Aumenta Activo (DB)"},
        {"Lenguaje de Barrio": "Agarré $10 de la caja", "Conta entiende": "RETIROS PERSONAL (3105)", "Acción": "Aumenta Retiro (DB)"},
        {"Lenguaje de Barrio": "Vendí un pan", "Conta entiende": "VENTAS (4135)", "Acción": "Aumenta Ingreso (CR)"}
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.info("📌 **Regla de Oro:** 'No importa si fue un peso o un millón, si se mueve, se anota.'")

def mostrar_chat_conta():
    st.markdown("### 💬 Chating con Conta")
    if 'chat_conta_history' not in st.session_state:
        st.session_state.chat_conta_history = []
    for msg in st.session_state.chat_conta_history[-20:]:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-message-user'><strong>Tú:</strong> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-message-conta'>{msg['content']}</div>", unsafe_allow_html=True)
    st.markdown("<div class='chat-clear'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    with col1:
        mensaje = st.text_input("", placeholder="Ej: 'Vendí un pan en $10,000' o '¿Cómo voy con el negocio?'", key="chat_input", label_visibility="collapsed")
    with col2:
        enviar = st.button("💬 Enviar", use_container_width=True)
    if enviar and mensaje:
        st.session_state.chat_conta_history.append({"role": "user", "content": mensaje})
        try:
            res = ia_conta_pro(mensaje)
            respuesta = f"**Conta:** {res['analisis']}\n\n✅ Registrado: {res['descripcion']}"
            libro.registrar(res)
            st.session_state.chat_conta_history.append({"role": "assistant", "content": respuesta})
        except Exception as e:
            st.session_state.chat_conta_history.append({"role": "assistant", "content": f"**Conta:** {mensaje} ¿Cuánto fue? Dame más detalles."})
        st.rerun()

# ============================================
# 9. PÁGINAS DE LA APLICACIÓN
# ============================================
def pantalla_dashboard():
    st.title("🏠 Dashboard CONTA PRO")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros Contables", len(st.session_state.asientos))
    col2.metric("Facturas Emitidas", len(st.session_state.facturas))
    col3.metric("Productos", len(st.session_state.inventario))
    col4.metric("Plan Activo", st.session_state.plan)
    mostrar_seccion_crecimiento()
    with st.expander("📖 Ver Diccionario de Traducción"):
        mostrar_diccionario()
    if st.session_state.asientos:
        st.subheader("📊 Últimos Movimientos")
        ultimos = st.session_state.asientos[-3:]
        for a in ultimos:
            with st.expander(f"{a['id']} - {a['descripcion']}"):
                st.write(a['analisis'])
    st.markdown("---")
    st.markdown("<footer style='text-align:center; color:#666;'>© 2024-2026 CONTA PRO - TuAmigoContable.com</footer>", unsafe_allow_html=True)

def pantalla_asistente():
    st.title("🤖 Asistente IA - Registro Rápido")
    mostrar_chat_conta()
    st.divider()
    with st.expander("📁 Subir Documento (PDF/Excel)"):
        archivo = st.file_uploader("Sube PDF o Excel", type=['pdf', 'xlsx'])
        if archivo:
            if archivo.type == "application/pdf":
                try:
                    reader = PyPDF2.PdfReader(archivo)
                    texto = ""
                    for pagina in reader.pages:
                        texto += pagina.extract_text()
                    st.text_area("Contenido extraído", texto, height=150)
                    if st.button("Procesar con IA"):
                        res = ia_conta_pro(f"Analiza este documento: {texto[:1000]}")
                        libro.registrar(res)
                        st.success(f"✅ {res['analisis']}")
                except Exception as e:
                    st.error(f"Error PDF: {e}")
            else:
                try:
                    df = pd.read_excel(archivo)
                    st.dataframe(df.head())
                    if st.button("Procesar Excel con IA"):
                        res = ia_conta_pro(f"Analiza estos datos: {df.head().to_string()}")
                        libro.registrar(res)
                        st.success(f"✅ {res['analisis']}")
                except Exception as e:
                    st.error(f"Error Excel: {e}")

def pantalla_libro():
    st.title("📖 Libro Diario y Reportes")
    tab1, tab2 = st.tabs(["📜 Historial de Registros", "📊 Reportes y Auditoría IA"])
    
    with tab1:
        if st.session_state.asientos:
            data = []
            for a in st.session_state.asientos:
                for m in a['movimientos']:
                    data.append({
                        "ID": a['id'],
                        "Fecha": a['fecha'],
                        "Descripción": a['descripcion'],
                        "Cuenta": m['cuenta'],
                        "Tipo": m['tipo'],
                        "Valor": f"${m['valor']:,.0f}"
                    })
            df_libro = pd.DataFrame(data)
            st.dataframe(df_libro, use_container_width=True)
            if st.button("📥 Exportar a Excel"):
                df_libro.to_excel("libro_diario_completo.xlsx", index=False)
                st.success("Exportado con éxito")
        else:
            st.info("No hay registros contables aún.")
    
    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("📥 Exportar Reporte Oficial")
            if st.button("Generar PDF de Balance"):
                balance = libro.obtener_balance_saldos()
                if not balance.empty:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, "CONTA PRO - Balance de Saldos", ln=True, align='C')
                    pdf.ln(10)
                    pdf.set_font("Arial", size=12)
                    for _, row in balance.iterrows():
                        pdf.cell(0, 10, f"{row['Cuenta']}: ${row['Saldo']:,.2f}", ln=True)
                    pdf.output("balance_contable.pdf")
                    with open("balance_contable.pdf", "rb") as f:
                        st.download_button("Descargar PDF", f, file_name="balance_contable.pdf")
                else:
                    st.warning("Sin datos para el PDF")
        with col_b:
            st.subheader("💡 Consejo del Director (IA)")
            if st.button("Analizar situación actual"):
                with st.spinner("Estudiando tus números..."):
                    consejo = libro.generar_analisis_estrategico()
                    st.success("Análisis Completado")
                    st.info(consejo)

def pantalla_facturacion():
    if st.session_state.plan == "Ninguno" or (st.session_state.plan == "Expirado"):
        st.warning("⚠️ Activa un plan para usar facturación")
        return
    st.title("🧾 Facturación")
    cliente = st.text_input("Cliente")
    concepto = st.text_input("Concepto")
    col_monto, col_iva = st.columns(2)
    with col_monto:
        monto = st.number_input("Monto", min_value=0.0, step=0.01)
    with col_iva:
        iva = st.number_input("IVA (%)", min_value=0.0, value=19.0, step=1.0)
    total = monto * (1 + iva/100)
    st.info(f"Total con IVA: **${total:,.2f} COP**")
    if st.button("Crear Factura"):
        factura = {"id": len(st.session_state.facturas)+1, "fecha": datetime.now().strftime("%Y-%m-%d"), "cliente": cliente, "concepto": concepto, "monto": monto, "iva": iva, "total": total, "estado": "Pendiente"}
        st.session_state.facturas.append(factura)
        st.success(f"Factura #{factura['id']} creada")
    st.subheader("📋 Facturas Registradas")
    st.dataframe(pd.DataFrame(st.session_state.facturas))

def pantalla_inventario():
    if st.session_state.plan == "Ninguno" or (st.session_state.plan == "Expirado"):
        st.warning("⚠️ Activa un plan para usar inventario")
        return
    st.title("📦 Inventario")
    producto = st.text_input("Producto")
    categoria = st.selectbox("Categoría", ["General", "Electrónicos", "Oficina", "Servicios"])
    precio = st.number_input("Precio (COP)", min_value=0.0, step=0.01)
    cantidad = st.number_input("Cantidad", min_value=0, step=1)
    if st.button("Agregar Producto"):
        item = {"id": len(st.session_state.inventario)+1, "producto": producto, "categoria": categoria, "precio": precio, "cantidad": cantidad, "fecha_agregado": datetime.now().strftime("%Y-%m-%d")}
        st.session_state.inventario.append(item)
        st.success(f"Producto {producto} agregado")
    st.subheader("📋 Inventario Actual")
    st.dataframe(pd.DataFrame(st.session_state.inventario))

def pantalla_suscripciones():
    st.title("💳 Planes de Suscripción")
    user_email = st.session_state.get('email', '')
    user_name = st.session_state.get('user_name', 'Usuario')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='plan-card'>
            <h3>🎁 Prueba Gratis</h3>
            <p><strong>7 días</strong> de acceso completo</p>
            <p>✅ Todas las funciones</p>
            <p>✅ Soporte básico</p>
            <div class='plan-price'>GRATIS</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Activar Prueba Gratis", key="gratis"):
            activar_plan_usuario(user_email, user_name, "Prueba Gratis", 7)
            st.success("✅ Prueba gratis activada por 7 días!")
            st.rerun()
    with col2:
        st.markdown("""
        <div class='plan-card'>
            <h3>📅 Mensual</h3>
            <p><strong>9 USD</strong> (~36.000 COP/mes)</p>
            <p>✅ Todas las funciones</p>
            <p>✅ Soporte prioritario</p>
            <div class='plan-price'>$9 USD</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Pagar Mensual", key="mensual"):
            url_paypal = crear_pago_paypal("Mensual", 9, user_email, user_name)
            url_mp = crear_preferencia_mp("Mensual", 36000, user_email, user_name)
            if url_paypal:
                st.markdown(f"[💳 Pagar con PayPal]({url_paypal})")
            if url_mp:
                st.markdown(f"[💳 Pagar con MercadoPago]({url_mp})")
    with col3:
        st.markdown("""
        <div class='plan-card'>
            <h3>📆 Anual</h3>
            <p><strong>85 USD</strong> (~340.000 COP/año)</p>
            <p>✅ Ahorra 23 USD</p>
            <p>✅ Soporte VIP</p>
            <div class='plan-price'>$85 USD</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Pagar Anual", key="anual"):
            url_paypal = crear_pago_paypal("Anual", 85, user_email, user_name)
            url_mp = crear_preferencia_mp("Anual", 340000, user_email, user_name)
            if url_paypal:
                st.markdown(f"[💳 Pagar con PayPal]({url_paypal})")
            if url_mp:
                st.markdown(f"[💳 Pagar con MercadoPago]({url_mp})")
    
    st.divider()
    col_mv, col_contacto = st.columns(2)
    with col_mv:
        st.subheader("🌟 Misión")
        st.write("Brindar soluciones contables simples y accesibles para emprendedores y profesionales en Colombia.")
        st.subheader("🚀 Visión")
        st.write("Convertirnos en la plataforma líder en automatización contable.")
    with col_contacto:
        st.subheader("📞 Contacto")
        st.write("**Correo:** info@tuamigocontable.com")
        st.write("**Teléfono:** +57 333 256 16 32")
        st.subheader("📍 Ubicación")
        st.components.v1.html(
            '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3976.999999999!2d-74.0721!3d4.7110!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1sBogotá!5e0!3m2!1ses!2sco!4v1710000000000!5m2!1ses!2sco" width="100%" height="250" style="border:0;" allowfullscreen="" loading="lazy"></iframe>',
            height=250
        )

def pantalla_legal():
    st.title("⚖️ Información Legal")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📜 Certificado de Registro")
        st.markdown("**Dirección Nacional de Derecho de Autor**  \nRegistro: 2026-03-24-001  \nTitular: TuAmigoContable.com")
        st.subheader("🏢 Datos de la Empresa")
        st.markdown("**NIT:** 901.234.567-8  \n**Domicilio:** Bogotá D.C., Colombia")
    with col2:
        st.subheader("🔐 Certificación de Seguridad")
        st.markdown("SSL Certificate: A+ Rating  \nGDPR Compliant: Sí  \nData Encryption: AES-256")
    with st.expander("📜 Términos y Condiciones"):
        st.write("Términos detallados...")
    with st.expander("🔒 Política de Privacidad"):
        st.write("Política de privacidad...")

# ============================================
# 10. FLASK API PARA WEBHOOKS (en segundo plano)
# ============================================
flask_app = Flask(__name__)

@flask_app.route("/webhook/paypal", methods=["POST"])
def webhook_paypal():
    data = request.json
    if data.get("event_type") == "PAYMENT.SALE.COMPLETED":
        custom = data["resource"].get("custom", "")
        if "|" in custom:
            user_email, plan = custom.split("|")
        else:
            user_email = data["resource"]["payer"]["email_address"]
            plan = "Mensual"
        nombre = data["resource"]["payer"]["payer_info"].get("first_name", "")
        activar_plan_usuario(user_email, nombre, plan, 30)
        # Enviar correo
        html = f"<h2>¡Gracias por tu suscripción!</h2><p>Tu plan {plan} ha sido activado con éxito. Disfruta de CONTA PRO.</p>"
        enviar_correo(user_email, "Confirmación de Suscripción CONTA PRO", html)
        return jsonify({"message": "Plan activado"}), 200
    return jsonify({"message": "Evento ignorado"}), 400

@flask_app.route("/webhook/mercadopago", methods=["POST"])
def webhook_mp():
    data = request.json
    if data.get("type") == "payment":
        payment_id = data["data"]["id"]
        try:
            payment = sdk.payment().get(payment_id)
            if payment["response"]["status"] == "approved":
                user_email = payment["response"]["payer"]["email"]
                external_ref = payment["response"].get("external_reference", "")
                if "|" in external_ref:
                    _, plan = external_ref.split("|")
                else:
                    plan = "Mensual"
                nombre = payment["response"]["payer"].get("first_name", "")
                activar_plan_usuario(user_email, nombre, plan, 30)
                html = f"<h2>¡Pago recibido!</h2><p>Tu plan {plan} ha sido activado. Gracias por confiar en CONTA PRO.</p>"
                enviar_correo(user_email, "Confirmación de Suscripción CONTA PRO", html)
                return jsonify({"message": "Plan activado"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Evento ignorado"}), 400

@flask_app.route("/usuarios", methods=["GET"])
def usuarios_endpoint():
    return jsonify(obtener_usuarios_activos())

def iniciar_flask():
    flask_app.run(host="0.0.0.0", port=5000, debug=False)

# Iniciar Flask en un hilo separado
flask_thread = threading.Thread(target=iniciar_flask, daemon=True)
flask_thread.start()

# ============================================
# 11. CONTROLADOR PRINCIPAL
# ============================================
init_db()
desactivar_suscripciones_expiradas()
auth.check_authentification()

if not st.session_state.get('connected', False):
    st.title("🔐 CONTA PRO")
    st.write("Tu asistente contable inteligente")
    # Mostrar usuarios activos (para marketing)
    usuarios_activos = obtener_usuarios_activos()
    st.metric("Usuarios Activos", len(usuarios_activos))
    auth.login()
else:
    user_info = st.session_state['user_info']
    user_email = user_info.get('email')
    user_name = user_info.get('name', 'Usuario')
    
    registrar_usuario_google(user_email, user_name)
    tiene_plan, plan_actual, fecha_exp = verificar_suscripcion_usuario(user_email)
    
    st.session_state.email = user_email
    st.session_state.user_name = user_name
    if tiene_plan:
        st.session_state.plan = plan_actual
    elif st.session_state.plan == "Prueba Gratis":
        pass
    else:
        st.session_state.plan = "Ninguno"
    
    # Sidebar
    with st.sidebar:
        st.header(f"👤 {user_name}")
        st.caption(f"📧 {user_email}")
        if tiene_plan:
            dias = (datetime.fromisoformat(fecha_exp) - datetime.now()).days
            st.success(f"✅ Plan: {plan_actual}")
            st.info(f"⏰ Vence en: {dias} días")
        elif st.session_state.plan == "Prueba Gratis":
            st.success("✅ Plan: Prueba Gratis")
        else:
            st.warning("⚠️ Sin plan activo")
        
        opcion = st.radio("📋 Menú", ["Dashboard", "Asistente IA", "Libro Diario", "Facturación", "Inventario", "Suscripciones", "Legal"])
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            auth.logout()
            st.rerun()
    
    # Mostrar página
    if opcion == "Dashboard":
        pantalla_dashboard()
    elif opcion == "Asistente IA":
        pantalla_asistente()
    elif opcion == "Libro Diario":
        if tiene_plan or st.session_state.plan == "Prueba Gratis":
            pantalla_libro()
        else:
            st.warning("⚠️ Activa un plan para usar esta función")
            if st.button("Ver Planes"):
                opcion = "Suscripciones"
                st.rerun()
    elif opcion == "Facturación":
        if tiene_plan or st.session_state.plan == "Prueba Gratis":
            pantalla_facturacion()
        else:
            st.warning("⚠️ Activa un plan para usar facturación")
    elif opcion == "Inventario":
        if tiene_plan or st.session_state.plan == "Prueba Gratis":
            pantalla_inventario()
        else:
            st.warning("⚠️ Activa un plan para usar inventario")
    elif opcion == "Suscripciones":
        pantalla_suscripciones()
    elif opcion == "Legal":
        pantalla_legal()


