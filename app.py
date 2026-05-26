import streamlit as st
from PIL import Image, ImageEnhance
import google.generativeai as genai

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Vinted AI Assistant Free", page_icon="🛍️", layout="centered")

st.title("🛍️ Vinted AI Assistant (Versione 100% Gratis)")
st.write("Migliora la foto e lascia che l'IA gratuita di Google crei l'annuncio perfetto per te.")

# --- Configurazione Chiave API Gemini ---
api_key = st.sidebar.text_input("Inserisci la tua Gemini API Key (Gratis)", type="password")
if not api_key and "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

# --- 1. CARICAMENTO IMMAGINE ---
uploaded_file = st.file_uploader("Scegli la foto del capo d'abbigliamento", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    st.subheader("🔧 Strumenti di Miglioramento")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rotazione = st.slider("Raddrizza / Ruota (Gradi)", -180, 180, 0, step=90)
    with col2:
        luminosita = st.slider("Luminosità", 0.5, 2.0, 1.0, step=0.1)
    with col3:
        contrasto = st.slider("Contrasto", 0.5, 2.0, 1.0, step=0.1)
        
    # Applicazione modifiche
    if rotazione != 0:
        image = image.rotate(-rotazione, expand=True)
    
    image = ImageEnhance.Brightness(image).enhance(luminosita)
    image = ImageEnhance.Contrast(image).enhance(contrasto)
    
    st.image(image, caption="Foto ottimizzata pronta per Vinted", use_column_width=True)
    
    # --- 2. GENERAZIONE ANNUNCIO CON GEMINI ---
    st.subheader("🤖 Generatore Annuncio Gratis")
    
    if st.button("Genera Titolo, Descrizione e Prezzo ✨"):
        if not api_key:
            st.error("Per favore, inserisci la tua Gemini API Key nella barra laterale per continuare.")
        else:
            with st.spinner("Gemini sta analizzando il tuo capo d'abbigliamento..."):
                try:
                    # Configuriamo l'IA di Google
                    genai.configure(api_key=api_key)
                    
                    # Usiamo il modello 'gemini-1.5-flash', perfetto, veloce e gratuito per le immagini
                    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
                    
                    prompt_testo = (
                        "Analizza attentamente questa foto di un capo d'abbigliamento destinato alla vendita su Vinted. "
                        "Fornisci un output in italiano strutturato esattamente in questo modo:\n\n"
                        "### 🎯 TITOLO ACCATTIVANTE\n"
                        "(Scrivi un titolo di massimo 40 caratteri ottimizzato per la ricerca su Vinted, includendo marca, stile o colore principale ed emoji. Es: 'Felpa Nike Vintage Blu M ✨')\n\n"
                        "### 📝 DESCRIZIONE PERSUASIVA\n"
                        "(Scrivi una descrizione dettagliata, onesta e accattivante in italiano. Includi lo stile (es. streetwear, y2k, minimal), "
                        "consigli su come abbinarlo, lo stato visibile del capo, invoglia all'acquisto rapido e aggiungi hashtag pertinenti.)\n\n"
                        "### 💰 PREZZO CONSIGLIATO\n"
                        "(Suggerisci un prezzo di vendita realistico per Vinted basato sul brand e sul tipo di capo, specificando una strategia di vendita veloce.)"
                    )
                    
                    # Con Gemini possiamo passare direttamente l'immagine PIL senza fare conversioni strane!
                    response = model.generate_content([prompt_testo, image])
                    
                    st.success("Ecco il tuo annuncio pronto!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Si è verificato un errore con Gemini: {e}")
