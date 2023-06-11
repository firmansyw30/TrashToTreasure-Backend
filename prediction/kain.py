from google.cloud import storage
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tensorflow as tf
from flask import Flask, request, jsonify

# Inisialisasi klien penyimpanan Google Cloud
service_account = 'nama-file-services-account.json'
client = storage.Client.from_service_account_json(service_account)

# Inisialisasi flask
app = Flask(__name__)

#load model dari file model
bucket_name = 'nama-bucket'
model_kain_path = 'models/model_kain.h5'
bucket = client.get_bucket(bucket_name)
blob = bucket.blob(model_kain_path)
model_kain_path_local = '/tmp/model_kain.h5'
blob.download_to_filename(model_kain_path_local)
loaded_model_kain = tf.keras.models.load_model(model_kain_path_local)

# Fungsi untuk mengklasifikasikan gambar kain dan memberikan rekomendasi
def klasifikasiKain(image_path):
    # Load dan preprocess gambar
    image = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    image_array = tf.expand_dims(image_array, 0)
    image_array = image_array / 255.0  # Normalisasi

    # Klasifikasikan gambar menggunakan model
    predictions = loaded_model_kain.predict(image_array)
    predicted_class = tf.argmax(predictions[0])

    # Jawaban dan deskripsi berdasarkan klasifikasi
    answer = ""
    description = ""
    folder_path = ""
    if predicted_class == 0:
        answer = "Kain."
        description = '''Sampah kain adalah jenis sampah yang terdiri dari potongan-potongan atau sisa-sisa kain yang tidak lagi digunakan atau rusak. 
        \tSampah kain dapat berasal dari pakaian bekas yang tidak terpakai, kain sisa dari proses produksi, atau barang-barang tekstil yang rusak.\n 
        \tKain merupakan bahan yang umum digunakan dalam berbagai produk seperti pakaian, kain penutup, furnitur, dan lain sebagainya. 
        \tNamun, ketika kain tidak lagi digunakan atau rusak, mereka dapat menjadi sumber limbah yang signifikan.\n
        \tPenting untuk membuang sampah kain dengan benar, baik dengan mendaur ulang atau membuangnya ke tempat sampah yang sesuai. 
        \tMengurangi pemborosan kain dan memperpanjang siklus hidup kain dapat membantu mengurangi dampak negatif pada lingkungan dan mengurangi 
        \tpenggunaan sumber daya alam yang berharga.\n'''
        folder_path = 'Recomendation/Kain/Kain'  # Path folder tempat gambar aluminium disimpan
    elif predicted_class == 1:
        answer = "Organik."
        description = '''Sampah organik adalah jenis sampah yang terdiri dari bahan-bahan yang berasal dari sisa-sisa organisme hidup, seperti sisa makanan, 
        \tdaun, ranting, kulit buah, sayuran yang busuk, atau limbah pertanian. Sampah organik terutama terdiri dari bahan-bahan yang dapat terdekomposisi 
        \tsecara alami oleh mikroorganisme/\n
        \tSampah organik memiliki sifat yang mudah membusuk dan dapat menghasilkan gas metana saat terurai dalam kondisi anaerobik (tanpa oksigen). 
        \tJumlah sampah organik yang terbuang secara tidak tepat ke tempat pembuangan akhir dapat menyebabkan peningkatan emisi gas rumah kaca dan 
        \tmenciptakan masalah lingkungan.\n
        \tNamun, sampah organik juga memiliki potensi untuk didaur ulang melalui proses pengomposan. Pengomposan adalah proses alami di mana sampah organik 
        \tterurai oleh mikroorganisme menjadi bahan yang berguna yang disebut kompos. Kompos ini dapat digunakan sebagai pupuk alami untuk meningkatkan 
        \tkesuburan tanah di kebun atau taman.\n
        \tPengelolaan yang tepat terhadap sampah organik dapat membantu mengurangi jumlah sampah yang dikirim ke tempat pembuangan akhir, mengurangi emisi 
        \tgas rumah kaca, dan menghasilkan sumber daya yang bernilai dari bahan organik yang terdekomposisi.\n'''
        folder_path = 'Recomendation/Kain/Organik'  # Path folder tempat gambar kaleng disimpan

    #mengembalikan response
    return answer, description, folder_path

#endpoint kain
@app.route('/kain', methods=['POST'])
def kain():
    #periksa apakah ada file gambar yang diunggah
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    #meminta request gambar ke body dengan method form data nantinya di postman
    image = request.files['image']

    #simpan gambar ke direktori sementara
    temp_image_path = 'content/temp_image.jpg'
    image.save(temp_image_path)

    #klasifikasikan gambar, berikan deskripsi dan rekomendasi
    answer, description, folder_path = klasifikasiKain(temp_image_path)

    #hapus file gambar sementara
    os.remove(temp_image_path)
    #remove model setelah digunakan
    #os.remove(model_kain_path_local)
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

