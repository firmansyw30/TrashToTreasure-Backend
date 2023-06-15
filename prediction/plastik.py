from google.cloud import storage
import os
import io
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tensorflow as tf
import tempfile
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image

# Inisialisasi klien penyimpanan Google Cloud
service_account = 'credential/artful-guru-386801-9390336d684c.json'
client = storage.Client.from_service_account_json(service_account)

# Inisialisasi flask
app = Flask(__name__)

#load model dari file model
bucket_name = 't2t-bucket'
model_plastik_path = 'models/model_plastik.h5'
bucket = client.get_bucket(bucket_name)
blob = bucket.blob(model_plastik_path)
model_plastik_path_local = '/tmp/model_plastik.h5'
blob.download_to_filename(model_plastik_path_local)
loaded_model_plastik = tf.keras.models.load_model(model_plastik_path_local)

# Fungsi untuk mengklasifikasikan gambar plastik dan memberikan rekomendasi
def klasifikasiPlastik(image_path):
    # Load dan preprocess gambar
    image = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    image_array = tf.expand_dims(image_array, 0)
    image_array = image_array / 255.0  # Normalisasi

    # Klasifikasikan gambar menggunakan model
    predictions = loaded_model_plastik.predict(image_array)
    predicted_class = tf.argmax(predictions[0])

    # Jawaban dan deskripsi berdasarkan klasifikasi
    answer = ""
    description = ""
    folder_path = ""
    if predicted_class == 0:
        answer = "Botol Plastik."
        description = '''Botol plastik merupakan salah satu jenis sampah yang sangat umum ditemui dalam kehidupan sehari-hari.
        \tBotol plastik umumnya terbuat dari polietilen tereftalat (PET), yang merupakan jenis plastik yang dapat didaur ulang.
        \tDaur ulang botol plastik memiliki manfaat besar bagi lingkungan karena mengurangi penggunaan bahan baku baru, 
        \tmengurangi limbah plastik yang mencemari lingkungan, dan menghemat energi yang diperlukan dalam produksi plastik baru. 
        \tOleh karena itu, penting bagi kita semua untuk mempraktikkan daur ulang botol plastik dengan membuangnya ke tempat yang benar 
        \tdan mendukung program daur ulang yang ada di lingkungan kita.\n'''
        folder_path = 'Recomendation/Plastik/Botol'  # Path folder tempat gambar botol disimpan
    elif predicted_class == 1:
        answer = "Kemasan Plastik."
        description = '''Sampah kemasan plastik merupakan jenis sampah yang terkait dengan penggunaan berbagai macam kemasan plastik dalam kehidupan sehari-hari.
        \tKemasan plastik umumnya digunakan untuk mengemas makanan, minuman, produk rumah tangga, produk kecantikan, dan berbagai produk lainnya.
        \tSampah kemasan plastik dapat berdampak negatif terhadap lingkungan dan ekosistem. Jika tidak dikelola dengan baik, kemasan plastik bisa mencemari lautan,
        \tsungai, dan lahan. Plastik yang terbuang sembarangan dapat merusak habitat alami dan menyebabkan keracunan pada hewan laut yang memakan atau terperangkap olehnya. 
        \tSelain itu, pembakaran atau pembuangan plastik yang tidak tepat juga dapat menghasilkan polusi udara dan tanah yang berbahaya.\n
        \tUpaya kolektif dari individu, pemerintah, dan industri dalam mengurangi penggunaan kemasan plastik sekali pakai, meningkatkan daur ulang, 
        \tserta meningkatkan inovasi dalam pengemasan yang ramah lingkungan dapat membantu mengurangi masalah sampah kemasan plastik dan menjaga keberlanjutan lingkungan kita.\n'''
        folder_path = 'Recomendation/Plastik/Kemasan'  # Path folder tempat gambar kemasan disimpan
    elif predicted_class == 2:
        answer = "Sedotan."
        description = '''Sampah sedotan plastik adalah jenis sampah yang terdiri dari sedotan atau pipet kecil yang terbuat dari plastik. 
        \tSedotan plastik umumnya digunakan untuk minuman seperti jus, soda, atau minuman ringan lainnya.\n
        \tMeskipun sedotan plastik terlihat kecil dan tidak signifikan, mereka dapat menjadi masalah lingkungan yang serius. 
        \tIni karena sedotan plastik sulit terurai dan cenderung berakhir sebagai sampah plastik yang mencemari lautan dan ekosistem.\n 
        \tDengan kesadaran dan tindakan kolektif, penggunaan dan pembuangan sedotan plastik sekali pakai dapat dikurangi secara signifikan. 
        \tMenggantinya dengan alternatif yang lebih berkelanjutan dan mengelola sampah sedotan plastik dengan benar adalah langkah penting 
        \tdalam menjaga keberlanjutan lingkungan kita.\n'''
        folder_path = 'Recomendation/Plastik/Sedotan'  # Path folder tempat gambar sedotan disimpan
    elif predicted_class == 3:
        answer = "Sendok."
        description = '''Sampah sendok plastik adalah jenis sampah yang terdiri dari sendok kecil yang terbuat dari plastik. 
        \tSendok plastik sering digunakan dalam berbagai acara atau makanan makanan siap saji yang dikonsumsi di luar rumah.\n 
        \tSampah sendok plastik memiliki dampak negatif pada ekosistem laut dan lingkungan secara keseluruhan. Satwa laut dapat tersangkut 
        \tatau memakan sendok plastik, yang dapat menyebabkan luka atau kematian. Selain itu, pembuangan sendok plastik yang tidak tepat juga 
        \tdapat menyebabkan pencemaran tanah dan air.\n
        \tDengan mengadopsi alternatif yang lebih ramah lingkungan dan mengelola sendok plastik dengan benar, kita dapat mengurangi dampak negatifnya 
        \tterhadap lingkungan dan menjaga keberlanjutan sumber daya alam kita.\n'''
        folder_path = 'Recomendation/Plastik/Sendok'  # Path folder tempat gambar sendok disimpan

    #mengembalikan response
    return answer, description, folder_path

#endpoint plastik
@app.route('/plastik', methods=['POST'])
def plastik():
    #periksa apakah ada file gambar yang diunggah
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    #meminta request gambar ke body dengan method form data nantinya di postman
    image = request.files['image']
    # Save the uploaded image to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    image.save(temp_file.name)
    #klasifikasi
    answer, description, folder_path = klasifikasiPlastik(temp_file.name)
    os.remove(temp_file.name)
    # Dapatkan objek bucket
    bucket = client.get_bucket(bucket_name)
    # Dapatkan daftar file dalam folder
    blobs = bucket.list_blobs(prefix=folder_path)

    #tampilkan gambar yang sesuai dengan klasifikasi
    file_urls = []
    for blob in blobs:
        file_url = f"https://storage.googleapis.com/{bucket_name}/{blob.name}"
        file_urls.append(file_url)
    if len(file_urls) > 0:
        return jsonify({'answer': answer, 'description': description, 'file_urls': file_urls}), 200
    else:
        return jsonify({'answer': answer, 'description': description, 'file_urls': []}), 200

    return jsonify({'error': 'No folder found for the classification'}), 500

