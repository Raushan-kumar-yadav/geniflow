from skimage.restoration import inpaint
from skimage import io, color

# Load the image and mask
image = io.imread('image2.jpg')
mask = io.imread('mask2.png', as_gray=True) > 0.5

# Perform inpainting
result = inpaint.inpaint_biharmonic(image, mask)

# Save the result
io.imsave('output3.jpg', result)
