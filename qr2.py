from PIL import Image as PILImage, ImageDraw, ImageFont
import qrcode
from dataclasses import dataclass
from typing import Optional, Tuple

'''
Plan: Dependency injected render functions
QRGenerator has a generic "render" function which iterates through cell list,
and calls the passed-in render class' render function.
This render function will call the class' renderBlock function, which will
handle most of the technical details.
'''

# Define a class for storing a single QR Cell
@dataclass
class QRCell:
    x: int
    y: int
    dx: int
    dy: int
    value: bool

@dataclass
class QRImageStyle:

    # Base image filename
    base_image_filename: Optional[str] = None

    # 2-image style
    # Images are stored as filenames that will be opened by the renderer
    on_image: Optional[str] = None
    off_image: Optional[str] = None

    # tint style
    on_tint: Optional[Tuple[Tuple[int, int, int], float]] = None
    off_tint: Optional[Tuple[Tuple[int, int, int], float]] = None

    # Render settings
    px_per_cell: int = 50
    cells_per_block: int = 2


@dataclass
class RenderCanvas:
    image: PILImage.Image
    draw: ImageDraw.ImageDraw

# Define QRGenerator class
class QRGenerator:

    # Define initializer
    def __init__(self, QRString: str):


        # Assign the QR string and the QR Data Matrix
        self.QRString: str = QRString
        self.QRData: list[list[bool]] = self._getQRData()

        # Assign width and height
        self.width = len(self.QRData[0])
        self.height = len(self.QRData)

    # Define function to generate QR code data
    def _getQRData(self):

        # Create QR object
        qr = qrcode.QRCode(border=1)

        # Add data to the QR code and make it
        qr.add_data(self.QRString)
        qr.make()

        # Extract the QR data
        QRData = qr.get_matrix()

        # Return the QR Data Matrix
        return QRData

    
# Define QRImageBlockRenderer
class QRImageBlockRenderer:
    def __init__(self, QR: QRGenerator, imageFilename: str, renderSettings: Optional[QRRenderSettings] = None):

        # Set filename
        self.imageFilename = imageFilename

        # Set QRData
        self.QR = QR

        # Assign settings
        if renderSettings is None:
            renderSettings = QRRenderSettings()
        self.renderSettings: QRRenderSettings = renderSettings

        # Get the image
        self.image = self._openImage()

        # Get the canvas
        self.canvas = self._getImageCanvas()

        # Get the cells
        self.cells = self._getCells()

        # Set tints
        # First value: color
        # Second value: opacity of tint
        self.onTint = ((0, 0, 0), 0.75)
        self.offTint = ((255, 255, 255), 0.7)

    def _getCells(self):

        # Create list for storing strings
        cells = []

        # Iterate through pixels of the QR Code
        for y in range(self.QR.height):
            for x in range(self.QR.width):

                # Get the value at the current position of the QR matrix
                value = self.QR.QRData[y][x]

                # Iterate through the pixels in the current QR block
                for dy in range(self.renderSettings.cells_per_block):
                    for dx in range(self.renderSettings.cells_per_block):

                        # Create cell and add it to list
                        cells.append(QRCell(x, y, dx, dy, value))

        # Return cells list
        return cells

    def _getImageCanvas(self):

        # Calculate image width and height
        img_width = self.QR.width * self.renderSettings.cells_per_block * self.renderSettings.px_per_cell
        img_height = self.QR.height * self.renderSettings.cells_per_block * self.renderSettings.px_per_cell

        # Initialize new image and draw classes
        image = PILImage.new("RGBA", (img_width, img_height), "white")
        draw = ImageDraw.Draw(image)

        # Combine into renderCanvas dataclass
        canvas = RenderCanvas(image, draw)

        # Return the canvas
        return canvas

    def _getXYPos(self, currentCell: QRCell):

        # Calculate pixel coordinates
        xpos = (currentCell.x * self.renderSettings.cells_per_block + currentCell.dx) * self.renderSettings.px_per_cell
        ypos = (currentCell.y * self.renderSettings.cells_per_block + currentCell.dy) * self.renderSettings.px_per_cell

        return (xpos, ypos)


    # Define function to open the image
    def _openImage(self):

        # Open the image
        image: PILImage = PILImage.open(self.imageFilename).convert("RGBA")

        # Scale the image
        image = self._scaleImage(image)

        # Return the image
        return image
    
    # Create render function
    def render(self):

        # Get the tinted images
        onImage = self._tintImage(self.image, self.onTint[0], self.onTint[1])
        offImage = self._tintImage(self.image, self.offTint[0], self.offTint[1])

        # Iterate through cells
        for cell in self.cells:

            # Get the correct tinted image depending on if cell value is true or not
            image = onImage if cell.value else offImage

            # Call render cell
            self._renderCell(cell, image)

        # Return the canvas (should contain rendered image)
        return self.canvas.image

    
    # Define a function to render a cell
    def _renderCell(self, 
                    currentCell: QRCell,
                    image: PILImage.Image):

        # Get the pixel coordinates
        xpos, ypos = self._getXYPos(currentCell)

        # paste the image at this location
        self.canvas.image.paste(image, (xpos, ypos))
    
    # Define function to scale image to fit and crop to square
    def _scaleImage(self, image):

        # Get original width and height
        original_size: tuple[int, int] = image.size
        original_width, original_height = original_size

        # Get target width and height from settings
        target_width =  target_height = self.renderSettings.px_per_cell

        # Calculate aspect ratios
        original_aspect = original_width / original_height
        target_aspect = target_width / target_height

        # Determine how to scale the image to fit the frame
        if original_aspect > target_aspect:
            new_height = target_height
            new_width = int(original_width * (target_height / original_height))
        else:
            new_width = target_width
            new_height = int(original_height * (target_width / original_width))

        # Resize the image
        resized_overlay = image.resize((new_width, new_height), PILImage.LANCZOS)

        # Calculate the center of the image
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        cropping_box = (left, top, right, bottom)

        # Crop the image
        cropped_image = resized_overlay.crop(cropping_box)

        # Return cropped image
        return cropped_image
    
    def _tintImage(self, originalImage: PILImage.Image, color: tuple[int, int, int], intensity: float):

        # check if image mode isn't RGBA
        if originalImage.mode != 'RGBA':

            # convert image to RGBA
            originalImage = originalImage.convert('RGBA')

        # generate tint layer
        tint_layer = PILImage.new('RGBA', originalImage.size, color)

        # return blended image
        return PILImage.blend(originalImage, tint_layer, intensity)
    
def main():

    qr = QRGenerator("https://hole.cd")
    renderer = QRImageBlockRenderer(qr, "images/laserdisc.jpg")
    image = renderer.render()
    image.show()
    

if __name__ == "__main__":
    main()






    
