import streamlit as st
from PIL import Image

# Set page config to widen the page and set the initial layout
st.set_page_config(page_title='DermAI', layout="centered")

# Custom CSS to add hover effects to the buttons
st.markdown("""
<style>
    .hover-button {
        padding: 0.25rem 1rem;
        margin: 0.25rem;
        color: #fff;
        border: 1px solid #fff;
        border-radius: 4px;
        text-align: center;
        display: inline-block;
        cursor: default;
    }
    .hover-button:hover {
        background-color: #444;
        border-color: #888;
    }
    .css-18e3th9 {
        background-color: #0e1117;
    }
    .css-1d391kg {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# Creating a sidebar for settings or information
st.sidebar.title("DermAI")

# Sidebar image uploader
# Sidebar image uploader for multiple images
uploaded_images = st.sidebar.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Display the uploaded images
if uploaded_images is not None:
    for uploaded_image in uploaded_images:
        image = Image.open(uploaded_image)
        st.sidebar.image(image, caption='Uploaded Image.', use_column_width=True)


# Session state to store chat history
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Text area to take user input
user_input = st.text_input("Ask your query here:", "")

# Create the non-clickable buttons with hover effect below the text input
button_texts = [
    "Please describe the skin issue you're experiencing in as much detail as possible.",
    "When did you first notice the skin condition?",
    "Has the appearance or size of the condition changed over time?",
    "Has the condition spread or remained localized to one area?",
    "On a scale from 1 to 10, how would you rate your discomfort or pain?",
    "Are you experiencing any itching, burning, or stinging sensations?",
    "Have you tried any treatments or products for this condition yet?",
    "Did any previous treatments improve, worsen, or have no effect on your skin condition?",
    "Tell me about your daily skin care routine.",
    "Have you been exposed to anything new or unusual that might have affected your skin?",
    "Do you have any known allergies or a history of skin conditions?",
    "Are there any ongoing medical conditions or medications that we should be aware of?",
]

for text in button_texts:
    st.markdown(f'<p class="hover-button">{text}</p>', unsafe_allow_html=True)

# Function to simulate ChatGPT response
def get_gpt_response(user_input):
    # Placeholder for GPT model integration
    return f"GPT: You said '{user_input}'"

# If the user gives input, append it and the response to the history
if user_input:
    st.session_state['history'].append(f"You: {user_input}")
    gpt_response = get_gpt_response(user_input)
    st.session_state['history'].append(gpt_response)

# Display the chat history
for chat in st.session_state['history']:
    st.text_area("", chat, height=70, key=chat)
