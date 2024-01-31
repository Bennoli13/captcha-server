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
The Captcha service has a rate limit of 10 requests per minute. Upon successful verification, the service will return a JSON response:
```
{
  "result": true
}
```
You can access the HTML example by navigating to the root ("/") of the server.
