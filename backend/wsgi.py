from app.main import create_app

app = create_app(force_recreate=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)