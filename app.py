from flask import Flask, render_template, request, jsonify
import openai
import pdfplumber
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

app = Flask(__name__)
# Your OpenAI API key
openai.api_key = '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'

# Default PDF file
DEFAULT_PDF_FILE = "C:\dummy\RULES word.pdf"

# Function to extract text from PDF


def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to summarize text (optional)


def summarize_text(text, ratio=0.5):  # Adjust ratio for desired summary length
    parser = PlaintextParser.from_string(text, Tokenizer())
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, sentences_count=int(
        ratio * len(parser.document.sentences)))
    summary_text = " ".join([str(sentence) for sentence in summary])
    return summary_text

# Function to answer questions using OpenAI


def answer_question(question, context, max_tokens=150):  # Reduce answer length by default
    shortened_context = context[:4096]  # Limit context length to 4096 tokens
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=shortened_context + "\nQuestion: " + question + "\nAnswer:",
        max_tokens=max_tokens
    )
    return response.choices[0].text.strip()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            question = request.form['question']

            # Extract text from the default PDF file
            pdf_text = extract_text_from_pdf(DEFAULT_PDF_FILE)

            # Summarize text (optional)
            # pdf_text = summarize_text(pdf_text)

            # Answer the question using OpenAI
            answer = answer_question(question, pdf_text)

            return jsonify({'question': question, 'answer': answer})
        except Exception as e:
            return jsonify({'error': str(e)})

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
