import requests
from PIL import Image
from io import BytesIO

# Form the request
data = {
    'image': (
        'https://sun9-4.userapi.com/impg/qXMKQzs91vqO_PESPteoi45CbKvj1hWNQ8Y6HA/'
        'X3Y8CJaAsFg.jpg?size=608x1080&quality=96&sign=a73c97e94d6e7ebe73b289e7259180f8'
        '&type=album'
    )
    # https://www.rostovmilo.ru/wa-data/public/shop/products/96/80/28096/images/1948/1948.970.jpeg
    # np_image.tolist()
}

# POST image to server and collect the response
response = requests.post("http://localhost:5000/api/v1.0/segmentation", json=data)

# Check if response is valide
if response.json()['status'] == 200:
    # Print the image link
    print(response.json()['segmentation'])
    # Get the image from link in respone
    image = Image.open(BytesIO(requests.get(response.json()['segmentation']).content))
    # Draw it on your screen
    image.show()
else:
    # If the response is invalid, show the error message
    print('Error ' + str(response.json()['status']) + ': ' + response.json()['error'])