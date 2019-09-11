from PIL import Image

def black_and_white(input_image_path,
    output_image_path):
   color_image = Image.open(input_image_path)
   bw = color_image.convert('L')
   bw.save(output_image_path)

if __name__ == '__main__':
    black_and_white('photo.JPG',
        'BWphoto.JPG.jpg')


#TODO
"""
blob-storage :

Source : <username>-12233324234/raw/623432432/photo.JPG
Target : <username>-12233324234/processed/623432432/photo.JPG

- Read the Image Item Name from the Que
- Read the Item from the Cloud Storage based on username
- Convert the BW Image and store them in the bLob under processed

"""
