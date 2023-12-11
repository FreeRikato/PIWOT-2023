import streamlit as st
from io import BytesIO
from dotenv import load_dotenv
from PIL import Image
import io
import os
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # This disables the GPU

import tensorflow as tf
from joblib import load
import numpy as np

from htmlTemplates import css, bot_template, user_template
from pdf_extractor import get_pdf_text
from text_chunker import get_text_chunks
from generate_embedding import get_vectorstore
from conversation_chain import get_conversation_chain
from save_files import save_uploaded_files
from find_source_pdf import search_pdfs
from pdf_to_image import pdf_pages_to_images
from tensorflow.keras.preprocessing import image


# Function to preprocess an image for prediction
def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(224, 224))  # Assuming your model expects 224x224 images
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    # img_array /= 255.0  # Normalize pixel values to the range [0, 1]
    return img_array

# Function to make predictions on an image
def predict_image(model, image_path):
    preprocessed_image = preprocess_image(image_path)
    predictions = model.predict(preprocessed_image)
    predicted_class = np.argmax(predictions)
    return predicted_class

def handle_userinput(user_question):
    chat_history = st.session_state.get('chat_history', [])
    response = st.session_state.conversation({"question": user_question, "chat_history": chat_history})
    answer = response.get('answer')
    source_document = response.get('source_documents')
    chat_history.append((user_question, answer))
    st.session_state['chat_history'] = chat_history
    for i, message in enumerate(st.session_state.chat_history):
        question, answer = message
        st.write(user_template.replace(
            "{{MSG}}", question), unsafe_allow_html=True)
        st.write(bot_template.replace(
            "{{MSG}}", answer), unsafe_allow_html=True)
        
    source = str(source_document[0]).split("page_content='", 1)[1].rstrip("'").replace('\\n', '\n').replace('\\t', '\t')

    found_pdf_path, found_page_num = search_pdfs("knowledge_base", source)
    
    if found_pdf_path:
        st.sidebar.write(f'Text found in: {found_pdf_path}')
        # Convert the found page, its previous, and its next page to images
        images = pdf_pages_to_images(found_pdf_path, found_page_num)
        for (img, pg_num) in images:  # Unpack the tuple here
            # Save fitz pixmap to a BytesIO buffer as a PNG
            buffer = BytesIO()
            buffer.write(img.tobytes("png"))
            buffer.seek(0)

            # Convert the BytesIO buffer to a PIL Image
            pil_img = Image.open(buffer)

            # Display the image in Streamlit's sidebar
            st.sidebar.image(pil_img, caption=f"Page {pg_num}")
    else:
        print(f'Text not found in any PDF in the knowledge base')
    

def main():
    load_dotenv()
    tf.keras.backend.clear_session()
    loaded_model = load('model.joblib')
    classes_names = ['Acne and Rosacea Photos',
        'Actinic Keratosis Basal Cell Carcinoma and other Malignant Lesions',
        'Atopic Dermatitis Photos',
        'Bullous Disease Photos',
        'Cellulitis Impetigo and other Bacterial Infections',
        'Chicken Pox and Measles',
        'Eczema Photos',
        'Exanthems and Drug Eruptions',
        'Hair Loss Photos Alopecia and other Hair Diseases',
        'Herpes HPV and other STDs Photos',
        'Light Diseases and Disorders of Pigmentation',
        'Lupus and other Connective Tissue diseases',
        'Melanoma Skin Cancer Nevi and Moles',
        'Monkey Pox',
        'Nail Fungus and other Nail Disease',
        'Poison Ivy Photos and other Contact Dermatitis',
        'Psoriasis pictures Lichen Planus and related diseases',
        'Scabies Lyme Disease and other Infestations and Bites',
        'Seborrheic Keratoses and other Benign Tumors',
        'Systemic Disease',
        'Tinea Ringworm Candidiasis and other Fungal Infections',
        'Urticaria Hives',
        'Vascular Tumors',
        'Vasculitis Photos',
        'Warts Molluscum and other Viral Infections',
        'bags',
        'bopeng',
        'bruntusan',
        'cystic',
        'papula',
        'pustula']
    embeddings = OpenAIEmbeddings()
    st.set_page_config(page_title="DermAI: A Provisional Diagnosis System",
                       page_icon="🧑🏻‍⚕️")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.header("DermAI: A Provisional Diagnosis System 🧑🏻‍⚕️")
    user_question = st.text_input(" ")
    
    knowledge_base_path = "knowledge_base"
    local_pdf_files = [os.path.join(knowledge_base_path, f) for f in os.listdir(knowledge_base_path) if f.endswith('.pdf')]
    
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        
        uploaded_files = st.file_uploader(
            "Upload your PDFs here and click on 'Process'",
            accept_multiple_files=True,
            type="jpg")
        if st.button("Process"):
            with st.spinner("Processing"):
                for uploaded_file in uploaded_files:
                    if uploaded_file is not None:
                        # To read file as bytes:
                        bytes_data = uploaded_file.getvalue()
                        loaded_image = Image.open(io.BytesIO(bytes_data))
                        st.image(loaded_image, caption='Uploaded Image.', use_column_width=True)

                        # Save the uploaded file to the user's directory
                        file_path = os.path.join(os.path.expanduser("~"), uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(bytes_data)
                        st.success(f"File saved at: {file_path}")
                        
                        predicted_class = predict_image(loaded_model, file_path)

                        st.subheader(f'Predicted skin condition: {classes_names[predicted_class]}')
                        vectorstore = FAISS.from_texts(texts = "#", embedding = embeddings)
                        vectorstore.load_local("knowledge_base/vectorbase", embeddings)

                        # create conversation chain
                        st.session_state.conversation = get_conversation_chain(
                            vectorstore)


if __name__ == '__main__':
    main()