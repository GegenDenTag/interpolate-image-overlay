# interpolate-image-overlay
personal script 2024-04-23
Automatic1111
The script mixes the output of img2img with the original input image in alpha strength. This allows the script to provide 
a second image or a texture file for an effect (e.g. watercolor, fog, spotlight, sun rays, etc.) via the upload dialog 
in the script area, to then add this effect to the original image (img2img).

The script uses alpha blending. The original image is overlaid in a loop over 11 steps with increasing alpha strength, 
starting at 0.0 - no change, and ending at 1.0 with the complete overlay of the original image and the display of the second image.

From the generated intermediate images, the desired result can then be selected.

As a basis, I used the script from DiceOwl, MIT License Copyright © 2022, Interpolate.py https://github.com/DiceOwl/StableDiffusionStuff, 
and adapted it to my needs. I would like to thank him for his work.

A few notes on this: 
Both images need to have the same dimensions. The upload of the original image should take place in the img2img area, the second image in the script area. 
(At the moment, the upload can still take place arbitrarily, the intermediate images are output accordingly in a changed order. 
But I am probably planning to expand the script in such a way that the metadata of the original image is read out and used at runtime) 

Currently, the same seed is assigned to the intermediate images, “Batch count” and “Batch size” are set to 1 at runtime, 
size: width and height to the values of the original image, and the “Denoising strength” value to 0.01, as only an overlay of both images should take place.

Automatic1111 v.1.6.0 "With textures with transparency, it can also become black." 😒 
Under the settings “With img2img, fill transparent parts of the input image with this color.” a desired color can be stored, which fills transparent areas. 
An option that transparency is actually recognized and maintained apparently does not exist. 
