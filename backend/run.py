from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SECURE FILE SHARING BACKEND SERVER")
    print("=" * 60)
    print(f"📍 Server: http://127.0.0.1:5000")
    print(f"🔍 Health Check: http://127.0.0.1:5000/health")
    print(f"📚 API Docs: Check endpoints at http://127.0.0.1:5000")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )