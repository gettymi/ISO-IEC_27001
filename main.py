import streamlit as st
import pandas as pd

# Konfiguracja strony
st.set_page_config(page_title="Analiza ryzyka", layout="wide")
st.title("🔐 Analiza ryzyka systemów teleinformatycznych zgodna z ISO/IEC 27001 i ISO 9126")

# Klasyfikacja ryzyka
def klasyfikuj_ryzyko(poziom):
    if poziom <= 6:
        return "Niskie"
    elif poziom <= 14:
        return "Średnie"
    else:
        return "Wysokie"

# Domyślne dane
default_risks = [
    {"Zagrożenie": "Awaria serwera", "Prawdopodobieństwo": 4, "Wpływ": 5, "Poufność": False, "Dostępność": True},
    {"Zagrożenie": "Atak DDoS", "Prawdopodobieństwo": 3, "Wpływ": 4, "Poufność": False, "Dostępność": True},
    {"Zagrożenie": "Błąd ludzki", "Prawdopodobieństwo": 5, "Wpływ": 3, "Poufność": True, "Dostępność": False},
    {"Zagrożenie": "Utrata zasilania", "Prawdopodobieństwo": 2, "Wpływ": 2, "Poufność": False, "Dostępność": True}
]

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(default_risks)

# ➕ Formularz dodawania nowego zagrożenia
st.subheader("➕ Dodaj nowe zagrożenie")
with st.form("add_risk_form"):
    name = st.text_input("Opis zagrożenia")
    prob = st.slider("Prawdopodobieństwo (1-5)", 1, 5, 3)
    impact = st.slider("Wpływ (1-5)", 1, 5, 3)
    confidentiality = st.checkbox("Czy narusza poufność?")
    availability = st.checkbox("Czy narusza dostępność?")
    submitted = st.form_submit_button("Dodaj")

    if submitted and name.strip() != "":
        new_row = {
            "Zagrożenie": name,
            "Prawdopodobieństwo": prob,
            "Wpływ": impact,
            "Poufność": confidentiality,
            "Dostępność": availability
        }
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Zagrożenie dodane.")

# ✏️ Edycja danych
st.subheader("✏️ Edytuj macierz ryzyka")
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    key="risk_editor"
)

st.session_state.df = edited_df.copy()

# Obliczenia
edited_df["Poziom ryzyka"] = edited_df["Prawdopodobieństwo"] * edited_df["Wpływ"]
edited_df["Klasyfikacja"] = edited_df["Poziom ryzyka"].apply(klasyfikuj_ryzyko)

# 📋 Filtrowanie według poziomu ryzyka
st.subheader("📋 Filtruj według poziomu ryzyka")
filt = st.radio("Pokaż:", ["Wszystkie", "Niskie", "Średnie", "Wysokie"], horizontal=True)

df_filtered = edited_df
if filt != "Wszystkie":
    df_filtered = df_filtered[df_filtered["Klasyfikacja"] == filt]

# 🔍 Filtr wg aspektów ISO/IEC 27001
st.subheader("🔍 Filtruj według aspektów ISO/IEC 27001")
aspects = st.multiselect("Pokaż zagrożenia wpływające na:", ["Poufność", "Dostępność"])
if "Poufność" in aspects:
    df_filtered = df_filtered[df_filtered["Poufność"] == True]
if "Dostępność" in aspects:
    df_filtered = df_filtered[df_filtered["Dostępność"] == True]

# 🧪 Ocena wg ISO 9126
st.subheader("🧪 Ocena jakości systemu wg ISO 9126")
funkcjonalnosc = st.slider("Funkcjonalność (1 - niska, 5 - wysoka)", 1, 5, 3)
niezawodnosc = st.slider("Niezawodność (1 - niska, 5 - wysoka)", 1, 5, 3)
st.markdown(f"""
📌 **Ocena jakości systemu:**

- **Funkcjonalność**: {funkcjonalnosc}/5  
- **Niezawodność**: {niezawodnosc}/5
""")

# 🎨 Kolorowanie tabeli
def koloruj(val):
    if val == "Niskie":
        return "background-color: #d4edda"
    elif val == "Średnie":
        return "background-color: #fff3cd"
    elif val == "Wysokie":
        return "background-color: #f8d7da"
    return ""

# 📊 Tabela końcowa
st.subheader("📊 Macierz ryzyka")
st.dataframe(
    df_filtered.style.applymap(koloruj, subset=["Klasyfikacja"]),
    use_container_width=True
)
