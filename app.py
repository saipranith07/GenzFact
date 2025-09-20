import streamlit as st
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import re

st.set_page_config(
    page_title="GenzFact",
    page_icon="⚖️",
    layout="wide"
)


st.markdown("""
<style>
    .main {
        background-color: #111111;
        color: #FFFFFF;
    }
    .block-container {
        max-width: 700px;
        margin: auto;
        text-align: center;
    }
    h1 {
        font-size: 64px !important;
        font-weight: 600 !important;
        margin-bottom: 40px;
        color: white;
    }
    .stTextArea textarea, .stTextInput input {
        background-color: #111111;
        color: #FFFFFF;
        border: 2px solid #FFFFFF;
        border-radius: 40px;
        padding: 14px;
        font-size: 18px;
        text-align: left;
    }
    .stTextArea label, .stTextInput label {
        display: none;
    }
    .stFileUploader {
        border: 2px solid #FFFFFF;
        border-radius: 40px;
        padding: 14px;
        background: #111111;
    }
    .stFileUploader label {
        font-size: 20px;
        color: white !important;
        font-weight: 500;
    }
    .stFileUploader div div {
        color: #AAAAAA !important;
    }
    .stButton button {
        background-color: #DDDDDD;
        color: black;
        font-size: 20px;
        border-radius: 40px;
        padding: 12px 40px;
        font-weight: 600;
        margin-top: 25px;
        border: none;
    }
    .stButton button:hover {
        background-color: #FFFFFF;
        color: black;
    }
    /* Badge styles */
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        color: black;
    }
    .badge-green { background-color: #4CAF50; color: white; }   /* TRUE */
    .badge-red { background-color: #E53935; color: white; }     /* FALSE */
    .badge-yellow { background-color: #FFB300; color: black; }  /* MISLEAD */
    .badge-blue { background-color: #1E88E5; color: white; }    /* UNVERIFIED */
</style>
""", unsafe_allow_html=True)

PROJECT_ID = "genzfact"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)


SYSTEM_INSTRUCTION = """
You are GenzFact, a specialized AI assistant designed to demystify complex legal documents
and identify potentially misleading information.

Always output ONLY in this exact formatted structure (Markdown, no extra text):

1. What is misinformation?
   - <answer here>

2. Extracted Misinformation Breakdown
   - <answer here>

3. Verification Panel:
   - Badge: true / false / unverified / mislead
   - Evidence Links:
     - <link1>
     - <link2>

4. AI Explanation
   - <answer here>

5. Credibility Score (0-100)
   - <number>
"""
model = GenerativeModel(
    "gemini-2.5-pro",
    system_instruction=SYSTEM_INSTRUCTION
)

st.title("GenzFact")
prompt_text = st.text_area("Ask GenzFact Anything...", key="prompt_box")
uploaded_file = st.file_uploader(
    "Upload a Document, Image, or Audio File",
    type=['pdf', 'doc', 'txt', 'png', 'jpg', 'jpeg', 'mp3', 'wav']
)

if st.button("Analyze", key="analyze_button"):
    if not prompt_text and not uploaded_file:
        st.warning("Please provide some text or upload a file to analyze.")
    else:
        with st.spinner("GenzFact is analyzing..."):
            request_contents = []
            if uploaded_file is not None:
                file_bytes = uploaded_file.getvalue()
                file_mime_type = uploaded_file.type
                request_contents.append(Part.from_data(data=file_bytes, mime_type=file_mime_type))

            if prompt_text:
                request_contents.append(Part.from_text(prompt_text))

            try:
                response = model.generate_content(request_contents)
                raw_text = response.text.strip()

                def replace_badge(match):
                    badge_value = match.group(1).strip().upper()
                    if badge_value == "TRUE":
                        return "Badge: <span class='badge badge-green'>TRUE</span>"
                    elif badge_value == "FALSE":
                        return "Badge: <span class='badge badge-red'>FALSE</span>"
                    elif badge_value == "MISLEAD":
                        return "Badge: <span class='badge badge-yellow'>MISLEAD</span>"
                    else:
                        return "Badge: <span class='badge badge-blue'>UNVERIFIED</span>"

                formatted_text = re.sub(r"Badge:\s*(\w+)", replace_badge, raw_text, flags=re.IGNORECASE)

                
                st.divider()
                st.subheader("Analysis Report")

                formatted_text = f"""
                <div style="text-align: left; line-height: 1.6; font-size: 16px;">
                {formatted_text}
                </div>
                """

               
                badge_colors = {
                    "TRUE": "#4CAF50",      
                    "FALSE": "#E53935",      
                    "MISLEAD": "#FDD835",    
                    "UNVERIFIED": "#1E88E5"  
                }

                for badge, color in badge_colors.items():
                    formatted_text = formatted_text.replace(
                        f"Badge: {badge}",
                        f"<span style='display:inline-block; padding:6px 14px; border-radius:12px; "
                        f"background-color:{color}; color:white; font-weight:bold;'>Badge: {badge}</span>"
                    )

                st.markdown(formatted_text, unsafe_allow_html=True)


            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
                st.write("Raw response:", response)
