from flask import Flask, request, render_template

app = Flask(__name__, template_folder="template")

@app.route("/", methods=["GET", "POST"])
def index():
    
    return render_template("index.html", action="/result",method="POST",value="Search")


@app.route("/result", methods=["GET", "POST"])
def speech():
        
    # import os
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "shalitha98-9b0e0cb27e46.json"

    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = "gs://shalitha98.appspot.com/sample/human.jpeg"

    response = client.web_detection(image=image)
    annotations = response.web_detection

    partial_detactions =[]
    full_detactions =[]
    title=""
    default_image_url = "https://storage.cloud.google.com/shalitha98.appspot.com/sample/human.jpeg"

    if annotations.pages_with_matching_images:
        title=f'{len(annotations.pages_with_matching_images)} Pages with matching images found'

        for page in annotations.pages_with_matching_images:
        
            if page.full_matching_images:
        
                for image in page.full_matching_images:

                    image_url = image.url
                    
                    if not any(ele in str(image_url) for ele in ['.jpeg','.jpg','.png']):
                        image_url = default_image_url

                    full_detactions.append({image_url:page.url})
                    break

            if page.partial_matching_images:

                for image in page.partial_matching_images:

                    image_url = image.url

                    if not any(ele in str(image_url) for ele in ['.jpeg','.jpg','.png']):
                        image_url = default_image_url

                    partial_detactions.append({image_url:page.url})
                    break


    all_detactions = partial_detactions + full_detactions

    return render_template("index.html",title=title, all_detactions=[i for n, i in enumerate(all_detactions) if i not in all_detactions[n + 1:]],action="/",method="GET",value="Back")
    


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
    
