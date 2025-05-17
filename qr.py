from PIL import Image, ImageDraw, ImageFont
import qrcode

# --- Settings ---
CELL_SIZE = 50  # Size of each QR code "cell" (in pixels)
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (220, 220, 220)
TEXT_BLOCK_SIZE = 2  # Size of the block (e.g., 2x2, 3x3, 4x4)
FILE_PATH = "qr.png"

# ✅
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
    
class QRText:
    def __init__(self, font_path):
        
        self.font = self._getScaledFont(font_path)

    def _getScaledFont(font_path, testChar = "%"):

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



# ✅
def getCanvas(width, height):

    # --- Create Image ---
    img_width = width * CELL_SIZE * TEXT_BLOCK_SIZE
    img_height = height * CELL_SIZE * TEXT_BLOCK_SIZE

    canvas = Image.new("RGBA", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)

    return canvas, draw

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

def setBackground(canvas):

    width, height = canvas.size
    imageWithBackground = Image.new("RGB", (width, height), "white")

    imageWithBackground.paste(canvas)

    return imageWithBackground

#✅
def tintImage(image, color, intensity=0.4):

    # check if image mode isn't RGBA
    if image.mode != 'RGBA':

        # convert image to RGBA
        image = image.convert('RGBA')

    # generate tint layer
    tint_layer = Image.new('RGBA', image.size, color)

    # return blended image
    return Image.blend(image, tint_layer, intensity)



# ✅
def scaleImage(image, newSize):

    # Get original width and height
    original_width, original_height = image.size

    # Get tarrget width and height
    target_width, target_height = newSize

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
    resized_overlay = image.resize((new_width, new_height), Image.LANCZOS)

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


# ✅
def placeImageBlock(canvas, position, overlay):

    # get the relative coordinates
    xpos, ypos = getXYPos(position)

    xpos = xpos - overlay.width // 2
    ypos = ypos - overlay.height // 2

    # paste the image at this location
    canvas.paste(overlay, (xpos, ypos))

def placeCharacterBlock(draw, font, position, character, color):
    
    # get the relative coordinates
    xpos, ypos = getXYPos(position)

    draw.text((xpos, ypos), character, font=font, fill=color, anchor="mm")


# ✅
def getXYPos(position):

    x, y, dx, dy = position

    xpos = (x * TEXT_BLOCK_SIZE + dx) * CELL_SIZE + CELL_SIZE // 2
    ypos = (y * TEXT_BLOCK_SIZE + dy) * CELL_SIZE + CELL_SIZE // 2

    return (xpos, ypos)

def drawQR(qr, canvas, draw, font, overlays):

    # --- Draw QR Code with New "Thicker" Cells ---
    for y in range(qr.height):
        for x in range(qr.width):
            value = qr.data[y][x]
            
            # Decide the block size (e.g., alternating blocks for aesthetics)

            # Block color
            color = BLACK_COLOR if value else WHITE_COLOR

            black_overlay, white_overlay = overlays
            overlay = black_overlay if value else white_overlay

            # Draw a block of text for each "pixel" (with new cells based on block size)
            for dy in range(TEXT_BLOCK_SIZE):
                for dx in range(TEXT_BLOCK_SIZE):

                    character = getCharacter((x, y), (dx, dy))

                    placeImageBlock(canvas, (x, y, dx, dy), overlay)
                    placeCharacterBlock(draw, font, (x, y, dx, dy), character, color)

    return canvas

def main():

    font_path = "fonts/times.ttf"
    font = getScaledFont(font_path)
    qr = QR("https://hole.cd")

    overlay = Image.open("images/laserdisc.jpg").convert("RGBA")
    overlay = scaleImage(overlay, (CELL_SIZE, CELL_SIZE)) # Scale once per cell block

    white_overlay = tintImage(overlay, (255, 255, 255), 0.7)
    black_overlay = tintImage(overlay, (0, 0, 0), 0.75)

    canvas, draw = getCanvas(qr.width, qr.height)
    drawing = drawQR(qr, canvas, draw, font, (black_overlay, white_overlay))

    #drawing = setBackground(drawing)
    drawing.save(FILE_PATH)
    print(f"Saved {FILE_PATH} ✅")

    
    
if __name__ == "__main__":
    main()


