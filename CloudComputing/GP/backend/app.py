import base64
from flask import Flask, send_file, request, jsonify, make_response, send_file, Blueprint
from flask_cors import CORS
import translation
from audio import analyze_audio
from image import get_text_from_image
import texttospeech
import os
from google.cloud import datastore

dir_path = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
bp = Blueprint('simple_app', __name__)
CORS(app)

datastore_client = datastore.Client()

@bp.route('/analyze_image', methods=["GET", "POST"])
def process_image():
    if request.method=="POST":
        print(request.form)
        print(request.files)
        image = request.files["image"]
        print(image.filename)
        print(image.content_type)

        image_text = get_text_from_image(image)

        response_body = {
                "message": "Image Transcript : "+ image_text
            }
        response = jsonify(response_body)
        return response

@bp.route('/analyze_audio', methods=["GET", "POST"])
def process_audio():
    response = analyze_audio(request)
    return response

@bp.route('/analyze_text', methods=["GET", "POST"])
def process_text():
    if request.method=="POST":
        print(request.form)
        if request.form["language"] == "Spanish":
            target = "es"
        else:
            target = "en"

        translatedText = translation.translate_text(target, request.form['text'])#"to Spanish (es)"
        response_body = {
                "message": translatedText
            }
        response = jsonify(response_body)
        return response

@bp.route('/save_text', methods=["GET", "POST"])
def save_text():
    if request.method=="POST":
        quote = request.form["text"]
        entity = datastore.Entity(key=datastore_client.key("proj3_files"))
        entity.update({
            'CloudStorage_url' : 'No URL',
            'Transcribed Text' : quote
        })
        datastore_client.put(entity)
        response_body = {
                "message": "Successfully added the quote..!!"
            }
        response = jsonify(response_body)
        return response

@bp.route('/text_to_audio',  methods=["GET", "POST"])
def text_to_audio():
    if request.method=="POST":
        #If request doesnt have id, then add it to db
        # If it does, send text to api  
        message = texttospeech.run(request.form['text'])  
        response_body = {
                "message": message
            }
        file_path = os.path.join(dir_path, 'output.mp3')
        return send_file(file_path)

@bp.route('/get_quotes', methods=["GET", "POST"])
def get_quotes():
    if request.method=="GET":
        query = datastore_client.query(kind="proj3_files")
        quotes_list = query.fetch()
        response_body = []
        for quote in quotes_list:
            print('Quote Id : ' + str(quote.key.id) + '   Transcribed Text: ' + quote['Transcribed Text'])        
            response_body.append({
            "id": quote.key.id,
            "text": quote['Transcribed Text'],
            })
        response = jsonify(response_body)
        return response

app.register_blueprint(bp, url_prefix='/api')

if __name__=='__main__':
    app.run(port=5000, debug=True)