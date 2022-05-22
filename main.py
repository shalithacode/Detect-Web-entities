from flask import Flask, request, render_template, redirect, flash
from werkzeug.utils import secure_filename


app = Flask(__name__, template_folder="template")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():

    return render_template(
        "index.html", action="/result", method="POST", value="Search"
    )


@app.route("/result", methods=["GET", "POST"])
def speech():

    import os
    from google.cloud import storage

    os.environ["SERVICE_JSON_FILE"] = os.environ[
        "GOOGLE_APPLICATION_CREDENTIALS"
    ] = "shalitha98-9b0e0cb27e46.json"
    client = storage.Client().from_service_account_json(os.environ["SERVICE_JSON_FILE"])
    os.environ["BUCKET_NAME"] = "shalitha98.appspot.com"
    bucket = storage.Bucket(client, os.environ["BUCKET_NAME"])
    blob = bucket.blob

    if request.method == "POST":

        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_blob = bucket.blob(filename, chunk_size=262144 * 5)
            file_blob.upload_from_file(
                file, content_type=file.content_type, client=client
            )
        else:
            flash("Enter Valid File")
            return redirect("/")

        storage_client = storage.Client()
        blobs = storage_client.list_blobs("shalitha98.appspot.com")

        arr = {}
        for blob in blobs:
            arr[blob.updated] = blob.name

        req_file = str(list(dict(sorted(arr.items())).values())[-1])

        print(req_file)
        from google.cloud import vision

        client = vision.ImageAnnotatorClient()
        image = vision.Image()
        image.source.image_uri = f"gs://shalitha98.appspot.com/{req_file}"

        response = client.web_detection(image=image)
        annotations = response.web_detection

        partial_detactions = []
        full_detactions = []
        title = ""
        default_image_url = (
            f"https://storage.cloud.google.com/shalitha98.appspot.com/{req_file}"
        )

        if annotations.pages_with_matching_images:
            title = f"{len(annotations.pages_with_matching_images)} Pages with matching images found"

            for page in annotations.pages_with_matching_images:

                if page.full_matching_images:

                    for image in page.full_matching_images:

                        image_url = image.url

                        if not any(
                            ele in str(image_url) for ele in [".jpeg", ".jpg", ".png"]
                        ):
                            image_url = default_image_url

                        full_detactions.append({image_url: page.url})
                        break

                if page.partial_matching_images:

                    for image in page.partial_matching_images:

                        image_url = image.url

                        if not any(
                            ele in str(image_url) for ele in [".jpeg", ".jpg", ".png"]
                        ):
                            image_url = default_image_url

                        partial_detactions.append({image_url: page.url})
                        break
        else:
            title = "No matching images found"

        all_detactions = partial_detactions + full_detactions
        
        return render_template(
            "index.html",
            title=title,
            all_detactions=[
                i
                for n, i in enumerate(all_detactions)
                if i not in all_detactions[n + 1 :]
            ],
            default_image_url=default_image_url,
            action="/result",
            method="POST",
            value="Search",
        )
    else:
        flash("Enter Valid File")


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
