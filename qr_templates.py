from .QREngine import QRCell, QRGenerator, RenderSettings
from .QRText import QRTextBlockRenderer, QRTextStyle, CellRenderingProtocol
from typing import Tuple

class RepeatingTextStrategy(CellRenderingProtocol):

    def __init__(self, 
                    string: str, 
                    overwrap: bool = False, 
                    light_color: Tuple[int, int, int] = (220, 220, 220),
                    dark_color: Tuple[int, int, int] = (0, 0, 0),
                    offset = 0,
                    shift = 0
                    ):
        
        self._overwrap = overwrap
        self._string = string

        self._light_color = light_color
        self._dark_color = dark_color

        self._offset = offset
        self._shift = shift

    def __call__(self, cell: QRCell, qr: QRGenerator, style: QRTextStyle, renderSettings: RenderSettings) -> Tuple[str, Tuple[int, int, int]]:

        def _getAbsolutePositions(cell: QRCell, style):
            absolute_x = cell.x * renderSettings.cells_per_block + cell.dx
            absolute_y = cell.y * renderSettings.cells_per_block + cell.dy
            total_rendered_cells_per_row = qr.width * renderSettings.cells_per_block
            absolute_index = (absolute_y * total_rendered_cells_per_row + absolute_x)

            return absolute_x, absolute_y, absolute_index

        # If cell is true, 
        if cell.value:
            color = self._dark_color
        else:
            color = self._light_color
        
        abs_x, abs_y, abs_index = _getAbsolutePositions(cell, style)
        shift = self._shift * abs_y

        if self._overwrap:
            character = self._string[(abs_index + self._offset + shift) % len(self._string)]
        else:
            character = self._string[(abs_x + self._offset + shift) % len(self._string)]

        return (character, color)

