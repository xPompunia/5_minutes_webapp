import streamlit as st
import pandas as pd
import io
import datetime
from processor import parse_docx_to_excel

# Edit styles
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .css-1gdpby3 {border: 2px dashed #d33682;} 
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Page config
st.set_page_config(page_title="Generator Modlitewnika", page_icon="📖", layout="centered")

st.title("Generator Modlitewnika")
st.markdown("Wrzuć plik DOCX, a otrzymasz gotowy plik XLSX.")

# Sidebar with settings
with st.sidebar:
    st.header("⚙️ Ustawienia")
    current_year = datetime.date.today().year
    target_year = st.text_input("Rok dla dat", value=str(current_year))

# Drag & Drop
uploaded_file = st.file_uploader("Przeciągnij plik Modlitewnika (.docx)", type="docx")

if uploaded_file is not None:
    # st.spinner for loading effect
    with st.spinner("Przetwarzanie dokumentu, proszę czekać..."):
        try:
            final_dataframe = parse_docx_to_excel(uploaded_file, "5minutes_empty.xlsx", target_year)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_dataframe.to_excel(writer, index=False)
            output.seek(0)

            st.success("✅ Udało się! Twój plik jest gotowy.")

            original_name = uploaded_file.name.replace(".docx", "")
            output_name = f"{original_name}_gotowy.xlsx"

            st.download_button(
                label="⬇️ Pobierz wygenerowany plik Excel",
                data=output,
                file_name=output_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Wystąpił błąd: {str(e)}")
            st.warning("Upewnij się, że plik '5minutes_empty.xlsx' jest na serwerze obok app.py.")