when {
    nilai > 100 -> txtResult.text = "Nilai tidak valid"
    nilai >= 80 -> txtResult.text = "Baik Sekali"
    nilai >= 60 -> txtResult.text = "Cukup"
    else -> txtResult.text = "Kurang"
}
