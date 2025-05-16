from PIL import Image, ImageDraw, ImageFont
import qrcode
from dataclasses import dataclass
from typing import Optional

# Define a class for storing a single QR Cell
@dataclass
class QRCell:
    x: int
    y: int
    dx: int
    dy: int
    value: bool

@dataclass
class QRRenderSettings:
    px_per_cell: int = 50
    cells_per_block: int = 2

# Define QRGenerator class
class QRGenerator:

    # Define initializer
    def __init__(self, QRString: str, settings: Optional[QRRenderSettings] = None):

        # Assign settings
        if settings is None:
            settings = QRRenderSettings()
        self.settings: QRRenderSettings = settings


        # Assign the QR string and the QR Data Matrix
        self.QRString: str = QRString
        self.QRData: list[list[bool]] = self._getQRData()

        # Assign width and height
        self.width = len(self.QRData[0])
        self.height = len(self.QRData)

        # Get detailed QR cells
        self.QRCells: list[QRCell] = self._getCells()

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
    
    def _getCells(self):

        # Create list for storing strings
        cells = []

        # Iterate through pixels of the QR Code
        for y in range(self.QRData.height):
            for x in range(self.QRData.width):

                # Get the value at the current position of the QR matrix
                value = self.QRData[y][x]

                # Iterate through the pixels in the current QR block
                for dy in range(self.cellsPerBlock):
                    for dx in range(self.cellsPerBlock):

                        # Create cell and add it to list
                        cells.append(QRCell(x, y, dx, dy, value))

        # Return cells list
        return cells

    
