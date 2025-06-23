from PIL import Image as PILImage, ImageDraw, ImageFont
import qrcode
from dataclasses import dataclass
from typing import Optional, Tuple, Callable, Protocol

@dataclass
class RenderCanvas:
    image: PILImage.Image
    draw: ImageDraw.ImageDraw

@dataclass
class RenderSettings:

    # Render settings
    px_per_cell: int = 50
    cells_per_block: int = 2

# Define QRGenerator class
class QRGenerator:

    # Define initializer
    def __init__(self, QRString: str):


        # Assign the QR string and the QR Data Matrix
        self.QRString: str = QRString
        self.QRData: list[list[bool]] = self._getQRData()

        # Assign width and height
        self.width = len(self.QRData[0])
        self.height = len(self.QRData)

    # Define function to generate QR code data
    def _getQRData(self):

        # Create QR object
        qr = qrcode.QRCode(border=1)

        # Add data to the QR code and make it
        qr.add_data(self.QRString)
        qr.make()

        # Extract the QR data
        QRData = qr.get_matrix()

        # Return the QR Data Matrix
        return QRData

# Define a class for storing a single QR Cell
@dataclass
class QRCell:
    x: int
    y: int
    dx: int
    dy: int
    value: bool

@dataclass
class QRTextStyle:

    # Font path
    font_path: str


@dataclass
class QRImageStyle:

    # Base image filename
    base_image_filename: Optional[str] = None

    # 2-image style
    # Images are stored as filenames that will be opened by the renderer
    on_image_filename: Optional[str] = None
    off_image_filename: Optional[str] = None

    # tint style
    on_tint: Optional[Tuple[Tuple[int, int, int], float]] = None
    off_tint: Optional[Tuple[Tuple[int, int, int], float]] = None

    # Render settings
    px_per_cell: int = 50
    cells_per_block: int = 2

    # Post init to validate we have exactly one style
    def __post_init__(self):

        # Set boolean values to check if we either have two images or two tints
        two_image_set = self.on_image_filename is not None and self.off_image_filename is not None
        two_tint_set = self.on_tint is not None and self.off_tint is not None

        # Check for presence of neither values
        if not (two_image_set or two_tint_set):

            # If neither present, raise ValueError
            raise ValueError (
                "You must provide either both on/off images or both on/off tints."
            )
        
        # Check for presence of both values
        if two_image_set and two_tint_set:

            # Raise ValueError (can only be one)
            raise ValueError (
                "You must provide either image pair or tint pair, not both."
            )
    
# Define interface for cell rendering
class CellRenderingProtocol(Protocol):

    def __call__(self, cell: QRCell, qr: QRGenerator, style: QRTextStyle, renderSettings: RenderSettings) -> Tuple[str, Tuple[int, int, int]]:
        ...


# Define QRRenderer base class
class QRRenderer:

    # Define initializer
    def __init__(self, QR: QRGenerator, renderSettings: RenderSettings):

        # Set QRdata
        self.__QR = QR

        # Set RenderSettings
        self.__renderSettings = RenderSettings

    # Define get cells function
    def get_cells(self):

        # Create list for storing strings
        cells = []

        # Iterate through pixels of the QR Code
        for y in range(self.__QR.height):
            for x in range(self.__QR.width):

                # Get the value at the current position of the QR matrix
                value = self.__QR.QRData[y][x]

                # Iterate through the pixels in the current QR block
                for dy in range(self.__renderSettings.cells_per_block):
                    for dx in range(self.__renderSettings.cells_per_block):

                        # Create cell and add it to list
                        cells.append(QRCell(x, y, dx, dy, value))

        # Return cells list
        return cells
    
    def get_canvas(self):

        # Calculate image width and height
        width = self.__QR.width * self.__renderSettings.cells_per_block * self.__renderSettings.px_per_cell
        height = self.__QR.height * self.__renderSettings.cells_per_block * self.__renderSettings.px_per_cell

        # Initialize new image and draw classes
        image = PILImage.new("RGBA", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # Combine into renderCanvas dataclass
        canvas = RenderCanvas(image, draw)

        # Return the canvas
        return canvas







# Define QRTextBlockRenderer
class QRTextBlockRenderer:

    def __init__(self, 
                 QR: QRGenerator, 
                 style: QRTextStyle,
                 renderSettings: RenderSettings,
                 cell_rendering_protocol: CellRenderingProtocol):

        # Set QRData
        self.QR = QR

        # Set style
        self.style = style
    
        # Set render settings
        self.__renderSettings = renderSettings

        # Set get cell function
        self._get_cell_func = cell_rendering_protocol

        # Get font
        self.font = self._getScaledFont()

        # Create a renderer
        self.__renderer = QRRenderer(self.QR, self.__renderSettings)

        # Get the canvas
        self.__canvas = self.__renderer.get_canvas()

        # Get cells
        self.cells = self.__renderer.get_cells()

    def _getScaledFont(self, testChar = "%"):

        # Step 1: Load with arbitrary small size first to measure
        base_font_size = 10
        font = ImageFont.truetype(self.style.font_path, base_font_size)

        # Step 2: Measure test character
        bbox = font.getbbox(testChar)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]

        # Step 3: Calculate scaling factor
        scale = self.__renderSettings.px_per_cell / max(char_width, char_height)
        final_font_size = int(base_font_size * scale)

        # Step 4: Reload font at the correct size
        font = ImageFont.truetype(self.style.font_path, final_font_size)

        return font
    
    def _getXYPos(self, currentCell: QRCell):

        # Extract
        x, y = currentCell.x, currentCell.y
        dx, dy = currentCell.dx, currentCell.dy
        cells_per_block, px_per_cell = self.__renderSettings.cells_per_block, self.__renderSettings.px_per_cell

        # Calculate pixel coordinates
        xpos = (x * cells_per_block + dx) * px_per_cell + (px_per_cell // 2)
        ypos = (y * cells_per_block + dy) * px_per_cell + (px_per_cell // 2)

        return (xpos, ypos)
    
    def render(self):

        # Iterate through cells
        for cell in self.cells:

            # Get a character
            char, color = self._get_cell_func(cell, self.QR, self.style, self.__renderSettings)

            # Call render cell
            self._renderCell(cell, char, color)

        # Then, return the canvas (should contain rendered image)
        return self.__canvas.image
            

    
    def _renderCell(self, currentCell: QRCell, character: str, color: Tuple[int, int, int]):

        # Get absolute x and y positions
        xpos, ypos = self._getXYPos(currentCell)

        self.__canvas.draw.text(
            (xpos, ypos), 
            character, 
            font=self.font, 
            fill=color, 
            anchor="mm")
        





# Define QRBlockRenderer
class QRBlockRenderer:
    def __init__(self, QR: QRGenerator, renderSettings: RenderSettings):

        # Set QRData
        self.QR = QR

        # Set render settings
        self.__renderSettings = renderSettings

        # Create a base renderer
        self.__renderer = QRRenderer(self.QR, renderSettings)

        # Get the canvas
        self._canvas = self.__renderer.get_canvas()

        # Get the cells
        self.cells = self.__renderer.get_cells()









    
# Define QRImageBlockRenderer
class QRImageBlockRenderer:
    def __init__(self, QR: QRGenerator, style: QRImageStyle, renderSettings: RenderSettings):

        # Set QRData
        self.QR = QR

        # Set style
        self.style = style

        # Set render settings
        self.__renderSettings = renderSettings

        # Get the canvas
        self.canvas = self._getImageCanvas()

        # Create a base renderer
        self.__renderer = QRRenderer(self.QR, self.__renderSettings)

        # Get the cells
        self.cells = self.__renderer.get_cells()

        # Set tints
        # First value: color
        # Second value: opacity of tint
        self.onTint = ((0, 0, 0), 0.75)
        self.offTint = ((255, 255, 255), 0.7)

    # getCells went here

    def _getImageCanvas(self):

        # Calculate image width and height
        img_width = self.QR.width * self.style.cells_per_block * self.style.px_per_cell
        img_height = self.QR.height * self.style.cells_per_block * self.style.px_per_cell

        # Initialize new image and draw classes
        image = PILImage.new("RGBA", (img_width, img_height), "white")
        draw = ImageDraw.Draw(image)

        # Combine into renderCanvas dataclass
        canvas = RenderCanvas(image, draw)

        # Return the canvas
        return canvas

    def _getXYPos(self, currentCell: QRCell):

        # Calculate pixel coordinates
        xpos = (currentCell.x * self.style.cells_per_block + currentCell.dx) * self.style.px_per_cell
        ypos = (currentCell.y * self.style.cells_per_block + currentCell.dy) * self.style.px_per_cell

        return (xpos, ypos)


    # Define function to open the image
    def _openImage(self, filename):

        # Open the image
        image: PILImage.Image = PILImage.open(filename).convert("RGBA")

        # Scale the image
        image = self._scaleImage(image)

        # Return the image
        return image
    
    # Create render function
    def render(self):

        # Get on / off images if present
        if self.style.on_image_filename and self.style.off_image_filename:
            onImage = self._openImage(self.style.on_image_filename)
            offImage = self._openImage(self.style.off_image_filename)

        # Otherwise, assume tint was passed
        else:

            baseImage = self._openImage(self.style.base_image_filename)

            # Check if tints are not none
            if self.style.on_tint is not None:
                onImage = self._tintImage(baseImage, self.style.on_tint)
            else:
                onImage = baseImage.copy()

            if self.style.off_tint is not None:
                offImage = self._tintImage(baseImage, self.style.off_tint)
            else:
                offImage = baseImage.copy()


        # Iterate through cells
        for cell in self.cells:

            # Get the correct tinted image depending on if cell value is true or not
            image = onImage if cell.value else offImage

            # Call render cell
            self._renderCell(cell, image)

        # Return the canvas (should contain rendered image)
        return self.canvas.image

    
    # Define a function to render a cell
    def _renderCell(self, 
                    currentCell: QRCell,
                    image: PILImage.Image):

        # Get the pixel coordinates
        xpos, ypos = self._getXYPos(currentCell)

        # paste the image at this location
        self.canvas.image.paste(image, (xpos, ypos))
    
    # Define function to scale image to fit and crop to square
    def _scaleImage(self, image):

        # Get original width and height
        original_size: tuple[int, int] = image.size
        original_width, original_height = original_size

        # Get target width and height from settings
        target_width =  target_height = self.style.px_per_cell

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
        resized_overlay = image.resize((new_width, new_height), PILImage.LANCZOS) # type: ignore

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
    
    def _tintImage(self, originalImage: PILImage.Image, tint: Tuple[Tuple[int, int, int], float]):

        # check if image mode isn't RGBA
        if originalImage.mode != 'RGBA':

            # convert image to RGBA
            originalImage = originalImage.convert('RGBA')

        # generate tint layer
        tint_layer = PILImage.new('RGBA', originalImage.size, tint[0])

        # return blended image
        return PILImage.blend(originalImage, tint_layer, tint[1])

             