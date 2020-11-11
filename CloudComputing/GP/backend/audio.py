import os
import datetime
import base64
from flask import Flask, send_file, request, jsonify, make_response
from flask_cors import CORS
from google.cloud import speech
from google.cloud import storage
from google.cloud import datastore

os.environ['GOOGLE_APPLICATION_CREDENTIALS']=r'proj3-ml-api-2ba7a1a87cba.json'
os.environ['CLOUD_STORAGE_BUCKET']='proj3_audio_bucket'
CLOUD_STORAGE_BUCKET = os.environ.get("CLOUD_STORAGE_BUCKET", "proj3_audio_bucket")
speech_client = speech.SpeechClient()
storage_client = storage.Client()
datastore_client = datastore.Client()

bucket = storage_client.bucket(CLOUD_STORAGE_BUCKET)

class Audio_API(object):
    def analyze_audio(self, request):
        if request.method=="POST":
            print(request.form)
            print(request.files)
            audio = request.files["file"]
            print(audio.filename)
            print(audio.content_type)
            audio.save("che.webm")
            dt = datetime.datetime.now().strftime("%f")
            blob_name=audio.filename + dt
            blob = bucket.blob(blob_name)
            # blob = bucket.blob(audio.filename)
            blob.upload_from_string(audio.read(), content_type=audio.content_type)
            blob.make_public()
        
            # gcs_uri = "gs://cloud-samples-tests/speech/brooklyn.flac"
            gcs_uri = "gs://proj3_audio_bucket/"+blob_name
            print(gcs_uri)
            audio = speech.RecognitionAudio(uri=gcs_uri)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
                sample_rate_hertz=48000,
                language_code="en-US",
            )
            response = speech_client.recognize(config=config, audio=audio)
            transcript=""
            print(response)
            for result in response.results:
                print(u"Transcript : {}".format(result.alternatives[0].transcript))
                transcript=format(result.alternatives[0].transcript)
        
            entity = datastore.Entity(key=datastore_client.key("proj3_files"))
            entity.update({
                'Audio_url' : blob.public_url,
                'Transcribed Text' : transcript
            })
            datastore_client.put(entity)
        
            response_body = {
                "message": "Transcript: " + transcript
            }
            response = jsonify(response_body)
            return response
