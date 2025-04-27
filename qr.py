from PIL import Image, ImageDraw, ImageFont
import qrcode

# --- QR Generation ---
qr = qrcode.QRCode(border=1)
qr.add_data("https://hole.cd")
qr.make()
ascii_qr = qr.get_matrix()

# --- Settings ---
CELL_SIZE = 70
GRID_WIDTH = len(ascii_qr[0])
GRID_HEIGHT = len(ascii_qr)
text_block_size = 3  # Size of the block (2x2, 3x3, 4x4) to represent each "pixel"

font_path = "fonts/times.ttf"

# Step 1: Load with arbitrary small size first to measure
base_font_size = 10
font = ImageFont.truetype(font_path, base_font_size)

# Step 2: Measure "%" character
test_char = "%"
bbox = font.getbbox(test_char)
char_width = bbox[2] - bbox[0]
char_height = bbox[3] - bbox[1]

# Step 3: Calculate scaling factor
scale = CELL_SIZE / max(char_width, char_height)
final_font_size = int(base_font_size * scale)

# Step 4: Reload font at the correct size
font = ImageFont.truetype(font_path, final_font_size)

# --- Create Image ---
img_width = GRID_WIDTH * CELL_SIZE
img_height = GRID_HEIGHT * CELL_SIZE

image = Image.new("RGB", (img_width, img_height), "white")
draw = ImageDraw.Draw(image)

BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (220, 220, 220)

# --- Draw QR Code with Text Blocks ---
for y in range(0, GRID_HEIGHT, text_block_size):
    for x in range(0, GRID_WIDTH, text_block_size):
        # Get block of QR code data (this will decide the color of the block)
        block_value = ascii_qr[y][x]

        # Text for the block (we'll use "HOLE" / "LEHO" just like before)
        if y % 2 == 0:
            text = "HOLE"[x % 4]
        else:
            text = "LEHO"[x % 4]

        color = BLACK_COLOR if block_value else WHITE_COLOR

        # Draw the block: filling the area of text_block_size x text_block_size
        for dy in range(text_block_size):
            for dx in range(text_block_size):
                xpos = (x + dx) * CELL_SIZE + CELL_SIZE // 2
                ypos = (y + dy) * CELL_SIZE + CELL_SIZE // 2

                # Center the text
                draw.text((xpos, ypos), text, font=font, fill=color, anchor="mm")

# --- Save Image ---
image.save("qr_times_new_roman_hole_thick.png")
print("Saved qr_times_new_roman_hole_thick.png ✅")
