from dataclasses import dataclass
from typing import Optional, Tuple
from PIL import Image as PILImage

from .QREngine import QRCell, QRRenderer, QRGenerator, RenderSettings

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

# Define QRImageBlockRenderer
class QRImageBlockRenderer:
    def __init__(self, QR: QRGenerator, style: QRImageStyle, renderSettings: RenderSettings):

        # Set QRData
        self.QR = QR

        # Set style
        self.style = style

        # Set render settings
        self.__renderSettings = renderSettings


        # Create a base renderer
        self.__renderer = QRRenderer(self.QR, self.__renderSettings)

        # Get the cells
        self.cells = self.__renderer.get_cells()

        # Get the canvas
        self.__canvas = self.__renderer.get_canvas()

        # Set tints
        # First value: color
        # Second value: opacity of tint
        self.onTint = ((0, 0, 0), 0.75)
        self.offTint = ((255, 255, 255), 0.7)


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
        return self.__canvas.image

    
    # Define a function to render a cell
    def _renderCell(self, 
                    currentCell: QRCell,
                    image: PILImage.Image):

        # Get the pixel coordinates
        xpos, ypos = self._getXYPos(currentCell)

        # paste the image at this location
        self.__canvas.image.paste(image, (xpos, ypos))
    
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