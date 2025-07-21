CREATE TABLE IF NOT EXISTS admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS produk (
    id SERIAL PRIMARY KEY,
    nama TEXT,
    deskripsi TEXT,
    harga INTEGER,
    gambar TEXT
);

CREATE TABLE IF NOT EXISTS about (
    id SERIAL PRIMARY KEY,
    konten TEXT
);

CREATE TABLE IF NOT EXISTS contact (
    id SERIAL PRIMARY KEY,
    alamat TEXT,
    telepon TEXT,
    email TEXT
);
