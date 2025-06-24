from .QREngine import QRGenerator, RenderSettings, QRRenderer, QRCell
from typing import Tuple, Protocol

# Define interface for cell rendering
class BlockRenderingProtocol(Protocol):

    def __call__(self, cell: QRCell, qr: QRGenerator, renderSettings: RenderSettings) -> Tuple[str, Tuple[int, int, int]]:
        ...

# Define QRBlockRenderer
class QRBlockRenderer:
    def __init__(self, 
                 QR: QRGenerator, 
                 renderSettings: RenderSettings,
                 cell_rendering_protocol: BlockRenderingProtocol):

        # Set QRData
        self.QR = QR

        # Set render settings
        self.__renderSettings = renderSettings

        # Create a base renderer
        self.__renderer = QRRenderer(self.QR, renderSettings)

        # Get the canvas
        self.__canvas = self.__renderer.get_canvas()

        # Get the cells
        self.cells = self.__renderer.get_cells()

        # Set get cell function
        self._get_cell_func = cell_rendering_protocol

    # Define function for converting cell values into pixel values
    def _getXYPos(self, cell: QRCell):

        # Calculate pixel coordinates
        xpos = (cell.x * 
                self.__renderSettings.cells_per_block + 
                cell.dx) * self.__renderSettings.px_per_cell
        
        ypos = (cell.y *
                self.__renderSettings.cells_per_block +
                cell.dx) * self.__renderSettings.px_per_cell

        # Return pixel values
        return (xpos, ypos)
    
    # Define function for rendering
    def render(self):

        # Iterate through cells
        for cell in self.cells:

            color = (255, 100, 255)

            # Call render cell
            self._renderCell(cell, color)

        # Then, return the canvas
        return self.__canvas.image
    
    # Define function for rendering a single cells
    def _renderCell(self, cell, color: Tuple[int, int, int]):

        # Get absolute x and y pixel positions
        xpos, ypos = self._getXYPos(cell)

        # Draw the square
        self.__canvas.draw.rectangle(
            xy=((xpos, ypos), (xpos + 5, ypos + 5)),
            fill=color,

        )

             