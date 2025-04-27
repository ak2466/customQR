from PIL import Image, ImageDraw, ImageFont

#print("".join("██" if cell else "  " for cell in row))
#print("".join("HOLE" if cell else "  " for cell in row))
#print("".join("H" if cell else "  " for cell in row))
#print("".join("◻️" if cell else "◾️" for cell in row))
#print("".join("██" if cell else "  " for cell in row))

'''even = False
for row in ascii_qr:
    if even:
        print("".join("HO" if cell else "  " for cell in row))
    else:
        print("".join("LE" if cell else "  " for cell in row))

    even = not even
    '''

'''
for index in range(0, len(ascii_qr)):
    print("".join("HOLE" if cell else "    " for cell in ascii_qr[index]))
    print("".join("LEHO" if cell else "    " for cell in ascii_qr[index]))
    '''

import qrcode

qr = qrcode.QRCode(border=1)
qr.add_data("https://hole.cd")
qr.make()

ascii_qr = qr.get_matrix()

CELL_HEIGHT = 40
CELL_WIDTH = 40

GRID_WIDTH = len(ascii_qr[0])
GRID_HEIGHT = len(ascii_qr)

font_path = "fonts/times.ttf"
font_size = 16
font = ImageFont.truetype(font_path, font_size)

img_width = GRID_WIDTH * CELL_WIDTH
img_height = GRID_HEIGHT * CELL_HEIGHT

image = Image.new("RGB", (img_width, img_height), "white")
draw = ImageDraw.Draw(image)

BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (220, 220, 220)


for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        value = ascii_qr[y][x]
        
        text_top = "H" if value else "    "
        text_bottom = "H" if value else "    "

        xpos = x * CELL_WIDTH
        ypos = y * CELL_HEIGHT

        # Draw top line
        draw.text((xpos, ypos), text_top, font=font, fill=BLACK_COLOR if value else WHITE_COLOR)

# --- Save Image ---
image.save("qr_times_new_roman_hole.png")
print("Saved qr_times_new_roman_hole.png ✅")