from __future__ import annotations

import os
from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def hello_world():
    return """
    <!doctype html>
    <html lang="pt-BR">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Lab 09 - Flask no Render</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 48px; color: #20232a; }
          code { background: #f2f2f2; padding: 4px 8px; border-radius: 6px; }
        </style>
      </head>
      <body>
        <h1>Hello World - Flask no Render</h1>
        <p>Exercicio 9.3 publicado no Render gratuito.</p>
        <p>Health check: <code>/api/health</code></p>
      </body>
    </html>
    """


@app.get("/api/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "framework": "Flask",
            "cloud": "Render",
            "exercise": "9.3",
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
