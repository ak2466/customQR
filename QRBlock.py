from .QREngine import QRGenerator, RenderSettings, QRRenderer, QRCell
from typing import Tuple, Protocol, Optional

# Define interface for cell rendering
class BlockRenderingProtocol(Protocol):

    def __call__(self, cell: QRCell, qr: QRGenerator, renderSettings: RenderSettings) -> Tuple[int, int, int]:
        ...

# Define QRBlockRenderer
class QRBlockRenderer:
    def __init__(self, 
                 QR: QRGenerator, 
                 renderSettings: RenderSettings,
                 block_rendering_protocol: Optional[BlockRenderingProtocol] = None):

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
        self.protocol = block_rendering_protocol if block_rendering_protocol else SimpleBlockProtocol()

    # Define function for converting cell values into pixel values
    def _getXYPos(self, cell: QRCell):

        # Calculate pixel coordinates
        xpos_start = (cell.x * 
                self.__renderSettings.cells_per_block + 
                cell.dx) * self.__renderSettings.px_per_cell
        
        ypos_start = (cell.y *
                self.__renderSettings.cells_per_block +
                cell.dx) * self.__renderSettings.px_per_cell
        
        xpos_end = ((cell.x + 1) * 
                self.__renderSettings.cells_per_block + 
                cell.dx) * self.__renderSettings.px_per_cell
        
        ypos_end = ((cell.y + 1) *
                self.__renderSettings.cells_per_block +
                cell.dx) * self.__renderSettings.px_per_cell

        # Return pixel values
        return (xpos_start, ypos_start, xpos_end, ypos_end)
    
    # Define function for rendering
    def render(self):

        # Iterate through cells
        for cell in self.cells:

            color = self.protocol(cell, self.QR, self.__renderSettings)

            # Call render cell
            self._renderCell(cell, color)

        # Then, return the canvas
        return self.__canvas.image
    
    # Define function for rendering a single cells
    def _renderCell(self, cell, color: Tuple[int, int, int]):

        # Get absolute x and y pixel positions
        xpos_start, ypos_start, xpos_end, ypos_end = self._getXYPos(cell)

        # Draw the square
        self.__canvas.draw.rectangle(
            xy=((xpos_start, ypos_start), (xpos_end, ypos_end)),
            fill=color,
        )

class SimpleBlockProtocol(BlockRenderingProtocol):

    def __init__(self,
                light_color: Tuple[int, int, int] = (255, 255, 255),
                dark_color: Tuple[int, int, int] = (0, 0, 0)):
        
        self.light_color = light_color
        self.dark_color = dark_color

    # Define actual action
    def __call__(self, cell: QRCell, qr: QRGenerator, renderSettings: RenderSettings):

        # Select color based on true/false val of QR
        color: Tuple[int, int, int] = self.dark_color if cell.value else self.light_color

        # Return color
        return color

             