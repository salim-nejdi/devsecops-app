from flask import (
    Flask,
    request,
    render_template,
    redirect,
    jsonify
)

from sqlalchemy import create_engine, text
from PIL import Image

import requests
import yaml
import os


app = Flask(__name__)

app.secret_key = "devsecops-super-secret-key-2026"

DATABASE_URL = "sqlite:///products.db"

engine = create_engine(DATABASE_URL)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def init_db():

    with engine.begin() as connection:

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                image TEXT
            )
        """))

        count = connection.execute(
            text("SELECT COUNT(*) FROM products")
        ).scalar()

        if count == 0:

            connection.execute(
                text("""
                    INSERT INTO products
                    (name, description)
                    VALUES
                    ('Laptop', 'Ordinateur portable'),
                    ('Switch Cisco', 'Switch réseau 24 ports'),
                    ('Firewall', 'Firewall pour le laboratoire')
                """)
            )


@app.route("/")
def index():

    with engine.connect() as connection:

        products = connection.execute(
            text("SELECT * FROM products")
        ).mappings().all()

    return render_template(
        "index.html",
        products=products,
        search=""
    )


@app.route("/search")
def search():

    value = request.args.get("q", "")

    query = text(
        "SELECT * FROM products "
        "WHERE name LIKE '%" + value + "%'"
    )

    with engine.connect() as connection:

        products = connection.execute(
            query
        ).mappings().all()

    return render_template(
        "index.html",
        products=products,
        search=value
    )


@app.route("/add", methods=["POST"])
def add_product():

    name = request.form.get("name")
    description = request.form.get("description")

    with engine.begin() as connection:

        connection.execute(
            text("""
                INSERT INTO products
                (name, description)
                VALUES (:name, :description)
            """),
            {
                "name": name,
                "description": description
            }
        )

    return redirect("/")


@app.route("/delete/<product_id>")
def delete_product(product_id):

    with engine.begin() as connection:

        connection.execute(
            text(
                "DELETE FROM products WHERE id = "
                + product_id
            )
        )

    return redirect("/")


@app.route("/upload", methods=["POST"])
def upload():

    if "image" not in request.files:
        return "Aucun fichier", 400

    file = request.files["image"]

    if file.filename == "":
        return "Nom de fichier vide", 400

    destination = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(destination)

    try:

        image = Image.open(destination)

        image.thumbnail(
            (500, 500)
        )

        image.save(destination)

    except Exception:

        pass

    return redirect("/")


@app.route("/api/product/<product_id>")
def api_product(product_id):

    with engine.connect() as connection:

        product = connection.execute(
            text(
                "SELECT * FROM products WHERE id = "
                + product_id
            )
        ).mappings().first()

    if product is None:

        return jsonify({
            "error": "Product not found"
        }), 404

    return jsonify(
        dict(product)
    )


@app.route("/api/fetch")
def fetch_url():

    url = request.args.get("url")

    if not url:

        return jsonify({
            "error": "URL missing"
        }), 400

    try:

        response = requests.get(
            url,
            timeout=10
        )

        return response.text

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


@app.route("/api/import-yaml", methods=["POST"])
def import_yaml():

    content = request.data.decode(
        "utf-8"
    )

    try:

        data = yaml.load(
            content,
            Loader=yaml.Loader
        )

        return jsonify({
            "status": "imported",
            "content": str(data)
        })

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 400


@app.route("/api/config")
def config():

    return jsonify({
        "environment": os.getenv(
            "ENVIRONMENT",
            "development"
        ),

        "debug": True,

        "api_token":
            "ghp_1234567890abcdefghijklmnopqrstuvwxyz",

        "database":
            DATABASE_URL
    })


@app.route("/api/system")
def system():

    return jsonify({

        "hostname":
            os.uname().nodename,

        "working_directory":
            os.getcwd(),

        "environment":
            dict(os.environ)
    })


@app.route("/health")
def health():

    return jsonify({
        "status": "OK",
        "application": "devsecops-app"
    })


if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
