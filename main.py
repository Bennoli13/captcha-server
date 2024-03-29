from flask import Flask, request, jsonify,render_template, make_response, redirect
from captcha.image import ImageCaptcha
import random
import string
import uuid
from flask import jsonify
from flask_limiter import Limiter, RateLimitExceeded
from flask_limiter.util import get_remote_address
import redis

REDIS_HOST = "captcha-redis"
RATE_LIMIT = "20 per 5 minutes"

app = Flask(__name__)
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def get_real_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    else:
        return request.remote_addr
    
limiter = Limiter(
    app,
    key_func=get_real_ip,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=f"redis://{REDIS_HOST}:6379"
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
@limiter.limit(RATE_LIMIT)
def generate_captcha():
    # Get uid from cookie
    request_uid = request.cookies.get('uid', None)
    if not request_uid:
        # Generate a random uid
        request_uid = str(uuid.uuid4())
    
    # Generate a random captcha text
    captcha_text = generate_random_text()
    
    # Store the captcha text in Redis
    store_captcha(request_uid, captcha_text)
    
    # Generate captcha image
    captcha_image = generate_captcha_image(captcha_text)

    # Create a response object
    response = make_response(captcha_image)
    
    # Set the cookie
    response.set_cookie('uid', request_uid)
    
    # Return the response
    return response

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

def verify_captcha_input(user_input="", captcha_text=""):
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
@limiter.limit(RATE_LIMIT)
def verify_captcha():
    #handle json and form data
    try:
        if request.headers['Content-Type'] == 'application/json':
            data = request.get_json()
            captcha_text = data.get('captcha', None)
        elif 'application/x-www-form-urlencoded' in request.headers['Content-Type']:
            captcha_text = request.form.get('captcha', None)
    except KeyError as e:
        return jsonify({'result': 'Invalid Content-Type'}), 400
    except Exception as e:
        print(f"An error occurred: {type(e).__name__}")
        return jsonify({'result': 'Invalid input or cookie not set'}), 400
    request_uid = request.cookies.get('uid', None)
    
    if not captcha_text or not request_uid:
        return jsonify({'result': 'Invalid input or cookie not set'}), 400
    
    #get captcha text from redis
    captcha_text_from_redis = get_captcha(request_uid)
    
    if captcha_text_from_redis is None:
        return jsonify({'result': 'Captcha expired, reload the /captcha page'}), 400
    
    result = verify_captcha_input(captcha_text, captcha_text_from_redis) 
    # Return True if the user_text is same as captcha_text, else return False
    return jsonify({'result': result})

@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    user_ip = get_real_ip()
    return jsonify({'result': 'Rate limit exceeded {}'.format(user_ip)}), 429

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=False)
   
    
