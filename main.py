from app import create_app
from config import Config

if __name__ == '__main__':
    app = create_app()
    # Hot reload için debug=True ve use_reloader=True
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=True,  # Hot reload aktif
        use_reloader=True  # Kod değişikliklerinde otomatik yeniden yükleme
    )

