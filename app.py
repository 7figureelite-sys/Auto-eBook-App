import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF
import os
import time
import urllib.parse

st.set_page_config(page_title="AI Auto Publisher 🚀", page_icon="📚", layout="centered")

st.title("🤖 AI Auto Publisher Pro")
st.markdown("एक क्लिक में **रिसर्च ➔ इमेजेस ➔ और कंप्लीट eBook PDF** तैयार!")

with st.sidebar:
    st.header("🔑 API Setup")
    api_key = st.text_input("यहाँ अपनी Google Gemini API Key डालें:", type="password")
    st.markdown("---")
    st.markdown("💡 **Whop Target:** $5k - $10k/Month")

topic = st.text_input("🎯 अपनी eBook का टॉपिक या आइडिया लिखें:", placeholder="e.g., 2026 me YouTube channel kaise grow kare")
pages = st.selectbox("📄 eBook के पेज (Chapters) चुनें:", [5, 10, 15, 20, 40, 50])

generate_btn = st.button("🚀 Generate Global Research & eBook", use_container_width=True)

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "Auto-Generated Premium eBook", align="C")
        self.ln(15)
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

if generate_btn:
    if not api_key:
        st.error("⚠️ प्लीज साइडबार में Gemini API Key डालें!")
    elif not topic:
        st.error("⚠️ प्लीज टॉपिक का नाम लिखें!")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash') 

            if not os.path.exists("temp_images"):
                os.makedirs("temp_images")

            pdf = PDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            with st.status("🔍 AI काम कर रहा है (इसमें 5-10 मिनट लग सकते हैं)...", expanded=True) as status:
                
                st.write("📊 ग्लोबल मार्केट रिसर्च और प्राइसिंग एनालाइज़ हो रही है...")
                research_prompt = f"Act as a global market researcher. Topic: {topic}. Give me: 1. A viral, click-worthy Title. 2. A short SEO Description. 3. Best selling price for Whop ($). Respond in simple English."
                research_data = model.generate_content(research_prompt).text
                
                pdf.set_font("helvetica", "B", 16)
                pdf.multi_cell(0, 10, "Market Research & Strategy")
                pdf.set_font("helvetica", "", 12)
                pdf.multi_cell(0, 8, research_data.replace("*", ""))
                pdf.add_page()
                time.sleep(2) 

                st.write(f"✍️ {pages} चैप्टर्स की राइटिंग और इमेजेस बन रही हैं...")
                
                for i in range(1, pages + 1):
                    st.write(f"⏳ Chapter {i} तैयार हो रहा है...")
                    
                    chapter_prompt = f"Act as an expert author. Write Chapter {i} for an eBook about '{topic}'. Include a short story or example. Give 3-4 paragraphs. Very Important: Include exactly ONE image prompt in the middle of the text. Write the image prompt exactly like this on a new line: IMAGE_PROMPT: [your detailed image description in english]."
                    
                    chapter_content = model.generate_content(chapter_prompt).text
                    
                    lines = chapter_content.split('\n')
                    pdf.set_font("helvetica", "", 12)
                    
                    pdf.set_font("helvetica", "B", 14)
                    pdf.cell(0, 10, f"Chapter {i}", ln=True)
                    pdf.set_font("helvetica", "", 12)
                    
                    for line in lines:
                        if line.startswith("IMAGE_PROMPT:"):
                            image_desc = line.replace("IMAGE_PROMPT:", "").strip()
                            st.write(f"🎨 इमेज बन रही है: {image_desc[:30]}...")
                            
                            encoded_prompt = urllib.parse.quote(image_desc)
                            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=500&nologo=true"
                            img_response = requests.get(image_url)
                            
                            if img_response.status_code == 200:
                                img_path = f"temp_images/img_{i}.jpg"
                                with open(img_path, 'wb') as f:
                                    f.write(img_response.content)
                                try:
                                    pdf.image(img_path, w=170)
                                    pdf.ln(5)
                                except Exception as e:
                                    pdf.multi_cell(0, 8, f"[Image generated but could not be added to PDF]")
                        else:
                            clean_line = line.replace("*", "").replace("#", "")
                            clean_line = clean_line.encode('latin-1', 'replace').decode('latin-1')
                            if clean_line.strip():
                                pdf.multi_cell(0, 8, clean_line)
                                pdf.ln(2)
                    
                    pdf.add_page()
                    time.sleep(3) 

                st.write("📑 पूरी eBook को PDF में पैक किया जा रहा है...")
                pdf_file_name = "Premium_eBook.pdf"
                pdf.output(pdf_file_name)
                
                status.update(label="✅ eBook सफलतापूर्वक बन गई!", state="complete", expanded=False)

            st.success("🎉 आपकी eBook Whop पर बेचने के लिए तैयार है!")
            with open(pdf_file_name, "rb") as pdf_file:
                st.download_button(
                    label="📥 Download Premium eBook (PDF)",
                    data=pdf_file,
                    file_name="My_Viral_eBook.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"❌ कुछ गड़बड़ हो गई: {e}")
              
