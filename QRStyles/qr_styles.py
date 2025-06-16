from qr_engine import QRTextStyle, QRTextBlockRenderer, QRGenerator
from qr_templates import RepeatingTextStrategy

def __main__():

    qr = QRGenerator("https://hole.cd")
    style = QRTextStyle(
        font_path="fonts/times.ttf",
        cells_per_block=3
    )

    text_strategy = RepeatingTextStrategy("HOLE", overwrap=False, shift=2)
    renderer = QRTextBlockRenderer(qr, style, text_strategy)

    image = renderer.render()
    image.show()

if __name__ == "__main__":
    __main__()