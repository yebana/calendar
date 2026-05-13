import calendar
import hashlib
import html
import json
import os
from datetime import date, datetime
from typing import Dict, List, Set

import pandas as pd
import streamlit as st


DB_FILE = "calendario_estados.json"
PASSWORD_HASH = "4e3192d7e42580fda0f10ca2c5d113093ad9efdb342b9fcb9d4dcfa06752f6af"

MESES = [
    "Enero",
    "Febrero", 
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]

DIAS_SEMANA_CORTOS = ["L", "M", "X", "J", "V", "S", "D"]

FESTIVOS_MADRID = {
    (1, 1): "Año Nuevo",
    (1, 6): "Epifanía del Señor",
    (4, 2): "Jueves Santo",
    (4, 3): "Viernes Santo",
    (5, 1): "Fiesta del Trabajo",
    (5, 2): "Fiesta de la Comunidad de Madrid",
    (8, 15): "Asunción de la Virgen",
    (10, 12): "Fiesta Nacional de España",
    (11, 2): "Traslado de Todos los Santos",
    (12, 7): "Traslado Día de la Constitución",
    (12, 8): "Día de la Inmaculada Concepción",
    (12, 25): "Natividad del Señor",
    (5, 15): "San Isidro Labrador",
    (11, 9): "Nuestra Señora de La Almudena",
}

ESTADOS = [
    "Vacaciones 2025",
    "Vacaciones 2026",
    "Asuntos Propios",
    "Remanente",
    "Comida",
]

ICONOS_ESTADOS = {
    "Vacaciones 2025": "🧳",
    "Vacaciones 2026": "🏖️",
    "Asuntos Propios": "📝",
    "Remanente": "♻️",
    "Comida": "🍽️",
}

COLORES_ESTADOS = {
    "Vacaciones 2025": "#2563eb",
    "Vacaciones 2026": "#0f766e",
    "Asuntos Propios": "#b45309",
    "Remanente": "#7c3aed",
    "Comida": "#be123c",
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def aplicar_estilos():
    st.markdown(
        """
        <style>
        :root {
            --line: #d9e2ec;
            --muted: #64748b;
            --ink: #172033;
            --panel: #f8fafc;
            --soft-blue: #e7f0ff;
            --soft-yellow: #fff7d6;
            --soft-green: #e8f7ee;
        }

        .block-container {
            padding-top: 1.3rem;
            padding-bottom: 2.5rem;
            max-width: 1440px;
        }

        h1, h2, h3 {
            letter-spacing: 0;
        }

        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
        }

        div[data-testid="stMetricLabel"] {
            color: var(--muted);
        }

        div[data-testid="stButton"] > button {
            height: 3rem !important;
            min-height: 3rem !important;
            max-height: 3rem !important;
            border-radius: 7px;
            border: 1px solid var(--line);
            font-weight: 650;
            box-shadow: none;
            transition: border-color 120ms ease, background 120ms ease, transform 120ms ease;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0.5rem !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            line-height: 1 !important;
        }

        /* Forzar altura específica para botones en columnas del calendario */
        div[data-testid="stVerticalBlock"] div[data-testid="element-container"] div[data-testid="column"] div[data-testid="stButton"] > button {
            height: 3rem !important;
            min-height: 3rem !important;
            max-height: 3rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0.5rem !important;
            margin: 0 !important;
        }

        /* Estilo para botones de fin de semana */
        .weekend-button {
            color: red !important;
            font-weight: bold !important;
        }

        div[data-testid="stButton"] > button:hover {
            border-color: #93b4dc;
            background: #f4f8ff;
            transform: translateY(-1px);
        }

        .hero {
            background: linear-gradient(135deg, #f8fafc 0%, #eef7f1 52%, #fff7d6 100%);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1.15rem 1.25rem;
            margin-bottom: 1rem;
        }

        .hero-title {
            margin: 0;
            color: var(--ink);
            font-size: clamp(1.75rem, 3vw, 2.65rem);
            font-weight: 800;
        }

        .hero-subtitle {
            margin: 0.35rem 0 0;
            color: var(--muted);
            font-size: 1rem;
        }

        .month-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: white;
            padding: 0.65rem;
            margin-bottom: 1rem;
        }

        .month-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.45rem;
            background-color: #fff7ed;
            border: 1px solid #fed7aa;
            border-radius: 7px;
            padding: 0.5rem 0.75rem;
        }

        .month-title strong {
            color: var(--ink);
            font-size: 1rem;
        }

        .month-count {
            color: var(--muted);
            font-size: 0.78rem;
        }

        .weekday {
            color: var(--muted);
            text-align: center;
            font-size: 0.72rem;
            font-weight: 800;
            padding-bottom: 0.15rem;
        }

        .empty-day {
            height: 3rem !important;
            min-height: 3rem !important;
            max-height: 3rem !important;
            border-radius: 7px;
            background: #f8fafc;
            border: 1px dashed #e2e8f0;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .selected-day {
            outline: 2px solid #2563eb;
            outline-offset: 2px;
            border-radius: 8px;
        }

        .day-note {
            color: var(--muted);
            font-size: 0.76rem;
            line-height: 1.25;
            min-height: 1.9rem;
            margin-top: -0.15rem;
            margin-bottom: 0.25rem;
            text-align: center;
        }

        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin: 0.4rem 0 0.1rem;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            border-radius: 999px;
            border: 1px solid var(--line);
            padding: 0.15rem 0.5rem;
            color: var(--ink);
            background: #ffffff;
            font-size: 0.78rem;
            font-weight: 650;
        }

        .selection-panel {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            padding: 1rem;
            margin-top: 0.6rem;
        }

        .hint {
            color: var(--muted);
            font-size: 0.92rem;
        }

        .legend-dot {
            display: inline-block;
            width: 0.72rem;
            height: 0.72rem;
            border-radius: 999px;
            margin-right: 0.35rem;
            vertical-align: -0.05rem;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def check_password() -> bool:
    def password_entered():
        if hash_password(st.session_state["password"]) == PASSWORD_HASH:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.markdown(
        """
        <div class="hero">
            <p class="hero-title">Calendario de estados</p>
            <p class="hero-subtitle">Accede para gestionar vacaciones, festivos y días marcados.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.text_input("Contraseña", type="password", on_change=password_entered, key="password")

    if "password_correct" in st.session_state:
        st.error("Contraseña incorrecta")

    return False


def cargar_estados() -> Dict[str, Set[str]]:
    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        st.error(f"No se pudieron cargar los datos: {e}")
        return {}

    estados = {k: set(v) for k, v in datos.items()}
    migrado = False
    for valores in estados.values():
        if "Vacaciones" in valores:
            valores.remove("Vacaciones")
            valores.add("Vacaciones 2025")
            migrado = True

    if migrado:
        guardar_estados(estados)

    return estados


def guardar_estados(estados: Dict[str, Set[str]]):
    try:
        datos_serializables = {k: sorted(v) for k, v in estados.items()}
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(datos_serializables, f, ensure_ascii=False, indent=2)
    except IOError as e:
        st.error(f"No se pudieron guardar los datos: {e}")


def inicializar_estado():
    if "estados_dias" not in st.session_state:
        st.session_state.estados_dias = cargar_estados()
    if "mes_actual" not in st.session_state:
        st.session_state.mes_actual = datetime.now().month
    if "ano_actual" not in st.session_state:
        st.session_state.ano_actual = datetime.now().year
    if "dias_seleccionados_anual" not in st.session_state:
        st.session_state.dias_seleccionados_anual = set()


def obtener_festivos_mes(ano: int, mes: int) -> Dict[int, str]:
    return {
        dia: nombre
        for (mes_festivo, dia), nombre in FESTIVOS_MADRID.items()
        if mes_festivo == mes
    }


def obtener_dias_mes(ano: int, mes: int) -> int:
    return calendar.monthrange(ano, mes)[1]


def es_fin_de_semana(ano: int, mes: int, dia: int) -> bool:
    return date(ano, mes, dia).weekday() >= 5


def toggle_estado_dia(ano: int, mes: int, dia: int, estado: str):
    clave_dia = f"{ano}-{mes:02d}-{dia:02d}"
    st.session_state.estados_dias.setdefault(clave_dia, set())

    if estado in st.session_state.estados_dias[clave_dia]:
        st.session_state.estados_dias[clave_dia].remove(estado)
        if not st.session_state.estados_dias[clave_dia]:
            del st.session_state.estados_dias[clave_dia]
    else:
        st.session_state.estados_dias[clave_dia].add(estado)

    guardar_estados(st.session_state.estados_dias)


def aplicar_estado_a_seleccion(claves: List[str], estado: str):
    todos_tienen_estado = all(
        estado in st.session_state.estados_dias.get(clave, set()) for clave in claves
    )

    for clave in claves:
        ano, mes, dia = [int(parte) for parte in clave.split("-")]
        if todos_tienen_estado:
            if estado in st.session_state.estados_dias.get(clave, set()):
                st.session_state.estados_dias[clave].remove(estado)
                if not st.session_state.estados_dias[clave]:
                    del st.session_state.estados_dias[clave]
        else:
            st.session_state.estados_dias.setdefault(clave, set()).add(estado)

    guardar_estados(st.session_state.estados_dias)


def limpiar_estados_seleccion(claves: List[str]):
    for clave in claves:
        st.session_state.estados_dias.pop(clave, None)
    guardar_estados(st.session_state.estados_dias)


def obtener_resumen_mes(ano: int, mes: int) -> Dict[str, int]:
    resumen = {estado: 0 for estado in ESTADOS}
    for dia in range(1, obtener_dias_mes(ano, mes) + 1):
        clave_dia = f"{ano}-{mes:02d}-{dia:02d}"
        for estado in st.session_state.estados_dias.get(clave_dia, set()):
            if estado in resumen:
                resumen[estado] += 1
    return resumen


def obtener_totales_anuales(ano: int) -> Dict[str, int]:
    totales = {estado: 0 for estado in ESTADOS}
    for mes in range(1, 13):
        resumen = obtener_resumen_mes(ano, mes)
        for estado, valor in resumen.items():
            totales[estado] += valor
    return totales


def contar_festivos_laborables(ano: int) -> int:
    total = 0
    for mes in range(1, 13):
        for dia in obtener_festivos_mes(ano, mes):
            if not es_fin_de_semana(ano, mes, dia):
                total += 1
    return total


def etiqueta_dia(ano: int, mes: int, dia: int) -> str:
    clave_dia = f"{ano}-{mes:02d}-{dia:02d}"
    estados = st.session_state.estados_dias.get(clave_dia, set())
    iconos = "".join(ICONOS_ESTADOS[estado] for estado in ESTADOS if estado in estados)
    seleccionado = clave_dia in st.session_state.dias_seleccionados_anual

    if dia in obtener_festivos_mes(ano, mes):
        prefijo = "★"
    else:
        prefijo = ""

    marca = "✓ " if seleccionado else ""
    
    # Los días festivos no muestran emoji adicional, solo el prefijo ★
    # No añadir iconos para días festivos sin estados
    
    return f"{marca}{prefijo}{dia} {iconos}".strip()


def texto_ayuda_dia(ano: int, mes: int, dia: int) -> str:
    clave_dia = f"{ano}-{mes:02d}-{dia:02d}"
    partes = [date(ano, mes, dia).strftime("%d/%m/%Y")]
    festivo = obtener_festivos_mes(ano, mes).get(dia)
    if festivo:
        partes.append(festivo)
    estados = st.session_state.estados_dias.get(clave_dia, set())
    if estados:
        partes.append(", ".join(sorted(estados)))
    return " · ".join(partes)


def render_pills_resumen(resumen: Dict[str, int]):
    partes = []
    for estado in ESTADOS:
        valor = resumen.get(estado, 0)
        if valor:
            color = COLORES_ESTADOS[estado]
            icono = ICONOS_ESTADOS[estado]
            partes.append(
                f'<span class="pill" style="border-color:{color}33;">'
                f'<span style="color:{color};">{icono}</span>{valor}</span>'
            )

    if not partes:
        partes.append('<span class="pill">Sin estados</span>')

    st.markdown(f'<div class="pill-row">{"".join(partes)}</div>', unsafe_allow_html=True)


def seleccionar_dia(clave_dia: str, seleccion_multiple: bool):
    seleccionados = set(st.session_state.dias_seleccionados_anual)
    if seleccion_multiple:
        if clave_dia in seleccionados:
            seleccionados.remove(clave_dia)
        else:
            seleccionados.add(clave_dia)
    else:
        seleccionados = {clave_dia}
    st.session_state.dias_seleccionados_anual = seleccionados


def mostrar_mes(ano: int, mes: int, seleccion_multiple: bool):
    resumen = obtener_resumen_mes(ano, mes)
    festivos = obtener_festivos_mes(ano, mes)

    # No aplicar estilos globales, se harán individualmente para cada botón de fin de semana

    st.markdown(
        f"""
        <div class="month-card">
            <div class="month-title">
                <strong>{MESES[mes - 1]}</strong>
                <span class="month-count">{sum(resumen.values())} marcas</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    header_cols = st.columns(7, gap="small")
    for col, dia_semana in zip(header_cols, DIAS_SEMANA_CORTOS):
        col.markdown(f'<div class="weekday">{dia_semana}</div>', unsafe_allow_html=True)

    for semana in calendar.monthcalendar(ano, mes):
        cols = st.columns(7, gap="small")
        for indice, dia in enumerate(semana):
            with cols[indice]:
                if dia == 0:
                    st.markdown('<div class="empty-day"></div>', unsafe_allow_html=True)
                    continue

                clave_dia = f"{ano}-{mes:02d}-{dia:02d}"
                
                # Determinar si es fin de semana
                es_fin_de_semana_flag = indice >= 5  # Sábado (5) o Domingo (6)
                if st.button(
                    etiqueta_dia(ano, mes, dia),
                    key=f"day_{clave_dia}",
                    help=texto_ayuda_dia(ano, mes, dia),
                    width='stretch',
                ):
                    seleccionar_dia(clave_dia, seleccion_multiple)
                    st.rerun()

    render_pills_resumen(resumen)


def mostrar_panel_seleccion():
    seleccionados = sorted(st.session_state.dias_seleccionados_anual)

    st.markdown('<div class="selection-panel"><strong>Edición rápida</strong></div>', unsafe_allow_html=True)
    st.subheader("Días seleccionados")

    if not seleccionados:
        st.markdown(
            '<p class="hint">Pulsa un día del calendario para seleccionarlo. Activa la selección múltiple para editar varios días a la vez.</p>',
            unsafe_allow_html=True,
        )
        return

    st.write(f"{len(seleccionados)} día(s): {', '.join(seleccionados)}")

    if len(seleccionados) == 1:
        clave = seleccionados[0]
        ano, mes, dia = [int(parte) for parte in clave.split("-")]
        festivo = obtener_festivos_mes(ano, mes).get(dia)
        estados_actuales = st.session_state.estados_dias.get(clave, set())
        if festivo:
            st.info(f"Festivo: {festivo}")
        if estados_actuales:
            st.write("Estados actuales: " + ", ".join(sorted(estados_actuales)))
        else:
            st.write("Sin estados marcados.")

    st.write("Aplicar o quitar estado")
    cols = st.columns(3)
    for indice, estado in enumerate(ESTADOS):
        todos_tienen_estado = all(
            estado in st.session_state.estados_dias.get(clave, set()) for clave in seleccionados
        )
        etiqueta = f"{ICONOS_ESTADOS[estado]} {estado}"
        if todos_tienen_estado:
            etiqueta += " ✓"
        with cols[indice % 3]:
            if st.button(etiqueta, key=f"estado_{estado}", width='stretch'):
                aplicar_estado_a_seleccion(seleccionados, estado)
                st.rerun()

    accion_cols = st.columns(2)
    with accion_cols[0]:
        if st.button("Limpiar selección", width='stretch'):
            st.session_state.dias_seleccionados_anual = set()
            st.rerun()
    with accion_cols[1]:
        if st.button("Borrar estados de estos días", width='stretch'):
            limpiar_estados_seleccion(seleccionados)
            st.rerun()


def mostrar_resumen_anual(ano: int):
    filas = []
    for mes in range(1, 13):
        resumen_mes = obtener_resumen_mes(ano, mes)
        fila = {"Mes": MESES[mes - 1], **resumen_mes}
        filas.append(fila)

    df_resumen = pd.DataFrame(filas)
    totales = {"Mes": "TOTAL"}
    for estado in ESTADOS:
        totales[estado] = int(df_resumen[estado].sum())
    df_resumen = pd.concat([df_resumen, pd.DataFrame([totales])], ignore_index=True)

    st.subheader("Resumen anual")
    st.dataframe(df_resumen, hide_index=True, width='stretch')


def mostrar_sidebar():
    st.sidebar.header("Opciones")
    seleccion_multiple = st.sidebar.checkbox(
        "Selección múltiple",
        key="seleccion_multiple_anual",
        help="Permite acumular varios días antes de aplicar un estado.",
    )

    st.sidebar.markdown("### Leyenda")
    st.sidebar.write("★ Festivo")
    for estado in ESTADOS:
        color = COLORES_ESTADOS[estado]
        icono = ICONOS_ESTADOS[estado]
        st.sidebar.markdown(
            f'<span class="legend-dot" style="background:{color};"></span>{icono} {estado}',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar sesión", width='stretch'):
        st.session_state["password_correct"] = False
        st.rerun()

    if st.sidebar.button("Limpiar todos los estados", width='stretch'):
        st.session_state.estados_dias = {}
        st.session_state.dias_seleccionados_anual = set()
        guardar_estados({})
        st.rerun()

    st.sidebar.markdown("---")
    if os.path.exists(DB_FILE):
        try:
            tamano = os.path.getsize(DB_FILE)
            st.sidebar.caption(f"Datos guardados en {DB_FILE} · {tamano} bytes")
        except OSError:
            st.sidebar.caption(f"Datos guardados en {DB_FILE}")
    else:
        st.sidebar.caption("Aún no hay archivo de datos.")

    return seleccion_multiple


def mostrar_vista_anual_solo_lectura():
    """Muestra el calendario anual de solo lectura sin botones clickeables"""
    ano = st.number_input(
        "Año",
        min_value=2020,
        max_value=2035,
        value=st.session_state.ano_actual,
        step=1,
    )

    totales = obtener_totales_anuales(ano)
    total_marcados = sum(totales.values())
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Días marcados", total_marcados)
    col2.metric("Festivos laborables", contar_festivos_laborables(ano))
    col3.metric("Vacaciones 2026", totales["Vacaciones 2026"])
    col4.metric("Asuntos propios", totales["Asuntos Propios"])

    st.markdown("### Calendario anual (vista de solo lectura)")

    for inicio in range(1, 13, 2):
        columnas = st.columns(2)
        for offset, col in enumerate(columnas):
            mes = inicio + offset
            with col:
                mostrar_mes_solo_lectura(ano, mes)

    mostrar_resumen_anual(ano)


def mostrar_mes_solo_lectura(ano: int, mes: int):
    """Muestra un mes en modo solo lectura (sin botones)"""
    resumen = obtener_resumen_mes(ano, mes)
    festivos = obtener_festivos_mes(ano, mes)

    st.markdown(
        f"""
        <div class="month-card">
            <div class="month-title">
                <strong>{MESES[mes - 1]}</strong>
                <span class="month-count">{sum(resumen.values())} marcas</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cabecera días de la semana
    header_cols = st.columns(7, gap="small")
    for col, dia_semana in zip(header_cols, DIAS_SEMANA_CORTOS):
        col.markdown(f'<div class="weekday">{dia_semana}</div>', unsafe_allow_html=True)

    # Días del mes (solo visualización)
    for semana in calendar.monthcalendar(ano, mes):
        cols = st.columns(7, gap="small")
        for indice, dia in enumerate(semana):
            with cols[indice]:
                if dia == 0:
                    st.markdown('<div class="empty-day"></div>', unsafe_allow_html=True)
                    continue

                clave_dia = f"{ano}-{mes:02d}-{dia:02d}"
                
                # Determinar si es fin de semana para aplicar estilo
                es_fin_de_semana_flag = indice >= 5
                
                # Mostrar día como texto (no botón)
                texto_dia = etiqueta_dia(ano, mes, dia)
                texto_ayuda = texto_ayuda_dia(ano, mes, dia)
                
                # Determinar si es festivo
                es_festivo = dia in obtener_festivos_mes(ano, mes)
                
                # Aplicar estilo según tipo de día
                if es_fin_de_semana_flag:
                    # Fin de semana
                    st.markdown(f"""
                    <div style="
                        background-color: #fff7ed;
                        border: 1px solid #fed7aa;
                        color: red;
                        font-weight: bold;
                        padding: 0.5rem;
                        text-align: center;
                        border-radius: 7px;
                        height: 3rem;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 2px;
                        cursor: help;
                    " title="{texto_ayuda}">
                        {texto_dia}
                    </div>
                    """, unsafe_allow_html=True)
                elif es_festivo:
                    # Día festivo (rojo y negrita)
                    st.markdown(f"""
                    <div style="
                        background-color: white;
                        border: 1px solid var(--line);
                        color: red;
                        font-weight: bold;
                        padding: 0.5rem;
                        text-align: center;
                        border-radius: 7px;
                        height: 3rem;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 2px;
                        cursor: help;
                    " title="{texto_ayuda}">
                        {texto_dia}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Día normal
                    st.markdown(f"""
                    <div style="
                        background-color: white;
                        border: 1px solid var(--line);
                        padding: 0.5rem;
                        text-align: center;
                        border-radius: 7px;
                        height: 3rem;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 2px;
                        cursor: help;
                    " title="{texto_ayuda}">
                        {texto_dia}
                    </div>
                    """, unsafe_allow_html=True)

    render_pills_resumen(resumen)


def mostrar_vista_mensual_edicion():
    """Muestra un mes específico con botones de edición y panel de selección"""
    # Obtener mes y año actuales por defecto
    if "mes_edicion" not in st.session_state:
        st.session_state.mes_edicion = datetime.now().month
    if "ano_edicion" not in st.session_state:
        st.session_state.ano_edicion = datetime.now().year

    # Selectores de mes y año
    col1, col2 = st.columns(2)
    with col1:
        mes = st.selectbox(
            "Mes",
            range(1, 13),
            format_func=lambda x: MESES[x-1],
            index=st.session_state.mes_edicion - 1,
            key="mes_select"
        )
        st.session_state.mes_edicion = mes
    with col2:
        ano = st.number_input(
            "Año",
            min_value=2020,
            max_value=2035,
            value=st.session_state.ano_edicion,
            step=1,
            key="ano_input"
        )
        st.session_state.ano_edicion = ano

    # Mostrar panel de selección
    mostrar_panel_seleccion()

    # Mostrar mes con edición
    seleccion_multiple = st.session_state.get("seleccion_multiple_anual", False)
    mostrar_mes(ano, mes, seleccion_multiple)


def mostrar_vista_calendario_anual():
    ano = st.number_input(
        "Año",
        min_value=2020,
        max_value=2035,
        value=st.session_state.ano_actual,
        step=1,
    )

    totales = obtener_totales_anuales(ano)
    total_marcados = sum(totales.values())
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Días marcados", total_marcados)
    col2.metric("Festivos laborables", contar_festivos_laborables(ano))
    col3.metric("Vacaciones 2026", totales["Vacaciones 2026"])
    col4.metric("Asuntos propios", totales["Asuntos Propios"])

    seleccion_multiple = st.session_state.get("seleccion_multiple_anual", False)
    st.markdown("### Calendario anual")
    
    # Mostrar panel de selección junto al calendario (se mueve verticalmente)
    mostrar_panel_seleccion()
    
    for inicio in range(1, 13, 3):
        columnas = st.columns(3)
        for offset, col in enumerate(columnas):
            mes = inicio + offset
            with col:
                mostrar_mes(ano, mes, seleccion_multiple)
    
    mostrar_resumen_anual(ano)


def main():
    st.set_page_config(
        page_title="Calendario de estados",
        page_icon="📅",
        layout="wide",
    )
    aplicar_estilos()

    if not check_password():
        return

    inicializar_estado()
    mostrar_sidebar()

    # Navegación entre vistas
    st.markdown(
        """
        <div class="hero">
            <p class="hero-title">Calendario de estados</p>
            <p class="hero-subtitle">Gestiona vacaciones, asuntos propios, comidas y festivos de Madrid.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Selector de vista
    col1, col2 = st.columns(2)
    with col1:
        vista = st.radio(
            "Selecciona vista:",
            ["Vista Anual (Solo Lectura)", "Vista Mensual (Edición)"],
            key="vista_selector"
        )
    
    # Mostrar vista seleccionada
    if vista == "Vista Anual (Solo Lectura)":
        mostrar_vista_anual_solo_lectura()
    else:
        mostrar_vista_mensual_edicion()


if __name__ == "__main__":
    main()
