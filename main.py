import streamlit as st
import pandas as pd
import os
import subprocess

# Awaryjna instalacja plotly, jeśli nie jest obecneimport streamlit as st
import pandas as pd
import os
from db import get_connection
import plotly.graph_objects as go

st.set_page_config(page_title="Analiza ryzyka z ISO", layout="wide")
st.title("🔐 Analiza ryzyka z modułami ISO/IEC 27001 i ISO/IEC 9126")

# ------------------- MACIERZ RYZYKA -------------------
def klasyfikuj_ryzyko(poziom):
    if poziom <= 6:
        return "Niskie"
    elif poziom <= 14:
        return "Średnie"
    else:
        return "Wysokie"

default_risks = [
    {"Zagrożenie": "Awaria serwera", "Prawdopodobieństwo": 4, "Wpływ": 5, "Poufność": False, "Dostępność": True},
    {"Zagrożenie": "Atak DDoS", "Prawdopodobieństwo": 3, "Wpływ": 4, "Poufność": False, "Dostępność": True},
    {"Zagrożenie": "Błąd ludzki", "Prawdopodobieństwo": 5, "Wpływ": 3, "Poufność": True, "Dostępność": False},
    {"Zagrożenie": "Utrata zasilania", "Prawdopodobieństwo": 2, "Wpływ": 2, "Poufność": False, "Dostępność": True}
]

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(default_risks)

st.subheader("➕ Dodaj nowe zagrożenie")
with st.form("add_risk_form"):
    name = st.text_input("Opis zagrożenia")
    prob = st.slider("Prawdopodobieństwo", 1, 5, 3)
    impact = st.slider("Wpływ", 1, 5, 3)
    conf = st.checkbox("Narusza poufność?")
    avail = st.checkbox("Narusza dostępność?")
    submitted = st.form_submit_button("Dodaj")
    if submitted and name:
        new_row = {"Zagrożenie": name, "Prawdopodobieństwo": prob, "Wpływ": impact,
                   "Poufność": conf, "Dostępność": avail}
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Zagrożenie dodane.")

st.subheader("✏️ Edytuj macierz ryzyka")
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
st.session_state.df = edited_df.copy()
edited_df["Poziom ryzyka"] = edited_df["Prawdopodobieństwo"] * edited_df["Wpływ"]
edited_df["Klasyfikacja"] = edited_df["Poziom ryzyka"].apply(klasyfikuj_ryzyko)

st.subheader("📋 Filtrowanie")
filt = st.radio("Poziom ryzyka:", ["Wszystkie", "Niskie", "Średnie", "Wysokie"], horizontal=True)
aspects = st.multiselect("Aspekty bezpieczeństwa:", ["Poufność", "Dostępność"])

df_filtered = edited_df
if filt != "Wszystkie":
    df_filtered = df_filtered[df_filtered["Klasyfikacja"] == filt]
if "Poufność" in aspects:
    df_filtered = df_filtered[df_filtered["Poufność"] == True]
if "Dostępność" in aspects:
    df_filtered = df_filtered[df_filtered["Dostępność"] == True]

def koloruj(val):
    if val == "Niskie":
        return "background-color: #d4edda"
    elif val == "Średnie":
        return "background-color: #fff3cd"
    elif val == "Wysokie":
        return "background-color: #f8d7da"
    return ""

st.subheader("📊 Macierz ryzyka")
st.dataframe(df_filtered.style.applymap(koloruj, subset=["Klasyfikacja"]), use_container_width=True)

# ------------------- ISO/IEC 9126 -------------------
st.header("🧪 ISO/IEC 9126 – Ocena jakości systemu")

features = {
    "Funkcjonalność": st.slider("Funkcjonalność", 1, 5, 3),
    "Niezawodność": st.slider("Niezawodność", 1, 5, 3),
    "Użyteczność": st.slider("Użyteczność", 1, 5, 3),
    "Efektywność": st.slider("Efektywność", 1, 5, 3),
    "Przenośność": st.slider("Przenośność", 1, 5, 3)
}

avg = sum(features.values()) / len(features)
interpretacje = []
if features["Niezawodność"] >= 4:
    interpretacje.append("Wysoka niezawodność")
if features["Przenośność"] <= 2:
    interpretacje.append("Niska przenośność")

st.markdown(f"""
📈 **Średnia ocena jakości**: `{avg:.2f}/5`

🗣️ **Interpretacja**: {", ".join(interpretacje) if interpretacje else "Brak istotnych odchyleń"}
""")

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=list(features.values()),
    theta=list(features.keys()),
    fill='toself',
    name='Ocena'
))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[1, 5])), showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ------------------- ISO/IEC 27001 -------------------
st.header("🔐 ISO/IEC 27001 – Ocena kontroli bezpieczeństwa")

obszar = st.selectbox("Wybierz obszar kontroli (Annex A)", ["A.5 – Organizacyjne", "A.6 – Ludzkie", "A.7 – Fizyczne", "A.8 – Techniczne"])

kontrole = {
    "A.5 – Organizacyjne": ["Zarządzanie politykami", "Zarządzanie ryzykiem", "Zarządzanie zgodnością"],
    "A.6 – Ludzkie": ["Szkolenia bezpieczeństwa", "Zarządzanie dostępem pracowników"],
    "A.7 – Fizyczne": ["Kontrola dostępu fizycznego", "Ochrona sprzętu", "Monitoring wizyjny"],
    "A.8 – Techniczne": ["Zarządzanie dostępem", "Szyfrowanie", "Logowanie i monitoring", "Ochrona przed złośliwym oprogramowaniem"]
}

oceny = {}
st.subheader("🛠 Ocena wdrożenia kontroli")
for k in kontrole[obszar]:
    oceny[k] = st.slider(f"{k}", 1, 5, 3)

srednia = sum(oceny.values()) / len(oceny)
kolor = "🟢 Wysoka" if srednia >= 4 else "🟡 Średnia" if srednia >= 2.5 else "🔴 Niska"

st.markdown(f"""
📊 **Średni poziom dojrzałości**: `{srednia:.2f}/5`

🔎 **Ocena**: {kolor}
""")

try:
    import plotly.graph_objects as go
except ModuleNotFoundError:
    subprocess.check_call(["pip", "install", "plotly"])
    import plotly.graph_objects as go

st.set_page_config(page_title="Analiza ryzyka z ISO", layout="wide")
st.title("🔐 Analiza ryzyka z modułami ISO/IEC 27001 i ISO/IEC 9126")

# ------------------- MACIERZ RYZYKA -------------------
def klasyfikuj_ryzyko(poziom):
    if poziom <= 6:
        return "Niskie"
    elif poziom <= 14:
        return "Średnie"
    else:
        return "Wysokie"

default_risks = [
    {"Zagrożenie": "Awaria serwera", "Prawdopodobieństwo": 4, "Wpływ": 5, "Poufność": False, "Dostępność": True},
    {"Zagrożenie": "Atak DDoS", "Prawdopodobieństwo": 3, "Wpływ": 4, "Poufność": False, "Dostępność": True},
    {"Zagrożenie": "Błąd ludzki", "Prawdopodobieństwo": 5, "Wpływ": 3, "Poufność": True, "Dostępność": False},
    {"Zagrożenie": "Utrata zasilania", "Prawdopodobieństwo": 2, "Wpływ": 2, "Poufność": False, "Dostępność": True}
]

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(default_risks)

st.subheader("➕ Dodaj nowe zagrożenie")
with st.form("add_risk_form"):
    name = st.text_input("Opis zagrożenia")
    prob = st.slider("Prawdopodobieństwo", 1, 5, 3)
    impact = st.slider("Wpływ", 1, 5, 3)
    conf = st.checkbox("Narusza poufność?")
    avail = st.checkbox("Narusza dostępność?")
    submitted = st.form_submit_button("Dodaj")
    if submitted and name:
        new_row = {"Zagrożenie": name, "Prawdopodobieństwo": prob, "Wpływ": impact,
                   "Poufność": conf, "Dostępność": avail}
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Zagrożenie dodane.")

st.subheader("✏️ Edytuj macierz ryzyka")
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
st.session_state.df = edited_df.copy()
edited_df["Poziom ryzyka"] = edited_df["Prawdopodobieństwo"] * edited_df["Wpływ"]
edited_df["Klasyfikacja"] = edited_df["Poziom ryzyka"].apply(klasyfikuj_ryzyko)

st.subheader("📋 Filtrowanie")
filt = st.radio("Poziom ryzyka:", ["Wszystkie", "Niskie", "Średnie", "Wysokie"], horizontal=True)
aspects = st.multiselect("Aspekty bezpieczeństwa:", ["Poufność", "Dostępność"])

df_filtered = edited_df
if filt != "Wszystkie":
    df_filtered = df_filtered[df_filtered["Klasyfikacja"] == filt]
if "Poufność" in aspects:
    df_filtered = df_filtered[df_filtered["Poufność"] == True]
if "Dostępność" in aspects:
    df_filtered = df_filtered[df_filtered["Dostępność"] == True]

def koloruj(val):
    if val == "Niskie":
        return "background-color: #d4edda"
    elif val == "Średnie":
        return "background-color: #fff3cd"
    elif val == "Wysokie":
        return "background-color: #f8d7da"
    return ""

st.subheader("📊 Macierz ryzyka")
st.dataframe(df_filtered.style.applymap(koloruj, subset=["Klasyfikacja"]), use_container_width=True)

# ------------------- ISO/IEC 9126 -------------------
st.header("🧪 ISO/IEC 9126 – Ocena jakości systemu")

features = {
    "Funkcjonalność": st.slider("Funkcjonalność", 1, 5, 3),
    "Niezawodność": st.slider("Niezawodność", 1, 5, 3),
    "Użyteczność": st.slider("Użyteczność", 1, 5, 3),
    "Efektywność": st.slider("Efektywność", 1, 5, 3),
    "Przenośność": st.slider("Przenośność", 1, 5, 3)
}

avg = sum(features.values()) / len(features)
interpretacje = []
if features["Niezawodność"] >= 4:
    interpretacje.append("Wysoka niezawodność")
if features["Przenośność"] <= 2:
    interpretacje.append("Niska przenośność")

st.markdown(f"""
📈 **Średnia ocena jakości**: `{avg:.2f}/5`

🗣️ **Interpretacja**: {", ".join(interpretacje) if interpretacje else "Brak istotnych odchyleń"}
""")

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=list(features.values()),
    theta=list(features.keys()),
    fill='toself',
    name='Ocena'
))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[1, 5])), showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ------------------- ISO/IEC 27001 -------------------
st.header("🔐 ISO/IEC 27001 – Ocena kontroli bezpieczeństwa")

obszar = st.selectbox("Wybierz obszar kontroli (Annex A)", ["A.5 – Organizacyjne", "A.6 – Ludzkie", "A.7 – Fizyczne", "A.8 – Techniczne"])

kontrole = {
    "A.5 – Organizacyjne": ["Zarządzanie politykami", "Zarządzanie ryzykiem", "Zarządzanie zgodnością"],
    "A.6 – Ludzkie": ["Szkolenia bezpieczeństwa", "Zarządzanie dostępem pracowników"],
    "A.7 – Fizyczne": ["Kontrola dostępu fizycznego", "Ochrona sprzętu", "Monitoring wizyjny"],
    "A.8 – Techniczne": ["Zarządzanie dostępem", "Szyfrowanie", "Logowanie i monitoring", "Ochrona przed złośliwym oprogramowaniem"]
}

oceny = {}
st.subheader("🛠 Ocena wdrożenia kontroli")
for k in kontrole[obszar]:
    oceny[k] = st.slider(f"{k}", 1, 5, 3)

srednia = sum(oceny.values()) / len(oceny)
kolor = "🟢 Wysoka" if srednia >= 4 else "🟡 Średnia" if srednia >= 2.5 else "🔴 Niska"

st.markdown(f"""
📊 **Średni poziom dojrzałości**: `{srednia:.2f}/5`

🔎 **Ocena**: {kolor}
""")
