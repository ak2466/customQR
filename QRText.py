from .QREngine import QRCell, QRGenerator, QRRenderer, RenderSettings

from dataclasses import dataclass
from typing import Protocol, Tuple
from PIL import ImageFont

@dataclass
class QRTextStyle:

    # Font path
    font_path: str

# Define interface for cell rendering
class CellRenderingProtocol(Protocol):

    def __call__(self, cell: QRCell, qr: QRGenerator, style: QRTextStyle, renderSettings: RenderSettings) -> Tuple[str, Tuple[int, int, int]]:
        ...

# Define QRTextBlockRenderer
class QRTextBlockRenderer:

    def __init__(self, 
                 QR: QRGenerator, 
                 style: QRTextStyle,
                 renderSettings: RenderSettings,
                 text_rendering_protocol: CellRenderingProtocol):

        # Set QRData
        self.QR = QR

        # Set style
        self.style = style
    
        # Set render settings
        self.__renderSettings = renderSettings

        # Set get cell function
        self._get_cell_func = text_rendering_protocol

        # Get font
        self.font = self._getScaledFont()

        # Create a renderer
        self.__renderer = QRRenderer(self.QR, self.__renderSettings)

        # Get the canvas
        self.__canvas = self.__renderer.get_canvas()

        # Get cells
        self.cells = self.__renderer.get_cells()

    def _getScaledFont(self, testChar = "%"):

        # Step 1: Load with arbitrary small size first to measure
        base_font_size = 10
        font = ImageFont.truetype(self.style.font_path, base_font_size)

        # Step 2: Measure test character
        bbox = font.getbbox(testChar)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]

        # Step 3: Calculate scaling factor
        scale = self.__renderSettings.px_per_cell / max(char_width, char_height)
        final_font_size = int(base_font_size * scale)

        # Step 4: Reload font at the correct size
        font = ImageFont.truetype(self.style.font_path, final_font_size)

        return font
    
    def _getXYPos(self, currentCell: QRCell):

        # Extract
        x, y = currentCell.x, currentCell.y
        dx, dy = currentCell.dx, currentCell.dy
        cells_per_block, px_per_cell = self.__renderSettings.cells_per_block, self.__renderSettings.px_per_cell

        # Calculate pixel coordinates
        xpos = (x * cells_per_block + dx) * px_per_cell + (px_per_cell // 2)
        ypos = (y * cells_per_block + dy) * px_per_cell + (px_per_cell // 2)

        return (xpos, ypos)
    
    def render(self):

        # Iterate through cells
        for cell in self.cells:

            # Get a character
            char, color = self._get_cell_func(cell, self.QR, self.style, self.__renderSettings)

            # Call render cell
            self._renderCell(cell, char, color)

        # Then, return the canvas (should contain rendered image)
        return self.__canvas.image
            

    
    def _renderCell(self, currentCell: QRCell, character: str, color: Tuple[int, int, int]):

        # Get absolute x and y positions
        xpos, ypos = self._getXYPos(currentCell)

        self.__canvas.draw.text(
            (xpos, ypos), 
            character, 
            font=self.font, 
            fill=color, 
            anchor="mm")