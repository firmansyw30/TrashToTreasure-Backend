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
model_metal_path = 'models/model_metal.h5'
bucket = client.get_bucket(bucket_name)
blob = bucket.blob(model_metal_path)
model_metal_path_local = '/tmp/model_metal.h5'
blob.download_to_filename(model_metal_path_local)
loaded_model_metal = tf.keras.models.load_model(model_metal_path_local)

# Fungsi untuk mengklasifikasikan gambar metal dan memberikan rekomendasi
def klasifikasiMetal(image_path):
    # Load dan preprocess gambar
    image = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    image_array = tf.expand_dims(image_array, 0)
    image_array = image_array / 255.0  # Normalisasi

    # Klasifikasikan gambar menggunakan model
    predictions = loaded_model_metal.predict(image_array)
    predicted_class = tf.argmax(predictions[0])

    # Jawaban dan deskripsi berdasarkan klasifikasi
    answer = ""
    description = ""
    folder_path = ""
    if predicted_class == 0:
        answer = "Aluminium Foil."
        description = '''Sampah aluminium foil adalah jenis sampah yang terdiri dari lembaran aluminium tipis yang digunakan 
        \tuntuk membungkus atau melindungi makanan, mengemas produk, atau digunakan dalam berbagai keperluan lainnya. Aluminium foil 
        \tmemiliki sifat yang fleksibel, ringan, dan tahan terhadap panas.\n
        \tSampah aluminium foil dapat terbentuk saat aluminium foil digunakan sekali pakai dan kemudian dibuang. Aluminium foil yang terbuang 
        \tsecara tidak tepat dapat mencemari lingkungan jika tidak dikelola dengan baik.\n
        \tNamun, aluminium foil juga memiliki potensi untuk didaur ulang. Aluminium merupakan salah satu jenis logam yang bisa didaur ulang dengan baik dan efisien. 
        \tMelalui proses daur ulang, aluminium foil yang terbuang dapat dikumpulkan, dipilah, dan diproses untuk digunakan kembali dalam pembuatan produk aluminium baru.\n
        \tPenting untuk membuang sampah aluminium foil ke tempat sampah daur ulang atau fasilitas daur ulang yang tersedia di komunitas. 
        \tMengedukasi diri sendiri dan masyarakat tentang pentingnya daur ulang aluminium foil dan mengelola sampah dengan benar adalah langkah penting dalam menjaga 
        \tkeberlanjutan lingkungan dan mengurangi pemborosan sumber daya.\n '''
        folder_path = 'Recomendation/Metal/Aluminium Foil'  # Path folder tempat gambar aluminium disimpan
    elif predicted_class == 1:
        answer = "Kaleng."
        description = '''Sampah kaleng adalah jenis sampah yang terdiri dari kaleng logam yang digunakan untuk mengemas minuman, makanan, atau produk-produk lainnya. 
        \tKaleng umumnya terbuat dari aluminium atau besi yang dilapisi dengan lapisan pelindung untuk mencegah korosi.\n
        \tSampah kaleng dapat mencakup kaleng minuman seperti minuman ringan, bir, atau kaleng makanan seperti kaleng sarden, kacang, atau makanan kaleng lainnya. 
        \tKaleng memiliki keunggulan sebagai kemasan karena ringan, mudah diolah, dan dapat memperpanjang umur simpan produk.\n
        \tPenting untuk mencermati pengelolaan sampah kaleng, karena mereka memiliki potensi untuk didaur ulang dengan sangat efisien. 
        \tKaleng logam merupakan salah satu jenis bahan yang paling umum didaur ulang di seluruh dunia. Proses daur ulang kaleng melibatkan pengumpulan, pemilahan, 
        \tpemrosesan, dan pengecoran ulang menjadi produk logam baru.\n
        \tDengan mendaur ulang sampah kaleng, kita dapat mengurangi kebutuhan akan bahan mentah baru dan mengurangi dampak lingkungan yang terkait dengan produksi logam baru. 
        \tSelain itu, daur ulang kaleng juga membantu mengurangi limbah yang masuk ke tempat pembuangan akhir.\n
        \tPenting untuk memisahkan sampah kaleng dari sampah lainnya dan membuangnya di tempat sampah daur ulang yang disediakan oleh pemerintah atau fasilitas daur ulang di komunitas. 
        \tDengan memastikan bahwa sampah kaleng terdaur ulang dengan benar, kita dapat membantu menjaga keberlanjutan lingkungan dan mengurangi pemakaian sumber daya alam yang berharga.\n '''
        folder_path = 'Recomendation/Metal/Kaleng'  # Path folder tempat gambar kaleng disimpan

    #mengembalikan response
    return answer, description, folder_path

#endpoint metal
@app.route('/metal', methods=['POST'])
def metal():
    #periksa apakah ada file gambar yang diunggah
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    #meminta request gambar ke body dengan method form data nantinya di postman
    image = request.files['image']
    # Mendefinisikan path folder 'uploaded-img'
    uploaded_img_folder = 'content/metal'

    # Membuat folder 'uploaded-img' jika belum ada
    if not os.path.exists(uploaded_img_folder):
        os.makedirs(uploaded_img_folder)

    # Simpan gambar ke folder lokal dengan nama sementara
    temp_image_path = os.path.join(uploaded_img_folder, secure_filename(image.filename))
    image.save(temp_image_path)
    # Simpan gambar ke Google Cloud Storage
    bucket = client.get_bucket(bucket_name)
    image_path = 'uploaded-img/metal/' + image.filename
    blob = bucket.blob(image_path)
    blob.upload_from_filename(temp_image_path)
    
    # Dapatkan URL file gambar di Google Cloud Storage
    image_uri = f"gs://{bucket_name}/{image_path}"

    #klasifikasikan gambar, berikan deskripsi dan rekomendasi
    answer, description, folder_path = klasifikasiMetal(image_uri)
    # Hapus file gambar sementara
    image.close()
    blob.delete()
    # Hapus gambar sementara dari folder lokal
    os.remove(temp_image_path)
    #remove model setelah digunakan
    #os.remove(model_metal_path_local)
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

