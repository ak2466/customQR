from PIL import Image, ImageDraw, ImageFont
import qrcode

# --- Settings ---
CELL_SIZE = 60  # Size of each QR code "cell" (in pixels)
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (220, 220, 220)
TEXT_BLOCK_SIZE = 3  # Size of the block (e.g., 2x2, 3x3, 4x4)
FILE_PATH = "qr.png"

class QR:
    def __init__(self, string):

        self.string = string
        self.data = self._getQRData()

        self.width = len(self.data[0])
        self.height = len(self.data)

    def _getQRData(self):

        # --- QR Generation ---
        qr = qrcode.QRCode(border=1)
        qr.add_data(self.string)
        qr.make()
        QRData = qr.get_matrix()

        return QRData

def getScaledFont(fontPath, testChar = "%"):

    # Step 1: Load with arbitrary small size first to measure
    base_font_size = 10
    font = ImageFont.truetype(font_path, base_font_size)

    # Step 2: Measure test character
    bbox = font.getbbox(testChar)
    char_width = bbox[2] - bbox[0]
    char_height = bbox[3] - bbox[1]

    # Step 3: Calculate scaling factor
    scale = CELL_SIZE / max(char_width, char_height)
    final_font_size = int(base_font_size * scale)

    # Step 4: Reload font at the correct size
    font = ImageFont.truetype(font_path, final_font_size)

    return font

def getImage(width, height):

    # --- Create Image ---
    img_width = width * CELL_SIZE * TEXT_BLOCK_SIZE
    img_height = height * CELL_SIZE * TEXT_BLOCK_SIZE

    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)

    return image, draw

def getCharacter(blockXY, relativeXY):

    # unpack tuple
    x, y = blockXY
    dx, dy = relativeXY

    # Set the text
    if y % 2 == 0:
        character = "HOLE"[x % 4]
    else:
        character = "LEHO"[x % 4]

    return character


def scaleImage(image, newSize):

    original_width, original_height = image.size
    target_width, target_height = newSize

    original_aspect = original_width / original_height
    target_aspect = target_width / target_height

    if original_aspect > target_aspect:
        new_height = target_height
        new_width = int(original_width * (target_height / original_height))
    else:
        new_width = target_width
        new_height = int(original_height * (target_width / original_width))

    resized_overlay = image.resize((new_width, new_height), Image.LANCZOS)

    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    cropping_box = (left, top, right, bottom)
    cropped_image = resized_overlay.crop(cropping_box)

    return cropped_image


def drawQR(qr, image, draw):

    # --- Draw QR Code with New "Thicker" Cells ---
    for y in range(qr.height):
        for x in range(qr.width):
            value = qr.data[y][x]
            
            # Decide the block size (e.g., alternating blocks for aesthetics)

            # Block color
            color = BLACK_COLOR if value else WHITE_COLOR

            # Draw a block of text for each "pixel" (with new cells based on block size)
            for dy in range(TEXT_BLOCK_SIZE):
                for dx in range(TEXT_BLOCK_SIZE):
                    xpos = (x * TEXT_BLOCK_SIZE + dx) * CELL_SIZE + CELL_SIZE // 2
                    ypos = (y * TEXT_BLOCK_SIZE + dy) * CELL_SIZE + CELL_SIZE // 2

                    character = getCharacter((x, y), (dx, dy))

                    # Center the text
                    draw.text((xpos, ypos), character, font=font, fill=color, anchor="mm")

    overlay = Image.open("images/PioneerLD_0001.jpg").convert("RGBA")
    print(image.size)
    halfsize = tuple(map(lambda x: x // 2, image.size))
    pos = tuple(map(lambda x: x - (x // 2), halfsize))
    overlay = scaleImage(overlay, halfsize)
    image.paste(overlay, pos)

    

    # --- Save Image ---
    image.save(FILE_PATH)
    print(f"Saved {FILE_PATH} ✅")








font_path = "fonts/times.ttf"
font = getScaledFont(font_path)
qr = QR("hole.cd")
image, draw = getImage(qr.width, qr.height)
drawQR(qr, image, draw)

