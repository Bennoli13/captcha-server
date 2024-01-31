from flask import Flask, request, jsonify,render_template, make_response,redirect
from captcha.image import ImageCaptcha
import random
import string
import uuid
from flask import jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

app = Flask(__name__)
r = redis.Redis(host='captcha-redis', port=6379, db=0)

def get_real_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    else:
        return request.remote_addr()
    
limiter = Limiter(
    app,
    key_func=get_real_ip,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://captcha-redis:6379"
)

def store_captcha(uid, captcha_text):
    # Store the captcha text against the uid in Redis
    r.set(uid, captcha_text)
    
def get_captcha(uid):
    # Get the captcha text for the given uid from Redis
    captcha_text = r.get(uid)
    if captcha_text is not None: captcha_text = captcha_text.decode('utf-8')
    r.delete(uid)
    return captcha_text

@app.route('/captcha', methods=['GET'])
@limiter.limit("10 per 5 minutes")
def generate_captcha():
    #get uid from cookie
    request_uid = request.cookies.get('uid', None)
    if not request_uid:
        return redirect('/')
    
    # Generate a random captcha text
    captcha_text = generate_random_text()
    
    #store the captcha text in redis
    store_captcha(request_uid, captcha_text)
    
    # Generate captcha image
    captcha_image = generate_captcha_image(captcha_text)

    # Return the captcha image as a response    
    return captcha_image

def generate_random_text(length=6):
    # Implement your logic to generate a random captcha text here
    
    # Define the characters to choose from
    characters = string.ascii_letters + string.digits
    # Generate a random captcha text of the specified length
    captcha_text = ''.join(random.choice(characters) for _ in range(length))
    return captcha_text

def generate_captcha_image(text):
    # Create an instance of ImageCaptcha
    captcha = ImageCaptcha(width=280, height=90)

    # Generate the captcha image
    image = captcha.generate(text)

    # Save the image to a file or convert it to bytes
    # You can choose to save the image to a file or convert it to bytes and return it as a response
    # For example, to save the image to a file:
    # image.save('/path/to/save/image.png')
    # Or to convert it to bytes and return it as a response:
    return image.getvalue(), 200, {'Content-Type': 'image/png'}

def verify_captcha_input(user_input, captcha_text):
    if len(user_input) != len(captcha_text):
        return False

    mistake_count = 0
    for i in range(len(user_input)):
        if user_input[i] != captcha_text[i]:
            mistake_count += 1
            if mistake_count > 1:
                return False

    return True

@app.route('/verify', methods=['POST'])
@limiter.limit("10 per 5 minutes")
def verify_captcha():
    #handle json and form data
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json()
        captcha_text = data.get('captcha', None)
    else:
        captcha_text = request.form.get('captcha', None)
    request_uid = request.cookies.get('uid', None)
    if not captcha_text or not request_uid:
        return redirect('/')
    #get captcha text from redis
    captcha_text_from_redis = get_captcha(request_uid)
    
    result = verify_captcha_input(captcha_text, captcha_text_from_redis) 
    # Return True if the user_text is same as captcha_text, else return False
    return jsonify({'result': result})

@app.route('/', methods=['GET'])
def load_captcha():
    # Generate a random uid
    uid = str(uuid.uuid4())
    response = make_response(render_template('captcha.html'))
    # Set cookie for captcha
    response.set_cookie('uid', uid)
    return response

if __name__ == '__main__':
    app.run()
    
