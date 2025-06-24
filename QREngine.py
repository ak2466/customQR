from PIL import Image as PILImage, ImageDraw
import qrcode
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class RenderCanvas:
    image: PILImage.Image
    draw: ImageDraw.ImageDraw

@dataclass
class RenderSettings:

    # Render settings
    px_per_cell: int = 50
    cells_per_block: int = 2

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

# Define a class for storing a single QR Cell
@dataclass
class QRCell:
    x: int
    y: int
    dx: int
    dy: int
    value: bool

# Define QRRenderer base class
class QRRenderer:

    # Define initializer
    def __init__(self, QR: QRGenerator, renderSettings: RenderSettings):

        # Set QRdata
        self.__QR = QR

        # Set RenderSettings
        self.__renderSettings = RenderSettings

    # Define get cells function
    def get_cells(self):

        # Create list for storing strings
        cells = []

        # Iterate through pixels of the QR Code
        for y in range(self.__QR.height):
            for x in range(self.__QR.width):

                # Get the value at the current position of the QR matrix
                value = self.__QR.QRData[y][x]

                # Iterate through the pixels in the current QR block
                for dy in range(self.__renderSettings.cells_per_block):
                    for dx in range(self.__renderSettings.cells_per_block):

                        # Create cell and add it to list
                        cells.append(QRCell(x, y, dx, dy, value))

        # Return cells list
        return cells
    
    def get_canvas(self):

        # Calculate image width and height
        width = self.__QR.width * self.__renderSettings.cells_per_block * self.__renderSettings.px_per_cell
        height = self.__QR.height * self.__renderSettings.cells_per_block * self.__renderSettings.px_per_cell

        # Initialize new image and draw classes
        image = PILImage.new("RGBA", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # Combine into renderCanvas dataclass
        canvas = RenderCanvas(image, draw)

        # Return the canvas
        return canvas
