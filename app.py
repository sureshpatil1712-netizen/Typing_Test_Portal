import streamlit as st
import time
import difflib
from supabase import create_client, Client

# १. पेजचे प्राथमिक सेटिंग
st.set_page_config(page_title="40 WPM Typing Test", page_icon="⌨️", layout="wide")

# २. डेटाबेस जोडणी
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# ३. लॉगिन आणि रजिस्ट्रेशन पेज डिझाईन
def login_registration_page():
    st.title("⌨️ 40 WPM Typing Test Portal")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["लॉगिन (Login)", "नवीन रजिस्ट्रेशन (Sign Up)"])
    
    with tab1:
        st.subheader("तुमच्या अकाउंटमध्ये प्रवेश करा")
        login_email = st.text_input("ईमेल (Email)", key="log_email")
        login_pass = st.text_input("पासवर्ड (Password)", type="password", key="log_pass")
        
        if st.button("लॉगिन करा", type="primary"):
            try:
                response = supabase.auth.sign_in_with_password({"email": login_email, "password": login_pass})
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = login_email
                st.success("लॉगिन यशस्वी! डॅशबोर्ड लोड होत आहे...")
                st.rerun()
            except Exception as e:
                st.error("लॉगिन अयशस्वी. कृपया ईमेल आणि पासवर्ड बरोबर असल्याची खात्री करा.")

    with tab2:
        st.subheader("नवीन अकाउंट तयार करा")
        st.info("🎁 नवीन रजिस्ट्रेशनवर मिळवा १० प्रॅक्टिस परिच्छेद पूर्णपणे मोफत!")
        reg_email = st.text_input("नवीन ईमेल (Email)", key="reg_email")
        reg_pass = st.text_input("पासवर्ड (किमान ६ अक्षरे)", type="password", key="reg_pass")
        
        if st.button("रजिस्ट्रेशन करा", type="primary"):
            try:
                response = supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                supabase.table("users_data").insert({
                    "email": reg_email, 
                    "free_passages_left": 10,
                    "is_premium": False
                }).execute()
                st.success("रजिस्ट्रेशन यशस्वी! आता तुम्ही 'लॉगिन' टॅबवर जाऊन लॉगिन करू शकता.")
            except Exception as e:
                st.error(f"रजिस्ट्रेशन अयशस्वी. हा ईमेल आधीच वापरला असू शकतो किंवा पासवर्ड ६ अक्षरांपेक्षा लहान आहे.")

# ४. मुख्य नेव्हिगेशन आणि डॅशबोर्ड
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_registration_page()
            
    else:
        st.sidebar.title("मेनू 📌")
        st.sidebar.write(f"👤 {st.session_state['user_email']}")
        
        # --- स्मार्ट मेनू लॉजिक (Admin Panel लपवणे) ---
        admin_email = "sureshpatil1712@gmail.com" 
        menu = ["Dashboard", "Typing Test", "Support Form"]
        
        # जर लॉगिन केलेला व्यक्ती तू (Admin) असशील, तरच मेनूमध्ये 'Admin Panel' ॲड होईल
        if st.session_state['user_email'] == admin_email:
            menu.append("Admin Panel")
            
        choice = st.sidebar.radio("पेज निवडा:", menu)

        # ----------------- डॅशबोर्ड -----------------
        if choice == "Dashboard":
            st.title("तुमचा डॅशबोर्ड 📊")
            
            user_data = supabase.table("users_data").select("*").eq("email", st.session_state['user_email']).execute()
            if len(user_data.data) > 0:
                free_left = user_data.data[0]['free_passages_left']
                is_premium = user_data.data[0]['is_premium']
                
                if is_premium:
                    st.success(f"🌟 तुम्ही प्रीमियम युझर आहात! उर्वरित परिच्छेद: {free_left}")
                else:
                    st.info(f"**उर्वरित मोफत परिच्छेद:** {free_left} / 10")
                    if free_left <= 0:
                        st.warning("तुमचे मोफत परिच्छेद संपले आहेत. नवीन परिच्छेद अनलॉक करण्यासाठी अपग्रेड करा.")
            else:
                st.warning("डेटा लोड होत आहे, कृपया रिफ्रेश करा.")
            
            st.markdown("---")
            if st.button("Logout (बाहेर पडा)"):
                st.session_state['logged_in'] = False
                supabase.auth.sign_out()
                st.rerun()

        # ----------------- ॲडमिन पॅनेल -----------------
        elif choice == "Admin Panel":
            st.title("ऑथर पॅनेल 🛠️")
            
            if st.session_state['user_email'] == admin_email:
                st.success("✅ Admin Access Granted!")
                
                st.subheader("१. नवीन परिच्छेद ॲड करा")
                passage_title = st.text_input("परिच्छेदाचे नाव (उदा. Bombay HC Civil Draft 1)")
                passage_content = st.text_area("परिच्छेदाचा मजकूर (Content)", height=150)
                
                if st.button("Save Passage", type="primary"):
                    if passage_title and passage_content:
                        word_count = len(passage_content.split())
                        try:
                            supabase.table("passages").insert({
                                "title": passage_title, "content": passage_content, "word_count": word_count
                            }).execute()
                            st.success(f"🎉 परिच्छेद सेव्ह झाला! (एकूण शब्द: {word_count})")
                        except Exception as e:
                            st.error("परिच्छेद सेव्ह करताना अडचण आली.")
                
                st.markdown("---")
                
                st.subheader("२. विद्यार्थ्यांच्या तक्रारी आणि फीडबॅक (Student Requests)")
                requests_data = supabase.table("student_requests").select("*").order("created_at", desc=True).execute()
                
                if requests_data.data:
                    for req in requests_data.data:
                        with st.expander(f"{req['category']} - {req['user_email']}"):
                            st.write(req['message'])
                else:
                    st.info("सध्या कोणतेही नवीन मेसेजेस नाहीत.")

        # ----------------- सपोर्ट फॉर्म -----------------
        elif choice == "Support Form":
            st.title("मदत आणि फीडबॅक 📝")
            st.write("वेबसाईट वापरताना काही अडचण आल्यास किंवा नवीन परिच्छेद हवा असल्यास खालील फॉर्म भरा.")
            
            with st.form("support_form"):
                category = st.selectbox("विषय निवडा:", ["तांत्रिक अडचण (Technical Issue)", "नवीन परिच्छेदाची मागणी (New Passage)", "पेमेंट अडचण (Payment Issue)", "इतर (Other)"])
                message = st.text_area("तुमचा मेसेज सविस्तर लिहा:")
                submitted = st.form_submit_button("Submit (मेसेज पाठवा)")
                
                if submitted:
                    if message:
                        try:
                            supabase.table("student_requests").insert({
                                "user_email": st.session_state['user_email'],
                                "category": category,
                                "message": message,
                                "status": "Pending"
                            }).execute()
                            st.success("तुमचा मेसेज यशस्वीरित्या पाठवला गेला आहे! ॲडमिन लवकरच यावर कार्यवाही करतील.")
                        except Exception as e:
                            st.error("मेसेज पाठवताना अडचण आली.")
                    else:
                        st.warning("कृपया मेसेज लिहा.")

        # ----------------- टायपिंग टेस्ट -----------------
        elif choice == "Typing Test":
            st.title("टायपिंग टेस्ट सुरू करा ⏱️")
            
            if 'test_active' not in st.session_state: st.session_state['test_active'] = False
            if 'show_result' not in st.session_state: st.session_state['show_result'] = False
                
            # स्क्रीन १: परिच्छेद निवडणे आणि क्रेडिट्स चेक करणे
            if not st.session_state['test_active'] and not st.session_state['show_result']:
                
                user_data = supabase.table("users_data").select("*").eq("email", st.session_state['user_email']).execute()
                
                # --- Safe Check ॲड केला ---
                if len(user_data.data) > 0:
                    credits_left = user_data.data[0]['free_passages_left']
                    is_premium = user_data.data[0]['is_premium']
                else:
                    st.error("तुमचा अकाउंट डेटा लोड करताना अडचण आली. कृपया पुन्हा लॉगिन करा किंवा डॅशबोर्डला भेट द्या.")
                    credits_left = 0
                    is_premium = False
                
                if credits_left <= 0 and not is_premium:
                    st.error("🚫 तुमचे मोफत परिच्छेद संपले आहेत!")
                    st.info("अधिक सराव करण्यासाठी फक्त ₹21 भरून नवीन 51 परिच्छेद अनलॉक करा.")
                    
                    if st.button("Unlock 51 Passages for ₹21 (Dummy Pay)"):
                        supabase.table("users_data").update({
                            "is_premium": True, "free_passages_left": 51
                        }).eq("email", st.session_state['user_email']).execute()
                        st.success("पेमेंट यशस्वी! नवीन परिच्छेद अनलॉक झाले आहेत. कृपया पेज रिफ्रेश करा.")
                        st.rerun()
                else:
                    response = supabase.table("passages").select("*").execute()
                    passages_list = response.data
                    
                    if len(passages_list) == 0:
                        st.warning("सध्या कोणताही परिच्छेद उपलब्ध नाही. ॲडमिनने परिच्छेद टाकण्याची वाट पहा.")
                    else:
                        st.subheader("१. सरावासाठी परिच्छेद निवडा:")
                        passage_titles = [p['title'] for p in passages_list]
                        selected_title = st.selectbox("खालील यादीतून परिच्छेद निवडा:", passage_titles)
                        
                        selected_passage = next(item for item in passages_list if item["title"] == selected_title)
                        st.write(f"**एकूण शब्द:** {selected_passage['word_count']} | **वेळ:** १० मिनिटे")
                        st.markdown("---")
                        
                        st.subheader("२. परीक्षेचा मोड निवडा:")
                        exam_mode = st.radio(
                            "तुम्हाला कोणत्या पद्धतीने टेस्ट द्यायची आहे?",
                            ["💻 Online Typing (Screen-to-Screen)", "📄 Paper Typing (Hardcopy-to-Screen)"]
                        )
                        
                        if "Paper" in exam_mode:
                            st.info("टीप: पेपर मोडमध्ये टेस्ट सुरू झाल्यावर स्क्रीनवर परिच्छेद दिसणार नाही. त्यामुळे खालील परिच्छेदाची प्रिंट काढा किंवा वाचण्यासाठी तयार ठेवा.")
                            with st.expander("परिच्छेद पहा आणि कॉपी करा (Print/Copy)"):
                                st.write(selected_passage['content'])
                        
                        st.markdown("---")
                        
                        if st.button("Start Test 🚀", type="primary", use_container_width=True):
                            st.session_state['test_active'] = True
                            st.session_state['start_time'] = time.time()
                            st.session_state['selected_passage'] = selected_passage
                            st.session_state['exam_mode'] = exam_mode
                            st.rerun()

            # स्क्रीन २: प्रत्यक्ष टायपिंग टेस्ट 
            elif st.session_state['test_active']:
                passage = st.session_state['selected_passage']
                mode = st.session_state['exam_mode']
                
                st.subheader(f"टेस्ट सुरू आहे: {passage['title']}")
                st.warning("⏳ तुमचा वेळ सुरू झाला आहे! बरोबर १० मिनिटांनी किंवा टायपिंग पूर्ण झाल्यावर खालील 'Submit Test' बटण दाबा.")
                
                if "Online" in mode:
                    st.info("खालील परिच्छेद पाहून टाईप करा:")
                    st.write(passage['content'])
                else:
                    st.info("📄 पेपर मोड सुरू आहे. स्क्रीनवर परिच्छेद दिसणार नाही. तुमच्या जवळील प्रिंट केलेला परिच्छेद पाहून टाईप करा.")
                    
                typed_text = st.text_area("येथे टाईप करायला सुरुवात करा:", height=300)
                
                if st.button("Submit Test (पेपर जमा करा)", type="primary"):
                    end_time = time.time()
                    time_taken = end_time - st.session_state['start_time']
                    
                    # --- क्रेडिट वजा करणे (१ परिच्छेद कमी करणे) - Safe Check ॲड केला ---
                    user_data = supabase.table("users_data").select("*").eq("email", st.session_state['user_email']).execute()
                    
                    if len(user_data.data) > 0:
                        current_credits = user_data.data[0]['free_passages_left']
                        if current_credits > 0:
                            supabase.table("users_data").update({"free_passages_left": current_credits - 1}).eq("email", st.session_state['user_email']).execute()
                    
                    st.session_state['test_active'] = False
                    st.session_state['typed_text'] = typed_text
                    st.session_state['time_taken'] = time_taken
                    st.session_state['show_result'] = True
                    st.rerun()

            # स्क्रीन ३: रिझल्ट आणि मार्किंग पेज
            elif st.session_state['show_result']:
                st.title("📊 तुमचा निकाल (Result)")
                
                original_text = st.session_state['selected_passage']['content']
                typed_text = st.session_state['typed_text']
                time_taken = st.session_state['time_taken']
                
                time_mins = min(time_taken / 60.0, 10.0)
                if time_mins == 0: time_mins = 0.01 
                
                gross_words = len(typed_text) / 5.0
                gross_wpm = round(gross_words / time_mins, 2)
                
                original_words = original_text.split()
                typed_words = typed_text.split()
                
                matcher = difflib.SequenceMatcher(None, original_words, typed_words)
                mistakes = 0
                error_display = [] 
                
                for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                    if tag == 'equal':
                        error_display.append(" ".join(typed_words[j1:j2]))
                    elif tag == 'replace': 
                        mistakes += max((i2 - i1), (j2 - j1))
                        wrong_words = " ".join(typed_words[j1:j2])
                        error_display.append(f"<span style='color:red; text-decoration:line-through;'>{wrong_words}</span>")
                    elif tag == 'delete': 
                        mistakes += (i2 - i1)
                        missed_words = " ".join(original_words[i1:i2])
                        error_display.append(f"<span style='color:orange;'>[{missed_words} - सुटले]</span>")
                    elif tag == 'insert': 
                        mistakes += (j2 - j1)
                        extra_words = " ".join(typed_words[j1:j2])
                        error_display.append(f"<span style='color:red; font-weight:bold;'>{extra_words}</span>")
                        
                net_words = max(0, gross_words - mistakes)
                net_wpm = round(net_words / time_mins, 2)
                marks = max(0, 20 - (mistakes * 0.25))
                
                st.markdown("---")
                
                if mistakes >= 40:
                    st.error("❌ तुम्ही या टेस्टमध्ये अपात्र (Disqualified) ठरला आहात!")
                    st.markdown(f"**तुमच्या एकूण चुका:** <span style='color:red; font-size:24px;'>{mistakes}</span>", unsafe_allow_html=True)
                    st.warning("४० किंवा त्याहून अधिक चुका असल्यामुळे तुम्हाला शून्य (०) गुण मिळाले आहेत. कृपया अधिक सराव करा.")
                    
                    if st.button("Restart (पुन्हा प्रयत्न करा)", type="primary"):
                        st.session_state['show_result'] = False
                        st.session_state['test_active'] = False
                        st.rerun()
                else:
                    st.success("🎉 अभिनंदन! तुम्ही टेस्ट पूर्ण केली.")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Gross Speed", f"{gross_wpm} WPM")
                    col2.metric("Net Speed", f"{net_wpm} WPM")
                    col3.metric("एकूण चुका", f"{mistakes}")
                    col4.metric("प्राप्त गुण", f"{marks} / 20")
                    
                    st.markdown("### 🔍 चुकांचे विश्लेषण:")
                    st.info("लाल रंग = चुकीचे/जास्तीचे शब्द | केशरी रंग = टाईप करायचे सुटलेले शब्द")
                    
                    st.markdown(f"<div style='background-color:#f0f2f6; padding:15px; border-radius:10px; line-height:1.6;'>{' '.join(error_display)}</div>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("डॅशबोर्डवर परत जा", type="primary"):
                        st.session_state['show_result'] = False
                        st.session_state['test_active'] = False
                        st.rerun()

if __name__ == '__main__':
    main()
