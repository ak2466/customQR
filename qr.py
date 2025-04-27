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

# --- Draw QR Code ---
for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        value = ascii_qr[y][x]
        
        if value:
            text = "HOLE"[x%4]
        else:
            text = "HOLE"[x%4]
        color = BLACK_COLOR if value else WHITE_COLOR

        xpos = x * CELL_SIZE + CELL_SIZE // 2
        ypos = y * CELL_SIZE + CELL_SIZE // 2

        # Center the text
        draw.text((xpos, ypos), text, font=font, fill=color, anchor="mm")

# --- Save Image ---
image.save("qr_times_new_roman_hole.png")
print("Saved qr_times_new_roman_hole.png ✅")
