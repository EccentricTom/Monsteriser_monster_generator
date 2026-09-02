import base64

import requests

url = "https://apply.caplena.com/api-guru"
encoded = "VGhlIEludGVybmV0PyAgV2UgYXJlIG5vdCBpbnRlcmVzdGVkIGluIGl0Lg=="

decoded = base64.b64decode(encoded)

print(repr(decoded))
# b'The Internet?  We are not interested in it.'

response = requests.post(
    url,
    data=decoded,
    headers={"Content-Type": "text/plain"},
    timeout=10,
)

print("Status:", response.status_code)
print("Headers:", dict(response.headers))
print("Body:", response.text)
