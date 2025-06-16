from qr_engine import *

def main():

    qr = QRGenerator("https://hole.cd")
    
    class RepeatingTextStrategy(CellRenderingProtocol):

        def __init__(self, string: str, overwrap: bool = False):
            self._overwrap = overwrap
            self._string = string

        def __call__(self, cell: QRCell, qr: QRGenerator, style: QRTextStyle) -> Tuple[str, Tuple[int, int, int]]:

            def _getAbsolutePositions(cell: QRCell, style):
                absolute_x = cell.x * style.cells_per_block + cell.dx
                absolute_y = cell.y * style.cells_per_block + cell.dy
                total_rendered_cells_per_row = qr.width * style.cells_per_block
                absolute_index = (absolute_y * total_rendered_cells_per_row + absolute_x)

                return absolute_x, absolute_y, absolute_index

            on_color = (220, 220, 220)
            off_color = (0, 0, 0)

            if cell.value:
                color = on_color
            else:
                color = off_color
            
            abs_x, abs_y, abs_index = _getAbsolutePositions(cell, style)

            if self._overwrap:
                character = self._string[abs_index % len(self._string)]
            else:
                character = self._string[abs_x % len(self._string)]

            return (character, color)
            

    style = QRTextStyle(
        font_path="fonts/times.ttf",
        cells_per_block=3
    )

    hole_text = RepeatingTextStrategy("HOLE", overwrap=True)

    renderer = QRTextBlockRenderer(qr, style, hole_text)

    image = renderer.render()
    image.show()
    image.save("newqr.png")
    

if __name__ == "__main__":
    main()


