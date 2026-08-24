"""
Flask backend that takes lat/long (or falls back to visitor IP)
and returns city/country.

Uses BigDataCloud's free API - no API key needed.

Run:
    pip install flask requests --break-system-packages
    python app.py

Test:
    http://localhost:5000/location?lat=19.0760&lon=72.8777
    http://localhost:5000/location
"""

from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)


BDC_URL = "https://api.bigdatacloud.net/data/reverse-geocode-client"


@app.after_request
def add_cors_headers(response):

    # Allows browser requests
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response


# ==========================================================
# CONNECT INDEX.HTML
# ==========================================================

@app.route("/", methods=["GET"])
def index():

    return send_from_directory(".", "index.html")


# ==========================================================
# LOCATION API
# ==========================================================

@app.route("/location", methods=["GET"])
def location():

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    params = {
        "localityLanguage": "en"
    }

    if lat and lon:

        params["latitude"] = lat
        params["longitude"] = lon

    try:

        resp = requests.get(
            BDC_URL,
            params=params,
            timeout=10
        )

        resp.raise_for_status()

        data = resp.json()

    except requests.RequestException as e:

        return jsonify({
            "error": f"Lookup failed: {e}"
        }), 502


    return jsonify({

        "latitude": lat or data.get("latitude"),

        "longitude": lon or data.get("longitude"),

        "city": data.get("city"),

        "country": data.get("countryName"),

        "raw": data

    })


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "server is up"
    })


# ==========================================================
# RUN SERVER
# ==========================================================



if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )