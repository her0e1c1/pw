import os

url = os.environ.get("PW_URL")
if "~" in url:
    url = url.replace("~", os.environ["HOME"])

config = {
    "url": url,
    "aes_format": "%32s"
}
