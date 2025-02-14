import requests
r = requests.post(
    "https://api.deepai.org/api/image-similarity",
    files={
        'image1': open('crop.png', 'rb'),
        'image2': open('template', 'rb'),
    },
    headers={'api-key': 'cbbfac12-2fd1-481a-84be-8d0eb90ec21a'}
)
print(r.json())
