# Captcha Server Project

## Description

This project is a Captcha server built using Flask. It uses Redis to store image data for later verification and NGINX as the service proxy.

## Installation

To get the server running, clone the repository and use Docker Compose to build and run all components:

```bash
git clone https://github.com/Bennoli13/captcha-server.git
cd captcha-server
docker-compose up --build
```

## Usage
The Captcha service has a rate limit of 20 requests per 5 minutes. Upon successful verification, the service will return a JSON response:
```
#Verification passed
{
  "result": true
}
#Verification failed
{
  "result": false
}
```
You can access the HTML example by navigating to the root ("/") of the server.

### Captcha Verification Flow
When using this captcha service, follow these steps:

1. GET the captcha image from the URI `/captcha`.

2. The server will respond with a `Set-Cookie` header and the captcha image.

3. POST data in the format `{'captcha': 'user input'}`. This data should be posted along with the cookie received in the previous step. The service accepts data in the following content types: `application/json` and `application/x-www-form-urlencoded`. When posting using `application/x-www-form-urlencoded`, the input field name should be `captcha`.

Please note that each captcha image is only valid for one verification attempt. After each attempt, the captcha image should be reloaded.

## Errors

The service may return the following error responses:

1. `{"result":"Rate limit exceeded 127.0.0.1"}`: This error is returned when the rate limit threshold is hit. The service allows a maximum of 10 requests per minute.

2. `{'result': 'Captcha expired, reload the /captcha page'}`: This error indicates that the captcha page should be reloaded. Each captcha image is only valid for one verification attempt, regardless of whether the attempt was successful. This is to prevent brute-force attacks. After each attempt, the captcha image should be reloaded.
 
3. `{'result': 'Invalid input or cookie not set'}`: This error is returned when the input is invalid or the cookie has not been set. Make sure to post the data along with the cookie received from the `/captcha` endpoint.

4. `{'result': 'Invalid Content-Type'}`: This error is returned when the posted data uses an invalid Content-Type. The service only accepts `application/json` and `application/x-www-form-urlencoded`. When posting using `application/x-www-form-urlencoded`, the input field name should be `captcha`.
