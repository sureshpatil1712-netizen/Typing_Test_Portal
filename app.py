import streamlit as st
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
    
    # लॉगिन आणि रजिस्ट्रेशनसाठी दोन टॅब्स
    tab1, tab2 = st.tabs(["लॉगिन (Login)", "नवीन रजिस्ट्रेशन (Sign Up)"])
    
    # टॅब 1: लॉगिन लॉजिक
    with tab1:
        st.subheader("तुमच्या अकाउंटमध्ये प्रवेश करा")
        login_email = st.text_input("ईमेल (Email)", key="log_email")
        login_pass = st.text_input("पासवर्ड (Password)", type="password", key="log_pass")
        
        if st.button("लॉगिन करा", type="primary"):
            try:
                # Supabase Auth द्वारे लॉगिन
                response = supabase.auth.sign_in_with_password({"email": login_email, "password": login_pass})
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = login_email
                st.success("लॉगिन यशस्वी! डॅशबोर्ड लोड होत आहे...")
                st.rerun() # पेज रिफ्रेश करण्यासाठी
            except Exception as e:
                st.error("लॉगिन अयशस्वी. कृपया ईमेल आणि पासवर्ड बरोबर असल्याची खात्री करा.")

    # टॅब 2: नवीन रजिस्ट्रेशन लॉजिक
    with tab2:
        st.subheader("नवीन अकाउंट तयार करा")
        st.info("🎁 नवीन रजिस्ट्रेशनवर मिळवा १० प्रॅक्टिस परिच्छेद पूर्णपणे मोफत!")
        reg_email = st.text_input("नवीन ईमेल (Email)", key="reg_email")
        reg_pass = st.text_input("पासवर्ड (किमान ६ अक्षरे)", type="password", key="reg_pass")
        
        if st.button("रजिस्ट्रेशन करा", type="primary"):
            try:
                # १. Supabase Auth मध्ये युझर बनवणे
                response = supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                
                # २. 'users_data' टेबलमध्ये मोफत १० परिच्छेदांसह डेटा सेव्ह करणे
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

    # जर युझर लॉगिन नसेल
    if not st.session_state['logged_in']:
        login_registration_page()
            
    # जर युझर लॉगिन असेल
    else:
        st.sidebar.title("मेनू 📌")
        st.sidebar.write(f"Logged in as: {st.session_state['user_email']}")
        
        menu = ["Dashboard", "Typing Test", "Support Form", "Admin Panel"]
        choice = st.sidebar.radio("पेज निवडा:", menu)

        if choice == "Dashboard":
            st.title("तुमचा डॅशबोर्ड 📊")
            
            # डेटाबेसमधून युझरचा रेकॉर्ड आणणे (किती मोफत परिच्छेद उरले आहेत ते तपासणे)
            user_data = supabase.table("users_data").select("*").eq("email", st.session_state['user_email']).execute()
            
            if len(user_data.data) > 0:
                free_left = user_data.data[0]['free_passages_left']
                st.info(f"**उर्वरित मोफत परिच्छेद:** {free_left} / 10")
            
            if st.sidebar.button("Logout"):
                st.session_state['logged_in'] = False
                # Supabase मधून Sign out करणे
                supabase.auth.sign_out()
                st.rerun()
                
        if choice == "Dashboard":
            st.title("तुमचा डॅशबोर्ड 📊")
            
            # डेटाबेसमधून युझरचा रेकॉर्ड आणणे (किती मोफत परिच्छेद उरले आहेत ते तपासणे)
            user_data = supabase.table("users_data").select("*").eq("email", st.session_state['user_email']).execute()
            
            if len(user_data.data) > 0:
                free_left = user_data.data[0]['free_passages_left']
                st.info(f"**उर्वरित मोफत परिच्छेद:** {free_left} / 10")
            
            if st.sidebar.button("Logout"):
                st.session_state['logged_in'] = False
                # Supabase मधून Sign out करणे
                supabase.auth.sign_out()
                st.rerun()

        # ---------- नवीन ॲडमिन पॅनेलचा कोड येथून सुरू ----------
        elif choice == "Admin Panel":
            st.title("ऑथर पॅनेल 🛠️")
            
            # इथे तुझा स्वतःचा ईमेल टाक (ज्याने तू लॉगिन करून पॅसेज ॲड करणार आहेस)
            admin_email = "sureshpatil1712@gmail.com" 
            
            if st.session_state['user_email'] == admin_email:
                st.success("✅ Admin Access Granted!")
                
                st.subheader("नवीन परिच्छेद सिस्टीममध्ये ॲड करा")
                st.info("जेमिनीकडून ४५०-५०० शब्दांचा परिच्छेद तयार करून घ्या आणि खाली पेस्ट करा.")
                
                passage_title = st.text_input("परिच्छेदाचे नाव (उदा. Bombay HC Civil Draft 1)")
                passage_content = st.text_area("परिच्छेदाचा मजकूर (Content)", height=250)
                
                if st.button("Save Passage", type="primary"):
                    if passage_title and passage_content:
                        # शब्दांची संख्या आपोआप मोजणे
                        word_count = len(passage_content.split())
                        
                        try:
                            # Supabase च्या passages टेबलमध्ये डेटा सेव्ह करणे
                            supabase.table("passages").insert({
                                "title": passage_title,
                                "content": passage_content,
                                "word_count": word_count
                            }).execute()
                            
                            st.success(f"🎉 परिच्छेद डेटाबेसमध्ये यशस्वीरित्या सेव्ह झाला! (एकूण शब्द: {word_count})")
                        except Exception as e:
                            st.error("परिच्छेद सेव्ह करताना अडचण आली.")
                    else:
                        st.warning("कृपया परिच्छेदाचे नाव आणि मजकूर दोन्ही भरा.")
            else:
                st.error("🚫 तुम्हाला हे पेज पाहण्याचा अधिकार नाही. (Only Admin Access)")
                
       elif choice == "Typing Test":
            st.title("टायपिंग टेस्ट सुरू करा ⏱️")
            
            # १. डेटाबेसमधून सर्व परिच्छेद (Passages) आणणे
            response = supabase.table("passages").select("*").execute()
            passages_list = response.data
            
            if len(passages_list) == 0:
                st.warning("सध्या कोणताही परिच्छेद उपलब्ध नाही. ॲडमिनने परिच्छेद टाकण्याची वाट पहा.")
            else:
                # २. परिच्छेद निवडण्यासाठी ड्रॉपडाऊन मेनू
                st.subheader("१. सरावासाठी परिच्छेद निवडा:")
                
                # परिच्छेदांची नावे (Titles) लिस्टमध्ये घेणे
                passage_titles = [p['title'] for p in passages_list]
                selected_title = st.selectbox("खालील यादीतून परिच्छेद निवडा:", passage_titles)
                
                # निवडलेल्या परिच्छेदाचा पूर्ण डेटा शोधणे
                selected_passage = next(item for item in passages_list if item["title"] == selected_title)
                
                st.write(f"**एकूण शब्द:** {selected_passage['word_count']} | **वेळ:** १० मिनिटे")
                st.markdown("---")
                
                # ३. परीक्षेचा मोड निवडणे
                st.subheader("२. परीक्षेचा मोड निवडा:")
                exam_mode = st.radio(
                    "तुम्हाला कोणत्या पद्धतीने टेस्ट द्यायची आहे?",
                    ["💻 Online Typing (Screen-to-Screen)", "📄 Paper Typing (Hardcopy-to-Screen)"]
                )
                
                # जर पेपर मोड असेल, तर परिच्छेद दाखवणे (प्रिंट/कॉपी करण्यासाठी)
                if exam_mode == "📄 Paper Typing (Hardcopy-to-Screen)":
                    st.info("टीप: पेपर मोडमध्ये टेस्ट सुरू झाल्यावर स्क्रीनवर परिच्छेद दिसणार नाही. त्यामुळे खालील परिच्छेदाची प्रिंट काढा किंवा वाचण्यासाठी तयार ठेवा.")
                    with st.expander("परिच्छेद पहा आणि कॉपी करा (Print/Copy)"):
                        st.write(selected_passage['content'])
                
                st.markdown("---")
                
                # ४. टेस्ट सुरू करण्याचे बटन
                if st.button("Start Test 🚀", type="primary", use_container_width=True):
                    # हे बटन दाबल्यावर काय होईल, याचे लॉजिक आपण पुढच्या स्टेपमध्ये लिहू
                    st.success("येथून पुढे १० मिनिटांचा टायमर आणि टायपिंग बॉक्स सुरू होईल. (पुढील कोडींग बाकी आहे!)")
if __name__ == '__main__':
    main()
