
# 💻 PENERAPAN PERCABANGAN DALAM BAHASA PEMROGRAMAN KOTLIN PADA ANDROID STUDIO

**SMK N 2 YOGYAKARTA**  
**Jurusan:** Sistem Informasi Jaringan dan Aplikasi (SIJA)  
**Laboratorium Komputer**  

---

## 🎯 KOMPETENSI

- Memahami konsep percabangan (branching) pada bahasa pemrograman **Kotlin**.  
- Mampu menerapkan struktur percabangan **if**, **if–else**, dan **when** dalam pemrograman Android Studio.  
- Mengembangkan logika percabangan untuk menyelesaikan **masalah sederhana** pada aplikasi Android.

---

## 📚 SUB-KOMPETENSI

1. Menjelaskan jenis-jenis percabangan pada Kotlin.  
2. Menulis sintaks percabangan sesuai aturan Kotlin.  
3. Menggunakan percabangan untuk membuat alur keputusan dalam aplikasi Android sederhana.

---

## 🧠 DASAR TEORI

Percabangan adalah struktur program yang memungkinkan program **menentukan alur eksekusi** berdasarkan **kondisi tertentu (true/false)**.

Dalam Kotlin, percabangan membantu program **membuat keputusan otomatis**, seperti menentukan nilai siswa, menampilkan kategori, atau memilih tindakan tertentu.

Jenis percabangan utama dalam Kotlin:

1. **if** → Menjalankan pernyataan jika kondisi bernilai *true*.  
2. **if–else** → Menjalankan salah satu dari dua pernyataan tergantung hasil kondisi.  
3. **if–else if–else** → Menangani beberapa kondisi secara bertingkat.  
4. **when** → Alternatif dari `switch` di Java, dengan sintaks yang lebih sederhana.

---

## ⚙️ ALAT DAN BAHAN

| No | Alat / Bahan | Keterangan |
|----|---------------|------------|
| 1  | Android Studio | IDE utama pengembangan aplikasi Kotlin |
| 2  | SDK Android & AVD | Simulasi perangkat Android |
| 3  | Laptop / PC | Media coding dan kompilasi |
| 4  | Perangkat Android / Emulator | Pengujian aplikasi |
| 5  | Koneksi Internet | Sinkronisasi Gradle dan dependensi |

---

## 🦺 KESELAMATAN KERJA

1. Gunakan komputer dan perangkat sesuai petunjuk.  
2. Pastikan semua kabel dan koneksi listrik aman.  
3. Hindari menyentuh stopkontak atau kabel dengan tangan basah.  
4. Ikuti instruksi kerja secara berurutan.  
5. Pastikan komputer dalam kondisi baik sebelum memulai pekerjaan.

---

## 🧩 LANGKAH KERJA

### 1️⃣ Membuat Project Baru

1. Buka **Android Studio** → Klik **“Start a new Android Studio project”**.  
2. Pilih **Empty Views Activity** → Klik **Next**.  
3. Isi data berikut:
   - **Name:** NamaPercabangan  
   - **Package Name:** com.example.namapercabangan  
   - **Language:** Kotlin  
   - **Minimum SDK:** API 21 (Lollipop)  
4. Klik **Finish**.

---

### 2️⃣ Mendesain Layout (`activity_main.xml`)

Buka file `activity_main.xml`, lalu isi dengan komponen seperti berikut:

```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">

    <TextView
        android:id="@+id/txtTitle"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Percabangan Kotlin"
        android:textSize="22sp"
        android:textStyle="bold"
        android:layout_gravity="center"
        android:paddingBottom="16dp"/>

    <EditText
        android:id="@+id/edtInput"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Masukkan angka/nilai"
        android:inputType="number"/>

    <Button android:id="@+id/btnIf" android:text="Cek dengan IF" ... />
    <Button android:id="@+id/btnIfElse" android:text="Cek dengan IF ELSE" ... />
    <Button android:id="@+id/btnIfElseIf" android:text="Cek dengan IF ELSE-IF ELSE" ... />
    <Button android:id="@+id/btnWhen" android:text="Cek dengan WHEN" ... />

    <TextView
        android:id="@+id/txtResult"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Hasil akan tampil di sini"
        android:textSize="18sp"
        android:gravity="center"/>
</LinearLayout>
````

---

### 3️⃣ Menulis Kode di `MainActivity.kt`

Hubungkan komponen UI ke kode Kotlin:

```kotlin
val edtInput = findViewById<EditText>(R.id.edtInput)
val txtResult = findViewById<TextView>(R.id.txtResult)
val btnIf = findViewById<Button>(R.id.btnIf)
val btnIfElse = findViewById<Button>(R.id.btnIfElse)
val btnIfElseIf = findViewById<Button>(R.id.btnIfElseIf)
val btnWhen = findViewById<Button>(R.id.btnWhen)
```

> Kode di atas berfungsi menghubungkan elemen dari layout ke logika Kotlin agar dapat diakses dalam program.

---

## 🧮 JENIS PERCABANGAN DALAM KOTLIN

### ✅ IF

```kotlin
btnIf.setOnClickListener {
    val input = edtInput.text.toString().toIntOrNull()
    if (input != null && input > 50) {
        txtResult.text = "IF: Angka lebih besar dari 50"
    }
}
```

➡ Mengeksekusi kode hanya jika kondisi benar (`true`).

---

### ✅ IF–ELSE

```kotlin
btnIfElse.setOnClickListener {
    val input = edtInput.text.toString().toIntOrNull()
    if (input != null) {
        if (input >= 75)
            txtResult.text = "Nilai Memuaskan"
        else
            txtResult.text = "Nilai Belum Memuaskan"
    }
}
```

➡ Menjalankan dua pilihan: jika benar (true) dan jika salah (false).

---

### ✅ IF–ELSE IF–ELSE

```kotlin
btnIfElseIf.setOnClickListener {
    val input = edtInput.text.toString().toIntOrNull()
    if (input != null) {
        val hasil = if (input >= 85) "A"
        else if (input >= 70) "B"
        else if (input >= 55) "C"
        else "D"
        txtResult.text = "Nilai = $hasil"
    }
}
```

➡ Digunakan untuk beberapa kondisi bertingkat, misalnya penilaian huruf A–D.

---

### ✅ WHEN

```kotlin
btnWhen.setOnClickListener {
    val input = edtInput.text.toString().toIntOrNull()
    if (input != null) {
        val hari = when (input) {
            1 -> "Minggu"
            2 -> "Senin"
            3 -> "Selasa"
            4 -> "Rabu"
            5 -> "Kamis"
            6 -> "Jumat"
            7 -> "Sabtu"
            else -> "Bukan nama hari"
        }
        txtResult.text = "WHEN: $hari"
    }
}
```

➡ `when` digunakan sebagai pengganti `switch` pada Java untuk pemilihan kondisi sederhana.

---

## ⚡ PERBANDINGAN WHEN EXPRESSION VS STATEMENT

### 🧾 Expression

```kotlin
val hasil = when (input) {
    1 -> "x == 1"
    2 -> "x == 2"
    else -> "x is neither 1 nor 2"
}
txtResult.text = "WHEN Expression: $hasil"
```

* `when` menghasilkan **nilai yang bisa disimpan ke variabel**.

---

### 🧾 Statement

```kotlin
when (input) {
    1 -> txtResult.text = "x == 1"
    2 -> txtResult.text = "x == 2"
    else -> txtResult.text = "x is neither 1 nor 2"
}
```

* `when` **tidak menghasilkan nilai**, hanya mengeksekusi aksi tertentu.

---

## 🌀 WHEN TANPA SUBJEK

```kotlin
when {
    input > 100 -> txtResult.text = "Angka lebih besar dari 100"
    input in 50..100 -> txtResult.text = "Angka antara 50-100"
    else -> txtResult.text = "Angka kurang dari 50"
}
```

* `when` digunakan tanpa variabel, langsung memakai **kondisi logika**.
* Cocok untuk kondisi kompleks seperti rentang nilai.

---

## 🧩 PENJELASAN PERBEDAAN UTAMA

| Jenis             | Ciri Utama         | Penggunaan Umum         |
| ----------------- | ------------------ | ----------------------- |
| if                | Kondisi tunggal    | Validasi sederhana      |
| if–else           | Dua kondisi        | Membandingkan nilai     |
| if–else if–else   | Banyak kondisi     | Klasifikasi / Range     |
| when              | Pemilihan nilai    | Pemetaan / enumerasi    |
| when (expression) | Menghasilkan nilai | Digunakan di variabel   |
| when (statement)  | Menjalankan aksi   | Tampilan hasil langsung |

---

## 💬 KESIMPULAN

* Struktur percabangan digunakan untuk **mengatur alur logika program**.
* Kotlin menyediakan cara yang efisien dan fleksibel melalui **if–else dan when**.
* Pemahaman percabangan menjadi dasar penting sebelum mempelajari topik lanjut seperti **looping, fungsi, dan class logic** di Android Studio.
* Dengan memahami percabangan, siswa dapat membuat aplikasi **dinamis, interaktif, dan cerdas**.

---

> 🧠 *“Logika percabangan adalah dasar dari kecerdasan program — setiap keputusan dalam aplikasi dimulai dari satu kondisi.”*


Kamu mau aku buatin file `README.md` siap unduh dari isi di atas biar bisa langsung kamu pakai di folder projekmu?
