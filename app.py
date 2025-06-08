import streamlit as st

st.set_page_config(page_title="Evaluador de Compras", layout="centered")


st.title("¿Debería comprarlo? 🤔")
st.markdown("Una herramienta sencilla para ayudarte a decidir si comprar o no eso que estás pensando. ✅")

# User inputs

product_type = st.radio("¿Estás pensando en comprar un producto o pagar un servicio?", ["Producto", "Servicio"])
product_name = st.text_input("¿Qué estás considerando comprar?")
product_value = st.number_input("¿Cuánto cuesta?", min_value=0)
is_necessity = st.radio("¿Es una necesidad o un deseo?", ["Necesidad", "Deseo"]) == "Necesidad"
    
is_cash_payment = st.radio("Lo piensas pagar al contado o en cuotas?", ["Al contado", "En cuotas"]) == "Al contado"
if not is_cash_payment:
    is_interest_charged = st.radio("¿Las cuotas tienen interés?", ["Sí, con interés", "No, sin interés"]) == "Con interés"
else:
    is_interest_charged = False

is_gift = st.radio("¿Es un regalo para alguien más?", ["Sí", "No"]) == "Sí"
monthly_income = st.number_input("¿Cuál es tu ingreso mensual aproximado?", min_value=1)
weekly_work_hours = st.number_input("¿Cuántas horas trabajas a la semana?", min_value=1)
has_alternative = st.selectbox("¿Existe una alternativa más barata y similar en función?", ["No", "No lo he pensado", "Sí"])
can_wait = st.selectbox("¿Podrías esperar 1 semana antes de comprarlo?", ["Sí", "Tal vez", "No"])
expected_life = st.selectbox("¿Cuánto esperas que dure el producto?", ["Menos de 1 mes", "1 a 6 meses", "6 meses a 1 año", "Más de 1 año"])

submitted = st.button("Evaluar compra")

# Purchase assesment function
def evaluate_purchase(data):
    score = 0

    # 1. % ingreso comprometido
    monthly_income_percentage = (data["costo"] / data["ingreso"]) * 100
    if monthly_income_percentage < 5:
        score += 2
    elif monthly_income_percentage < 10:
        score += 1
    elif monthly_income_percentage <= 20:
        score += 0
    else:
        score -= 1

    # 2. Horas de trabajo
    hourly_income = data["ingreso"] / (data["horas"]*4)
    required_hours_to_pay = data["costo"] / hourly_income
    if required_hours_to_pay < 4:
        score += 3
    elif required_hours_to_pay < 8:
        score += 1
    elif required_hours_to_pay >8:
        score -= 1

    # 3. Necesidad o deseo
    score += 4 if data["necesidad"] else 0

    # 4. Pago contado
    if data["necesidad"] and data["contado"]:
        score += 6
    elif data["necesidad"] and not data["contado"]:
        score += 2
    if not data["necesidad"] and data["contado"]:
        score += 3
    else:
        score -= 6

    # 5. Cuotas sin interés
    if not data["contado"] and data["cuotas"]:
        if not data["interes"]:
            score += 2

    # 6. Alternativa
    if data["alternativa"] == "No":
        score += 1
    elif data["alternativa"] == "Sí":
        score -= 3

    # 7. Puede esperar
    if data["espera"] == "Sí":
        score -= 3
    elif data["espera"] == "No":
        score += 4

    # 8. Durabilidad
    match data["duracion"]:
        case "Más de 1 año":
            score += 3
        case "6 meses a 1 año":
            score += 2
        case "1 a 6 meses":
            score += 1
        case "Menos de 1 mes":
            score -= 1

    # 9. Regla 50/30/20
    limite = data["ingreso"] * (0.5 if data["necesidad"] else 0.3)
    p_subpresupuesto = data["costo"] / limite
    if p_subpresupuesto < 0.10:
        score += 6
    elif p_subpresupuesto < 0.20:
        score += 3
    elif p_subpresupuesto > 0.40:
        score -= 4

    # Interpretación
    if score >= 5:
        return "✅ Comprar con confianza", score, required_hours_to_pay
    elif score >= 2:
        return "🕒 Esperar o reevaluar", score, required_hours_to_pay
    else:
        return "❌ No comprar por ahora", score, required_hours_to_pay

# Resultado
if submitted:
    datos = {
        "tipo": product_type,
        "nombre": product_name,
        "costo": product_value,
        "necesidad": is_necessity,
        "contado": is_cash_payment,
        "cuotas": not(is_cash_payment),
        "interes": is_interest_charged,
        "regalo": is_gift,
        "ingreso": monthly_income,
        "horas": weekly_work_hours,
        "alternativa": has_alternative,
        "espera": can_wait,
        "duracion": expected_life
    }

    st.subheader("📋 Resumen de tu evaluación:")
    st.write(f"- Tipo de compra: {product_type}")
    st.write(f"- Nombre del ítem: {product_name}")
    st.write(f"- Costo: ${product_value:,.0f}")
    st.write(f"- Es una necesidad: {'Sí' if is_necessity else 'No'}")
    st.write(f"- Forma de pago: {'Contado' if is_cash_payment else 'Cuotas'}")
    if not is_cash_payment:
        st.write(f"  - Cuotas con interés: {'Sí' if is_interest_charged else 'No'}")
    st.write(f"- Ingreso mensual: ${monthly_income:,.0f}")
    st.write(f"- Alternativas más baratas: {has_alternative}")
    st.write(f"- Puede esperar 1 semana: {can_wait}")
    st.write(f"- Duración esperada: {expected_life}")

    resultado, score, horas = evaluate_purchase(datos)

    st.subheader("🎯 Recomendación:")
    st.success(f"{resultado} (Puntaje: {score})")
    st.info(f"Esta compra representa aproximadamente {horas:.1f} horas de trabajo.")

