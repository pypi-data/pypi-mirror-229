from PIL import Image

class ImageProcessor:
    def __init__(self, image_path):
        self.image = Image.open(image_path)
        self.width, self.height = self.image.size

    def display(self):
        self.image.show()

class ImageResizer:
    def __init__(self, image):
        self.image = image

    def resize(self):
        width, height = self.image.size
        new_width = width // 2
        new_height = height // 2
        resized_image = self.image.resize((new_width, new_height))
        return resized_image

class ImageConverter:
    def __init__(self, image):
        self.image = image

    def convert_to_grayscale(self):
        grayscale_image = self.image.convert("L")
        return grayscale_image

if __name__ == "__main__":
    image_path = input("Enter the path or name of the image file: ")

    try:
        processor = ImageProcessor(image_path)

        # Display the original image
        processor.display()

        # Create instances of the image processing classes
        resizer = ImageResizer(processor.image)
        converter = ImageConverter(processor.image)

        # Perform image processing operations
        resized_image = resizer.resize()
        grayscale_image = converter.convert_to_grayscale()

        # Save the processed images
        resized_image.save("resized.jpg")
        grayscale_image.save("grayscale.jpg")

        # Close the original image
        processor.image.close()

    except FileNotFoundError:
        print("Image not found. Please make sure the file path or name is correct.")
    except Exception as e:
        print(f"An error occurred: {e}")
