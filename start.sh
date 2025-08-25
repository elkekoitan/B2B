#!/bin/bash

# Agentik B2B Tedarik Uygulaması - Kurulum ve Çalıştırma Scripti

echo "🚀 Agentik B2B Tedarik Uygulaması kurulumu başlatılıyor..."

# .env dosyasını kontrol et
if [ ! -f ".env" ]; then
    echo "⚠️  .env dosyası bulunamadı. .env.example'dan kopyalanıyor..."
    cp .env.example .env
    echo "✅ .env dosyası oluşturuldu. Lütfen Supabase ve email ayarlarını güncelleyin."
fi

# Docker çalışıp çalışmadığını kontrol et
if ! command -v docker &> /dev/null; then
    echo "❌ Docker kurulu değil. Lütfen Docker'i kurun: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose kurulu değil. Lütfen Docker Compose'u kurun."
    exit 1
fi

# Log klasörünü oluştur
mkdir -p logs

echo "🔧 Docker image'ları build ediliyor..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Build işlemi başarılı!"
else
    echo "❌ Build işlemi başarısız oldu!"
    exit 1
fi

echo "🚀 Servisler başlatılıyor..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ Tüm servisler başarıyla başlatıldı!"
    echo ""
    echo "🌐 Uygulama URL'leri:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - Redis: localhost:6379"
    echo ""
    echo "📊 Servis durumunu kontrol etmek için:"
    echo "   docker-compose ps"
    echo ""
    echo "📋 Logları görmek için:"
    echo "   docker-compose logs -f [servis-adı]"
    echo ""
    echo "🛑 Durdurmak için:"
    echo "   docker-compose down"
else
    echo "❌ Servisler başlatılamıyor!"
    echo "Hata loglarını kontrol edin: docker-compose logs"
    exit 1
fi