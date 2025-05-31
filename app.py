import streamlit as st

st.set_page_config(page_title="Evaluador de Compras", layout="centered")

st.title("¿Debería comprarlo?")
st.markdown("Una herramienta sencilla para ayudarte a decidir si comprar o no eso que estás pensando.")

# Formulario
with st.form("evaluador_form"):
    tipo = st.radio("¿Estás pensando en comprar un producto o pagar un servicio?", ["Producto", "Servicio"])
    nombre = st.text_input("¿Qué estás considerando comprar?")
    costo = st.number_input("¿Cuánto cuesta?", min_value=0)
    es_necesidad = st.radio("¿Es una necesidad o un deseo?", ["Necesidad", "Deseo"]) == "Necesidad"
    pago_contado = st.radio("Lo piensas pagar al contado o en cuotas?", ["Sí", "No"]) == "Sí"
    
    usa_cuotas = False
    cuotas_con_interes = False
    if not pago_contado:
        usa_cuotas = st.radio("¿Puedes pagarlo en cuotas?", ["Sí", "No"]) == "Sí"
        if usa_cuotas:
            cuotas_con_interes = st.radio("¿Las cuotas tienen interés?", ["Sí, con interés", "No, sin interés"]) == "Con interés"

    es_regalo = st.radio("¿Es un regalo para alguien más?", ["Sí", "No"]) == "Sí"
    ingreso_mensual = st.number_input("¿Cuál es tu ingreso mensual aproximado?", min_value=1)
    horas_mensuales = st.number_input("¿Cuántas horas trabajas a la semana?", min_value=1)
    alternativa = st.selectbox("¿Existe una alternativa más barata y similar en función?", ["No", "No lo he pensado", "Sí"])
    puede_esperar = st.selectbox("¿Podrías esperar 1 semana antes de comprarlo?", ["Sí", "Tal vez", "No"])
    duracion = st.selectbox("¿Cuánto esperas que dure el producto?", ["Menos de 1 mes", "1 a 6 meses", "6 meses a 1 año", "Más de 1 año"])

    submitted = st.form_submit_button("Evaluar compra")

# Función de evaluación
def evaluar(data):
    puntaje = 0

    # 1. % ingreso comprometido
    porcentaje_ingreso = (data["costo"] / data["ingreso"]) * 100
    if porcentaje_ingreso < 5:
        puntaje += 2
    elif porcentaje_ingreso < 10:
        puntaje += 1
    elif porcentaje_ingreso <= 20:
        puntaje += 0
    else:
        puntaje -= 1

    # 2. Horas de trabajo
    valor_hora = data["ingreso"] / data["horas"]
    horas_trabajo = data["costo"] / valor_hora
    if horas_trabajo < 5:
        puntaje += 2
    elif horas_trabajo < 10:
        puntaje += 1
    elif horas_trabajo > 20:
        puntaje -= 1

    # 3. Necesidad o deseo
    puntaje += 2 if data["necesidad"] else 0

    # 4. Pago contado
    puntaje += 2 if data["contado"] else 0

    # 5. Cuotas sin interés
    if not data["contado"] and data["cuotas"]:
        if not data["interes"]:
            puntaje += 1

    # 6. Alternativa
    if data["alternativa"] == "no":
        puntaje += 1
    elif data["alternativa"] == "si":
        puntaje -= 1

    # 7. Puede esperar
    if data["espera"] == "si":
        puntaje += 1
    elif data["espera"] == "no":
        puntaje -= 1

    # 8. Durabilidad
    match data["duracion"]:
        case ">1_año":
            puntaje += 2
        case "6-12_meses":
            puntaje += 1
        case "<1_mes":
            puntaje -= 1

    # 9. Regla 50/30/20
    limite = data["ingreso"] * (0.5 if data["necesidad"] else 0.3)
    p_subpresupuesto = data["costo"] / limite
    if p_subpresupuesto < 0.10:
        puntaje += 2
    elif p_subpresupuesto < 0.20:
        puntaje += 1
    elif p_subpresupuesto > 0.40:
        puntaje -= 1

    # Interpretación
    if puntaje >= 9:
        return "✅ Comprar con confianza", puntaje, horas_trabajo
    elif puntaje >= 6:
        return "🕒 Esperar o reevaluar", puntaje, horas_trabajo
    else:
        return "❌ No comprar por ahora", puntaje, horas_trabajo

# Resultado
if submitted:
    datos = {
        "tipo": tipo,
        "nombre": nombre,
        "costo": costo,
        "necesidad": es_necesidad,
        "contado": pago_contado,
        "cuotas": usa_cuotas,
        "interes": cuotas_con_interes,
        "regalo": es_regalo,
        "ingreso": ingreso_mensual,
        "horas": horas_mensuales,
        "alternativa": alternativa,
        "espera": puede_esperar,
        "duracion": duracion
    }

    st.subheader("📋 Resumen de tu evaluación:")
    st.write(f"- Tipo de compra: {tipo}")
    st.write(f"- Nombre del ítem: {nombre}")
    st.write(f"- Costo: ${costo:,.0f}")
    st.write(f"- Es una necesidad: {'Sí' if es_necesidad else 'No'}")
    st.write(f"- Forma de pago: {'Contado' if pago_contado else 'Cuotas'}")
    if not pago_contado:
        st.write(f"  - Cuotas con interés: {'Sí' if cuotas_con_interes else 'No'}")
    st.write(f"- Ingreso mensual: ${ingreso_mensual:,.0f}")
    st.write(f"- Alternativas más baratas: {alternativa}")
    st.write(f"- Puede esperar 1 semana: {puede_esperar}")
    st.write(f"- Duración esperada: {duracion}")

    resultado, puntaje, horas = evaluar(datos)

    st.subheader("🎯 Recomendación:")
    st.success(f"{resultado} (Puntaje: {puntaje})")
    st.info(f"Esta compra representa aproximadamente {horas:.1f} horas de trabajo.")
