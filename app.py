from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)

BDC_URL = "https://api.bigdatacloud.net/data/reverse-geocode-client"


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.route("/", methods=["GET"])
def index():
    return send_from_directory(".", "index.html")


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


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "server is up"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )