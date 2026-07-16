
# Tambahkan fungsi ini sebelum threading.Thread(...).start()

def run_api():
    port = int(os.getenv("PORT", 5000))
    api.run(host="0.0.0.0", port=port, debug=False)

# Ganti bagian START FLASK API menjadi:

threading.Thread(
    target=run_api,
    daemon=True
).start()
