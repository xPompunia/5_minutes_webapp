# 5 minutes webapp

Streamlit tool that converts a Polish prayer-book DOCX into a structured XLSX.
It splits the document into daily entries (psalm, gospel, contemplation, prayers)
and generates audio-friendly variants of titles — dates, psalm numbers, and Bible
references are expanded into spoken-form Polish ("rozdział trzeci, werset piąty").

## Running

```bash
pip install -r requirements.txt
streamlit run app.py
```

Upload the DOCX in the browser and download the generated XLSX. The
`5minutes_empty.xlsx` template must sit next to `app.py`.
