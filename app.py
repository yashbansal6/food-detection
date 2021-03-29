import os
import requests
import numpy as np
from keras.preprocessing import image
from keras.models import load_model
from uuid import uuid4

from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

food_list = ['donuts',
 'french_fries',
 'fried_rice',
 'hamburger',
 'hot_dog',
 'pizza',
 'samosa',
 'spring_rolls',
 'sushi',
 'waffles']

def predict_class(model, img, show = True):
    pred = model.predict(img)
    index = np.argmax(pred)
    food_list.sort()
    pred_value = food_list[index]
    if show:
        plt.imshow(img[0])                           
        plt.axis('off')
        plt.title(pred_value)
        plt.show()
        print(pred_value)
        
    api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
    query = pred_value.replace("_"," ")
    response = requests.get(api_url + query, headers={'X-Api-Key': 'Sa1uVWZLKXJxM5YPaIEfpg==cEn3gyPDIKhGlmor'})
    if response.status_code == requests.codes.ok:
        data_json = response.json()
        data = data_json['items']
        return data
    else:
        print("Error:", response.status_code, response.text)

@app.route("/")

def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])

def upload():
    target = os.path.join(APP_ROOT, 'images/')
    print(target)
    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Couldn't create upload directory: {}".format(target))
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target, filename])
        print ("Accept incoming file:", filename)
        print ("Save it to:", destination)
        upload.save(destination)
        
        model = load_model('best_model_10class.hdf5',compile = False)
        
        img = image.load_img('images/'+filename, target_size=(299,299))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img /= 255.
        
        prediction = predict_class(model, img, False)
        name = prediction[0]['name']
        calories = prediction[0]['calories']
        prediction[0].pop('name')
        prediction[0].pop('calories')
        
    return render_template("template.html", image_name=filename, name=name, calories=calories, info=prediction)

@app.route('/upload/<filename>')

def send_image(filename):
    return send_from_directory("images", filename)

if __name__ == "__main__":
    app.run(debug=False)

