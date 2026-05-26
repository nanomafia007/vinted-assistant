import streamlit as st
from PIL import Image, ImageEnhance
import openai
import base64
from io import BytesIO

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Vinted AI Assistant", page_icon="🛍️", layout="centered")

st.title("🛍️ Vinted AI Assistant")
st.write("Carica la foto del tuo capo, migliorala e lascia che l'IA crei l'annuncio perfetto per te.")

# --- Configurazione Chiave API ---
# Permette di inserire la chiave OpenAI nella barra laterale o di leggerla dai Secrets di Streamlit una volta online
api_key = st.sidebar.text_input("Inserisci la tua OpenAI API Key", type="password")
if not api_key and "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]

# --- 1. CARICAMENTO IMMAGINE ---
uploaded_file = st.file_uploader("Scegli la foto del capo d'abbigliamento", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Apriamo l'immagine originale
    image = Image.open(uploaded_file)
    
    st.subheader("🔧 Strumenti di Miglioramento")
    
    # Creiamo tre colonne per i controlli di editing
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rotazione = st.slider("Raddrizza / Ruota (Gradi)", -180, 180, 0, step=90)
    with col2:
        luminosita = st.slider("Luminosità", 0.5, 2.0, 1.0, step=0.1)
    with col3:
        contrasto = st.slider("Contrasto", 0.5, 2.0, 1.0, step=0.1)
        
    # Applicazione dei miglioramenti grafici
    # 1. Rotazione (per addrizzare foto storte)
    if rotazione != 0:
        image = image.rotate(-rotazione, expand=True)
        
    # 2. Luminosità (per ravvivare i colori ed eliminare ombre di pieghe soft)
    enhancer_lum = ImageEnhance.Brightness(image)
    image = enhancer_lum.enhance(luminosita)
    
    # 3. Contrasto (per dare profondità al tessuto)
    enhancer_con = ImageEnhance.Contrast(image)
    image = enhancer_con.enhance(contrasto)
    
    # Mostra l'immagine modificata all'utente
    st.image(image, caption="Foto ottimizzata pronta per Vinted", use_column_width=True)
    
    # --- 2. GENERAZIONE ANNUNCIO CON IA ---
    st.subheader("🤖 Generatore Annuncio")
    
    if st.button("Genera Titolo, Descrizione e Prezzo ✨"):
        if not api_key:
            st.error("Per favore, inserisci la tua OpenAI API Key nella barra laterale per continuare.")
        else:
            with st.spinner("L'IA sta analizzando il tuo capo e studiando il mercato..."):
                try:
                    # Convertiamo l'immagine modificata in Base64 per inviarla a GPT-4o
                    buffered = BytesIO()
                    # Convertiamo in RGB se l'immagine è in formato RGBA (es. PNG trasparenti)
                    if image.mode in ("RGBA", "P"):
                        image = image.convert("RGB")
                    image.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    
                    # Inizializziamo il client OpenAI
                    client = openai.OpenAI(api_key=api_key)
                    
                    # Definiamo le istruzioni per l'IA (Prompt Engineering)
                    prompt_testo = (
                        "Analizza attentamente questa foto di un capo d'abbigliamento destinato alla vendita su Vinted. "
                        "Fornisci un output strutturato esattamente in questo modo:\n\n"
                        "### 🎯 TITOLO ACCATTIVANTE\n"
                        "(Scrivi un titolo di massimo 40 caratteri ottimizzato per la ricerca su Vinted, includendo marca, stile o colore principale ed emoji. Es: 'Felpa Nike Vintage Blu M ✨')\n\n"
                        "### 📝 DESCIZIONE PERSUASIVA\n"
                        "(Scrivi una descrizione dettagliata, onesta e accattivante in italiano. Includi lo stile (es. streetwear, y2k, minimal), "
                        "consigli su come abbinarlo, lo stato visibile del capo, invoglia all'acquisto rapido e aggiungi hashtag pertinenti.)\n\n"
                        "### 💰 PREZZO CONSIGLIATO\n"
                        "(Suggerisci un prezzo di vendita realistico per Vinted basato sul brand e sul tipo di capo, specificando una strategia di vendita veloce.)"
                    )
                    
                    # Chiamata API a GPT-4o (modello con capacità visive)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_testo},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{img_str}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=600
                    )
                    
                    # Mostriamo il risultato finale sul sito
                    risultato = response.choices[0].message.content
                    st.success("Ecco il tuo annuncio pronto da copiare!")
                    st.markdown(risultato)
                    
                except Exception as e:
                    st.error(f"Si è verificato un errore con l'IA: {e}")