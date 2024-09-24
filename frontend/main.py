import streamlit as st
import requests
from config import GENERATE_DESCRIPTION_API_URL, FIND_CV_API_URL, app_logger
import base64
import re  # Regular expressions module
import pandas as pd
import altair as alt
import streamlit.components.v1 as components
import uuid
import json
import time  # İlerleme çubukları için gerekli

def get_base64_image(image_file):
    try:
        with open(image_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        app_logger.error(f"Dosya bulunamadı: {image_file}")
        return ""

# Logoyu base64 olarak al
base64_logo = get_base64_image("9138bf7b781c8954841e6ea7757e51cb.png")

# Sayfa başlığı ve altyazısı
st.set_page_config(page_title="LCW PoC - İş Tanımı ve CV Bulucu", page_icon="🛒")

# Logoyu ortalayarak ekle
st.markdown(
    f"""
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{base64_logo}' alt='logo' width='200'>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🛒 LCW PoC - İş Tanımı ve CV Bulucu")
st.caption("🚀 NTT Data Business Solutions Türkiye - Veri Bilimi Ekibi tarafından desteklenmektedir")

# Dil seçimi
language = st.sidebar.selectbox("Dil Seçimi", ["Türkçe", "English"])

# Yardım bölümü
with st.sidebar.expander("ℹ️ Nasıl Kullanılır?"):
    st.write("""
    1. **İş Tanımı Oluşturucu** sekmesinde nitelikleri ve rol tanımını girin.
    2. **CV Yükleme ve En Uygun CV'yi Bulma** sekmesinde iş tanımını girin ve CV dosyalarını yükleyin.
    3. **En Uygun CV'yi Bul** butonuna tıklayın ve sonuçları görün.
    """)

# Sekmeler oluştur
tabs = st.tabs(["📝 İş Tanımı Oluşturucu", "📂 CV Yükleme ve CV Eşleştirici", "💬 Geri Bildirim"])

# -------------------- Sekme 1: İş Tanımı Oluşturucu --------------------
with tabs[0]:
    st.header("📝 İş Tanımı Oluşturucu")

    # Örnek verileri yükleme fonksiyonu
    def load_sample_data():
        st.session_state['qualifications'] = "Python, Veri Analizi, Makine Öğrenimi"
        st.session_state['role_definition'] = "Veri Bilimcisi olarak veri analizi ve modelleme"

    # Örnek verileri yükle butonu
    if st.button("📄 Örnek Verileri Yükle"):
        load_sample_data()

    with st.form(key='job_description_form'):
        col1, col2 = st.columns(2)
        with col1:
            qualifications = st.text_area(
                "Nitelikler",
                placeholder="Örneğin: Python, Veri Analizi, Makine Öğrenimi...",
                key='qualifications'
            )
        with col2:
            role_definition = st.text_area(
                "Rol Tanımı",
                placeholder="Örneğin: Veri Bilimcisi olarak veri analizi ve modelleme...",
                key='role_definition'
            )
        experience_level = st.slider("Deneyim Seviyesi (Yıl)", 0, 10, 3)
        department = st.selectbox("Departman Seçimi", ["IT", "İnsan Kaynakları", "Pazarlama"])
        generate_description_button = st.form_submit_button(label='💡 İş Tanımını Oluştur')

    # İş tanımı oluşturma süreci
    if generate_description_button:
        job_description_payload = {
            "qualifications": qualifications,
            "role_definition": role_definition,
            "experience_level": experience_level,
            "department": department
        }

        progress_bar = st.progress(0)  # İlerleme çubuğunu başlat
        status_text = st.empty()       # Durum mesajı için boş bir yer ayır

        try:
            status_text.text("İş Tanımı Oluşturuluyor...")
            # İlerleme çubuğunu simüle et
            # API çağrısı tamamlanana kadar ilerleme çubuğunu yavaşça doldur
            for percent_complete in range(10, 100, 10):
                progress_bar.progress(percent_complete)
                time.sleep(0.02)  # Gerçek zamanlı ilerleme için bekleme

            with st.spinner('İş Tanımı Oluşturuluyor...'):
                app_logger.info("İş tanımı oluşturma isteği gönderiliyor")
                response = requests.post(GENERATE_DESCRIPTION_API_URL, json=job_description_payload)
                response_data = response.json()

            if response.status_code == 200:
                job_description = response_data.get("job_description", "İş tanımı oluşturulamadı.")
                st.success("✅ İş Tanımı Başarıyla Oluşturuldu!")

                # İş tanımını st.write ile görüntüleme
                st.write(job_description)

                # `job_description` metnini güvenli bir şekilde JSON formatında encode et
                escaped_job_description = json.dumps(job_description)

                # HTML ve JavaScript ile Kopyalama Butonu
                copy_button_html = f"""
                <button onclick="copyText()" style="padding: 10px 20px; font-size: 16px; cursor: pointer;">
                    📋 İş Tanımını Kopyala
                </button>
                <script>
                function copyText() {{
                    const text = {escaped_job_description};
                    navigator.clipboard.writeText(text).then(function() {{
                        alert('İş tanımı panoya kopyalandı!');
                    }}, function(err) {{
                        alert('Kopyalama işlemi başarısız: ' + err);
                    }});
                }}
                </script>
                """

                # Render the copy button
                components.html(copy_button_html, height=60)

                # İndir Butonu
                st.download_button(
                    label="📥 İş Tanımını İndir",
                    data=job_description,
                    file_name="is_tanimi.txt"
                )
            else:
                st.error("❌ İş tanımı oluşturulamadı. Lütfen tekrar deneyin.")
        except Exception as e:
            app_logger.error(f"Bir hata oluştu: {e}")
            st.error(f"Bir hata oluştu: {e}. Lütfen daha sonra tekrar deneyin veya destek ekibiyle iletişime geçin.")
        finally:
            progress_bar.progress(100)  # İlerleme çubuğunu tamamla
            time.sleep(0.5)
            progress_bar.empty()  # İlerleme çubuğunu kaldır
            status_text.empty()    # Durum mesajını kaldır

# -------------------- Contact Info Parsing Function --------------------
def parse_contact_info(contact_info_str):
    """
    contact_info string'ini parse eder ve standartlaştırılmış anahtarlarla bir sözlük döner.
    """
    contact_info = {
        'Telefon': 'Bilgi yok',
        'E-posta': 'Bilgi yok',
        'Adres': 'Bilgi yok'
    }

    # Markdown ve gereksiz karakterleri temizle
    text = contact_info_str.replace('*', '').replace('-', '').replace('_', '').strip()

    # Telefon, Email ve Adres için regex desenleri
    phone_patterns = [
        r'Phone Number[: ]*(.+)', r'Phone[: ]*(.+)', r'Telefon[: ]*(.+)'
    ]
    email_patterns = [
        r'Email[: ]*(.+)', r'E-posta[: ]*(.+)', r'E-mail[: ]*(.+)'
    ]
    address_patterns = [
        r'Address[: ]*(.+)', r'Adres[: ]*(.+)'
    ]

    # Başlıkları kaldır
    text = re.sub(r'Contact Information[:]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'İletişim Bilgileri[:]*', '', text, flags=re.IGNORECASE)

    # Satırları böl
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        # Telefon kontrolü
        for pattern in phone_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                contact_info['Telefon'] = match.group(1).strip()
                break
        # Email kontrolü
        for pattern in email_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                contact_info['E-posta'] = match.group(1).strip()
                break
        # Adres kontrolü
        for pattern in address_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                contact_info['Adres'] = match.group(1).strip()
                break

    return contact_info

# -------------------- Sekme 2: CV Yükleme ve CV Eşleştirici --------------------
with tabs[1]:
    st.header("📂 CV Yükleme ve En Uygun CV'yi Bulma")

    # Geçici dosya yükleyici anahtarı
    if 'file_uploader_key' not in st.session_state:
        st.session_state['file_uploader_key'] = 0

    # Dosyaları sıfırla butonu
    if st.button('📁 Dosyaları Sıfırla'):
        st.session_state['file_uploader_key'] += 1

    # Dosya yükleyici
    uploaded_pdfs = st.file_uploader(
        "CV PDF'lerini Yükleyin",
        accept_multiple_files=True,
        type=["pdf"],
        key=st.session_state['file_uploader_key']
    )

    with st.form(key='cv_finder_form'):
        job_description_input = st.text_area(
            "İş Tanımı",
            placeholder="İş tanımını buraya girin veya yukarıdaki sekmeden oluşturulan iş tanımını kullanın..."
        )
        find_cv_button = st.form_submit_button(label='🔍 En Uygun CV\'yi Bul')

    # En Uygun CV'yi Bulma Süreci
    if find_cv_button:
        if uploaded_pdfs and job_description_input:
            # POST isteği için dosya ve veri hazırlığı
            files = [('cv_pdfs', (pdf.name, pdf, 'application/pdf')) for pdf in uploaded_pdfs]
            data = {'job_description': job_description_input}

            # Yüklenen dosya sayısını logla
            app_logger.info(f"Yüklenen dosya sayısı: {len(uploaded_pdfs)}")

            progress_bar = st.progress(0)  # İlerleme çubuğunu başlat
            status_text = st.empty()       # Durum mesajı için boş bir yer ayır

            try:
                status_text.text("CV'ler İşleniyor...")
                total_pdfs = len(uploaded_pdfs)
                progress_increment = 100 / (total_pdfs + 1)  # +1 API çağrısı için

                # Her bir PDF'yi işleyerek ilerleme çubuğunu güncelle
                for i, pdf in enumerate(uploaded_pdfs, 1):
                    # Burada gerçek PDF işleme kodunuz olmalı
                    # Örneğin, her PDF'yi sunucuya gönderip işliyorsanız, burada bekleme süresi olabilir
                    # Bu örnekte, sadece simülasyon için time.sleep kullanıyoruz
                    time.sleep(0.2)  # PDF işleme süresini simüle et
                    progress_bar.progress(int(i * progress_increment))
                    status_text.text(f"İşleniyor: {pdf.name}")

                # API çağrısı için ilerlemeyi güncelle
                progress_bar.progress(int((total_pdfs + 1) * progress_increment))
                status_text.text("En uygun CV'ler aranıyor...")

                with st.spinner('En Uygun CV Aranıyor...'):
                    app_logger.info("En uygun CV'yi bulma isteği gönderiliyor")
                    response = requests.post(FIND_CV_API_URL, data=data, files=files)
                    app_logger.info(f"Cevap durumu: {response.status_code}")

                    response_data = response.json()

                if response.status_code == 200:
                    # En uygun CV'lerin listesi
                    top_cvs = response_data.get("cv_list", [])
                    if top_cvs:
                        st.success("✅ En Uygun CV'ler Bulundu!")

                        # En üst 10 CV'yi al
                        top_10_cvs = top_cvs[:10]

                        # Her bir CV'yi bireysel olarak göster
                        for i, cv in enumerate(top_10_cvs):
                            st.subheader(f"{i + 1}. {cv['cv_name']}")
                            st.write(f"**Benzerlik Skoru (%):** {round(cv['similarity_score'] * 100, 2)}")
                            contact_info_str = cv.get('contact_info', 'Bilgi yok')

                            # İletişim bilgilerini parse et
                            contact_info = parse_contact_info(contact_info_str)

                            # İletişim bilgilerini formatla
                            st.write("**İletişim Bilgileri:**")
                            st.write(f"- **Telefon:** {contact_info['Telefon']}")
                            st.write(f"- **E-posta:** {contact_info['E-posta']}")
                            st.write(f"- **Adres:** {contact_info['Adres']}")
                            st.write("---")  # Ayırıcı çizgi

                        # Grafik oluştur
                        chart_data = pd.DataFrame({
                            'CV Adı': [cv['cv_name'] for cv in top_10_cvs],
                            'Benzerlik Skoru (%)': [round(cv['similarity_score'] * 100, 2) for cv in top_10_cvs]
                        })

                        chart = alt.Chart(chart_data).mark_bar().encode(
                            x=alt.X('Benzerlik Skoru (%)', sort='-y'),
                            y=alt.Y('CV Adı', sort='-x')
                        )

                        st.altair_chart(chart, use_container_width=True)

                    else:
                        st.error("❌ Uygun bir CV bulunamadı.")
                else:
                    st.error(f"❌ En uygun CV bulunamadı. Durum kodu: {response.status_code}")
            except Exception as e:
                app_logger.error(f"Bir hata oluştu: {e}")
                st.error(f"Bir hata oluştu: {e}. Lütfen daha sonra tekrar deneyin veya destek ekibiyle iletişime geçin.")
            finally:
                time.sleep(0.5)
                progress_bar.empty()  # İlerleme çubuğunu kaldır
                status_text.empty()    # Durum mesajını kaldır
        else:
            st.error("Lütfen bir iş tanımı girin ve en az bir CV PDF dosyası yükleyin.")

# -------------------- Sekme 3: Geri Bildirim --------------------
with tabs[2]:
    st.header("💬 Geri Bildirim")
    feedback = st.text_input("Uygulama hakkında geri bildirimlerinizi paylaşın:")
    if st.button("Gönder"):
        if feedback.strip():
            # Geri bildirimi işleme kodu
            # Örneğin, bir API'ye göndermek veya bir veri tabanına kaydetmek
            app_logger.info(f"Geri Bildirim alındı: {feedback}")
            st.success("Geri bildiriminiz için teşekkür ederiz!")
        else:
            st.error("Lütfen geri bildiriminizi yazın.")

# -------------------- Altbilgi ve Gizlilik Bilgisi --------------------
st.markdown(
    """
    ---
    🔒 Yüklediğiniz dosyalar güvende tutulmaktadır ve üçüncü taraflarla paylaşılmaz.
    """,
    unsafe_allow_html=True
)
