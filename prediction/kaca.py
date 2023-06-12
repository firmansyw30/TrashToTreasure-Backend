from google.cloud import storage
import os
import tempfile
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tensorflow as tf
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Inisialisasi klien penyimpanan Google Cloud
service_account = 'artful-guru-386801-9390336d684c.json'
client = storage.Client.from_service_account_json(service_account)

# Inisialisasi flask
app = Flask(__name__)

#load model dari file model
bucket_name = 't2t-bucket'
model_kaca_path = 'models/model_kaca.h5'
bucket = client.get_bucket(bucket_name)
blob = bucket.blob(model_kaca_path)
model_kaca_path_local = '/tmp/model_kaca.h5'
blob.download_to_filename(model_kaca_path_local)
loaded_model_kaca = tf.keras.models.load_model(model_kaca_path_local)

# Fungsi untuk mengklasifikasikan gambar kaca dan memberikan rekomendasi
def klasifikasiKaca(image_path):
    # Load dan preprocess gambar
    image = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    image_array = tf.expand_dims(image_array, 0)
    image_array = image_array / 255.0  # Normalisasi

    # Klasifikasikan gambar menggunakan model
    predictions = loaded_model_kaca.predict(image_array)
    predicted_class = tf.argmax(predictions[0])

    # Jawaban dan deskripsi berdasarkan klasifikasi
    answer = ""
    description = ""
    folder_path = ""
    if predicted_class == 0:
        answer = "Botol Kaca."
        description = '''Sampah botol kaca adalah jenis sampah yang terdiri dari botol yang terbuat dari bahan kaca. 
        \tBotol kaca digunakan dalam berbagai industri, seperti industri minuman, kosmetik, dan farmasi. Botol kaca memiliki 
        \tkeunggulan karena dapat digunakan berulang kali dan memiliki sifat yang tahan terhadap pengaruh panas dan zat kimia.\n 
        \tNamun, sampah botol kaca juga dapat menjadi masalah lingkungan jika tidak dikelola dengan baik. Botol kaca yang tidak didaur ulang 
        \tatau dibuang ke tempat sampah yang tepat dapat memakan waktu lama untuk terurai di alam bebas. Selain itu, pecahan botol kaca yang tidak 
        \tditangani dengan hati-hati dapat menjadi bahaya bagi manusia dan hewan.\n
        \tDengan mengadopsi praktik daur ulang yang baik dan pengelolaan sampah yang bertanggung jawab, kita dapat mengurangi dampak negatif 
        \tsampah botol kaca terhadap lingkungan dan memanfaatkan kembali sumber daya kaca yang berharga.\n'''
        folder_path = 'Recomendation/Glass/Botol Kaca'  # Path folder tempat gambar botol kaca disimpan
    elif predicted_class == 1:
        answer = "Kaca."
        description = '''Sampah potongan kaca adalah jenis sampah yang terdiri dari pecahan atau potongan-potongan kaca yang tidak utuh. 
        \tSampah ini bisa berasal dari pecahan botol kaca, jendela kaca, peralatan kaca, atau benda-benda kaca lainnya yang pecah atau rusak.\n
        \tSelain itu, sampah potongan kaca juga memiliki dampak negatif pada lingkungan jika dibuang secara sembarangan. Pecahan kaca yang terbuang 
        \tdi alam bebas dapat mencemari tanah, air, dan ekosistem. Satwa liar juga dapat terluka atau terperangkap oleh pecahan kaca yang terbuang secara tidak benar.\n
        \tDengan penanganan yang hati-hati dan pengelolaan sampah yang tepat, kita dapat mengurangi risiko cedera dan dampak negatif sampah potongan kaca terhadap lingkungan.\n '''
        folder_path = 'Recomendation/Glass/Kaca'  # Path folder tempat gambar kaca disimpan

    #mengembalikan response
    return answer, description, folder_path

#endpoint kaca
@app.route('/kaca', methods=['POST'])
def kaca():
    #periksa apakah ada file gambar yang diunggah
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    #meminta request gambar ke body dengan method form data nantinya di postman
    image = request.files['image']
    # Mendefinisikan path folder 'uploaded-img'
    uploaded_img_folder = 'content/kaca'

    # Membuat folder 'uploaded-img' jika belum ada
    if not os.path.exists(uploaded_img_folder):
        os.makedirs(uploaded_img_folder)

    # Simpan gambar ke folder lokal dengan nama sementara
    temp_image_path = os.path.join(uploaded_img_folder, secure_filename(image.filename))
    image.save(temp_image_path)
    #Simpan gambar ke Google Cloud Storage
    bucket = client.get_bucket(bucket_name)
    image_path = 'uploaded-img/kaca/' + image.filename
    blob = bucket.blob(image_path)
    blob.upload_from_filename(temp_image_path)
    # Dapatkan URL file gambar di Google Cloud Storage
    image_uri = f"gs://{bucket_name}/{image_path}"
    #klasifikasikan gambar, berikan deskripsi dan rekomendasi
    answer, description, folder_path = klasifikasiKaca(image_uri)
    # Hapus file gambar sementara
    image.close()
    blob.delete()
    # Hapus gambar sementara dari folder lokal
    os.remove(temp_image_path)
    #os.remove(image.filename)
    # Dapatkan objek bucket
    bucket = client.get_bucket(bucket_name)
    # Dapatkan daftar file dalam folder
    files = bucket.list_blobs(prefix=folder_path)

    #tampilkan gambar yang sesuai dengan klasifikasi
    if folder_path:
        file_list = os.listdir(folder_path)
        if len(file_list) > 0:
            num_images = len(file_list)
            #menampilkan masing-masing file gambar yang ada digoogle cloud storage folder
            file_urls = []
            for file in files:
                file_urls.append(f"gs://{bucket_name}/{file.name}")
            return jsonify({'answer': answer, 'description': description, 'file_urls': file_urls}), 200
        else:
            return jsonify({'answer': answer, 'description': description, 'file_urls': []}), 200
    else:
        return jsonify({'error': 'No folder found for the classification'}), 500
        

