# Git'e Yükleme Rehberi - Adım Adım

Bu rehber projenizi Git repository'sine yüklemeniz için gerekli tüm adımları içerir.

## 📋 ÖN HAZIRLIK

### 1. Git Kurulumu Kontrolü
Git'in kurulu olup olmadığını kontrol edin:

```bash
git --version
```

Eğer Git kurulu değilse: https://git-scm.com/downloads adresinden indirin.

---

## 🚀 ADIM ADIM YÜKLEME

### ADIM 1: Git Repository Başlatma

Proje klasörünüzde Git repository'sini başlatın:

```bash
cd C:\Users\dariy\OneDrive\Desktop\mvc45\mvc44\mvc44\mvc
git init
```

**Ne yapar?** Proje klasörünüzde `.git` klasörü oluşturur ve Git takibini başlatır.

---

### ADIM 2: Dosyaları Staging Area'ya Ekleme

Tüm dosyaları Git'e eklemek için:

```bash
git add .
```

**Ne yapar?** Tüm dosyaları Git'in takip edeceği listeye ekler. `.gitignore` dosyasındaki dosyalar otomatik olarak atlanır.

**Alternatif:** Sadece belirli dosyaları eklemek isterseniz:
```bash
git add README.md
git add *.py
```

---

### ADIM 3: İlk Commit (Kayıt) Oluşturma

Değişiklikleri kaydetmek için:

```bash
git commit -m "Initial commit: MUBA Cari Hesap Yönetim Sistemi"
```

**Ne yapar?** Tüm değişiklikleri yerel Git repository'nize kaydeder.

**Not:** İlk commit'te Git kullanıcı bilgilerinizi sorabilir:
```bash
git config --global user.name "Adınız Soyadınız"
git config --global user.email "email@example.com"
```

---

### ADIM 4: GitHub/GitLab Repository Oluşturma

**GitHub için:**
1. https://github.com adresine gidin
2. Sağ üstteki "+" butonuna tıklayın
3. "New repository" seçin
4. Repository adını girin (örn: `muba-cari-hesap`)
5. Public veya Private seçin
6. **"Initialize this repository with a README" seçmeyin** (zaten README.md var)
7. "Create repository" butonuna tıklayın

**GitLab için:**
1. https://gitlab.com adresine gidin
2. "New project" butonuna tıklayın
3. "Create blank project" seçin
4. Project adını girin
5. Visibility seçin
6. "Create project" butonuna tıklayın

---

### ADIM 5: Remote Repository Bağlama

GitHub/GitLab'da oluşturduğunuz repository'nin URL'sini alın ve bağlayın:

**GitHub için:**
```bash
git remote add origin https://github.com/KULLANICI_ADI/REPO_ADI.git
```

**GitLab için:**
```bash
git remote add origin https://gitlab.com/KULLANICI_ADI/REPO_ADI.git
```

**Örnek:**
```bash
git remote add origin https://github.com/dariy/muba-cari-hesap.git
```

**Ne yapar?** Yerel repository'nizi uzak repository ile bağlar.

**Kontrol etmek için:**
```bash
git remote -v
```

---

### ADIM 6: Ana Branch'i Main Olarak Ayarlama (Gerekirse)

Eğer branch adınız `master` ise `main` olarak değiştirin:

```bash
git branch -M main
```

**Ne yapar?** Ana branch adını `main` olarak ayarlar (GitHub'ın yeni standartı).

---

### ADIM 7: Dosyaları Uzak Repository'ye Gönderme

```bash
git push -u origin main
```

**Ne yapar?** Tüm commit'leri GitHub/GitLab'a yükler.

**İlk kez push yapıyorsanız** kullanıcı adı ve şifre/Personal Access Token sorabilir.

---

## 🔐 GÜVENLİK: Personal Access Token (GitHub)

GitHub artık şifre kabul etmiyor. Personal Access Token kullanmanız gerekiyor:

### Token Oluşturma:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" → "Generate new token (classic)"
3. Token adı verin (örn: "muba-project")
4. Süre seçin (örn: 90 days)
5. **repo** yetkisini işaretleyin
6. "Generate token" butonuna tıklayın
7. **Token'ı kopyalayın** (bir daha gösterilmeyecek!)

### Token ile Push:
```bash
git push -u origin main
# Username: GitHub kullanıcı adınız
# Password: Personal Access Token (şifre değil!)
```

---

## ✅ KONTROL

### Repository'yi Kontrol Edin:
```bash
git status
```

### Remote Repository'yi Kontrol Edin:
```bash
git remote -v
```

### Commit Geçmişini Görün:
```bash
git log --oneline
```

---

## 🔄 SONRAKI DEĞİŞİKLİKLER İÇİN

Projede değişiklik yaptıktan sonra:

```bash
# 1. Değişiklikleri kontrol et
git status

# 2. Değişiklikleri ekle
git add .

# 3. Commit yap
git commit -m "Değişiklik açıklaması"

# 4. Push yap
git push
```

---

## 🆘 SORUN GİDERME

### "fatal: not a git repository" hatası:
```bash
git init
```

### "remote origin already exists" hatası:
```bash
git remote remove origin
git remote add origin https://github.com/KULLANICI_ADI/REPO_ADI.git
```

### "failed to push" hatası:
```bash
# Önce pull yapın
git pull origin main --allow-unrelated-histories
# Sonra tekrar push yapın
git push -u origin main
```

### Yanlış dosya eklediyseniz:
```bash
# Dosyayı Git'ten çıkar (dosyayı silmez)
git rm --cached dosya_adi
# .gitignore'a ekle
echo "dosya_adi" >> .gitignore
```

---

## 📝 ÖZET KOMUTLAR

```bash
# 1. Git başlat
git init

# 2. Dosyaları ekle
git add .

# 3. Commit yap
git commit -m "Initial commit: MUBA Cari Hesap Yönetim Sistemi"

# 4. Remote ekle
git remote add origin https://github.com/KULLANICI_ADI/REPO_ADI.git

# 5. Branch adını ayarla
git branch -M main

# 6. Push yap
git push -u origin main
```

---

## 🎯 BAŞARILI YÜKLEME KONTROLÜ

GitHub/GitLab sayfanızda şunları görmelisiniz:
- ✅ README.md dosyası
- ✅ Tüm Python dosyaları
- ✅ requirements.txt
- ✅ .gitignore dosyası
- ✅ LICENSE dosyası (varsa)

**database.db, model.pkl gibi dosyalar görünmemeli!** (.gitignore sayesinde)

---

**İyi çalışmalar! 🚀**

