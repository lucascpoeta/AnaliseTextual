import streamlit as st
import pandas as pd
import json
import re
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud
import fitz  # PyMuPDF


# Lista de palavras comuns (stopwords) para remover
def remove_stopwords(words):
    stopwords = {"de", "da", "do", "das", "dos", "e", "o", "a", "os", "as", "em", "que", "na", "no", "nos", "nas"}
    return [word for word in words if word.lower() not in stopwords]


# Função para limpar e remover caracteres especiais
def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove caracteres especiais
    return text


def text_analysis(text):
    # Limpar o texto antes de realizar a análise
    text = clean_text(text)
    
    words = text.split()
    words = remove_stopwords(words)
    word_count = len(words)
    char_count = sum(len(word) for word in words)
    word_freq = Counter(words)
    most_common = word_freq.most_common(10)

    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)

    paragraphs = text.split("\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    paragraph_count = len(paragraphs)

    avg_word_length = char_count / word_count if word_count > 0 else 0
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

    return word_count, char_count, most_common, sentence_count, paragraph_count, avg_word_length, avg_sentence_length, word_freq


st.title("📊 Análise Estatística de Texto")
st.write("Forneça um texto para análise estatística. Escolha entre escrever ou enviar um arquivo.")

# Escolha entre digitar ou enviar um arquivo
input_choice = st.radio("Escolha como deseja fornecer o texto:", ("Escrever o texto", "Enviar um arquivo"))

text = ""
if input_choice == "Escrever o texto":
    # Entrada de texto digitado
    text_input = st.text_area("Digite ou cole um texto:")
    text = text_input

elif input_choice == "Enviar um arquivo":
    # Upload de arquivo
    uploaded_file = st.file_uploader("Envie um arquivo de texto ou PDF", type=["txt", "csv", "xlsx", "json", "pdf"])

    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1]
        if file_type == "txt":
            text = uploaded_file.getvalue().decode("utf-8")
        elif file_type == "csv":
            df = pd.read_csv(uploaded_file)
            text = " ".join(df.astype(str).values.flatten())
        elif file_type == "xlsx":
            df = pd.read_excel(uploaded_file)
            text = " ".join(df.astype(str).values.flatten())
        elif file_type == "json":
            data = json.load(uploaded_file)
            text = json.dumps(data)
        elif file_type == "pdf":
            # Lê o arquivo PDF e extrai o texto
            pdf_document = fitz.open(uploaded_file)
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text += page.get_text("text")
        else:
            st.error("Formato de arquivo não suportado. Envie um arquivo de texto (.txt, .csv, .xlsx, .json, .pdf).")

if text:
    st.write("## 📑 Resultados da Análise:")
    word_count, char_count, most_common, sentence_count, paragraph_count, avg_word_length, avg_sentence_length, word_freq = text_analysis(
        text)
    st.write(f"📄 Número total de palavras: {word_count}")
    st.write(f"🔤 Número total de caracteres (sem espaços): {char_count}")
    st.write(f"📏 Comprimento médio das palavras: {avg_word_length:.2f} caracteres")
    st.write(f"📜 Número de sentenças: {sentence_count}")
    st.write(f"📖 Número de parágrafos: {paragraph_count}")
    st.write(f"📎 Comprimento médio das frases: {avg_sentence_length:.2f} palavras")

    st.write("📊 Palavras mais frequentes:")
    df = pd.DataFrame(most_common, columns=["Palavra", "Frequência"])
    st.table(df)

    # Escolher o tipo de gráfico
    chart_type = st.radio("Escolha o tipo de gráfico", ("Gráfico de Barra", "Gráfico de Pizza", "Nuvem de Palavras"))

    if chart_type == "Gráfico de Barra":
        st.write("### 📊 Gráfico de Frequência das Palavras")
        fig, ax = plt.subplots()
        sns.barplot(x=[word for word, freq in most_common], y=[freq for word, freq in most_common], ax=ax)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig)

    elif chart_type == "Gráfico de Pizza":
        st.write("### 🍕 Gráfico de Frequência das Palavras")
        fig, ax = plt.subplots()
        ax.pie([freq for word, freq in most_common], labels=[word for word, freq in most_common],
               autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)

    elif chart_type == "Nuvem de Palavras":
        st.write("### ☁️ Nuvem de Palavras")
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(word_freq.keys()))
        fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
        ax_wc.imshow(wordcloud, interpolation='bilinear')
        ax_wc.axis("off")
        st.pyplot(fig_wc)
