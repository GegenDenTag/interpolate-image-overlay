import numpy as np
import gradio as gr
from copy import copy
from PIL import Image
import modules.scripts as scripts
from modules import processing, images
from modules.processing import Processed
from modules.shared import opts, state
import modules.images as images


""" 
MIT License
Copyright (c) 2023 gdt     image_overlay.py, adapted this script to my needs
Copyright (c) 2022 DiceOwl Interpolate.py https://github.com/DiceOwl/StableDiffusionStuff

""" 

def image_overlay(imgs, weights):
    n = [np.asarray(i.convert("RGB")) for i in imgs]
    img = n[0]*weights[0]    
    for i in range(1,len(imgs)):
        img += n[i]*weights[i]        
        # Exp: Stack Overflow Image.fromarray(img.astype('uint8'), mode='RGB')
    return Image.fromarray(img.astype(np.uint8))


class Script(scripts.Script):
    def __init__(self):    
        self.grids = []
        self.images = []
        self.images_grid = []

    def title(self):
        return "image overlay"

    def show(self, is_img2img):
        return is_img2img

    def ui(self, is_img2img):       
        #init_img2 = gr.Image(label="img2img image overlay", elem_id="img2img_image_overlay", show_label=False, source="upload", interactive=True, type="pil", visible=False)
        
        def gr_show(visible=True):
            return {"visible": visible, "__type__": "update"}

        def change_visibility(show):
            return {comp: gr_show(show) for comp in loopback_vis}
        
        # ToDo Dec, 2023
        # gr.image does not offer the possibility to access the file name and path of the uploaded image object.
        # Try to pass the path of the file via the gr.file component gr.image type="filepath", inputs=object_file
        loopback_vis = []   
        #with gr.Box(visible=True) as box:           
            #loopback_vis.append(box)  
        
        init_img2 = gr.Image(label="img2img image overlay", elem_id="img2img_image_overlay", show_label=False, source="upload", interactive=False, type="pil", visible=True)

        def preview(files, sd: gr.SelectData):            
            return files[sd.index].name
                       
        object_file = gr.File(file_types=["image"], file_count="binary")
        #object_file.select(change_visibility, inputs=object_file, outputs=loopback_vis)    
        # stupid overwrite     
        object_file.select(preview, object_file, init_img2)
                
        paragraph = gr.HTML(
            "<p style=\"margin-bottom:1em\">Upload an image or texture, and then overlay the previously stored image (found in the img2img upload dialog) in a loop consisting of 11 steps.</p>")
        
        return [init_img2]

    def run(self, p, init_img2):
        # empty lists
        self.grids *= 0
        self.images *= 0
        self.images_grid *= 0
        # Init
        """ only one overlay of the two images should be carried out,i.e. some must-haves """
        processing.fix_seed(p)
        init_seed = p.seed
        # Init images
        if not init_img2:
            return Processed(p, [], init_seed, "Upload an overlay image...")
        init_img = p.init_images[0]
        if not init_img:
            return Processed(p, [], init_seed, "Upload an image...")
        p.n_iter = 1
        p.batch_size = 1        
        p.denoising_strength = 0.01
        batch_count = p.n_iter
        p.width, p.height = init_img.size
        # Init Metadata
        """ Exp.: init_info = create_infotext(p, p.prompt, [p.seed], [p.subseed], [...]) """
        # binding nonlocal
        init_info = None
        """ ToDo: Understand the difference between info and prompt(subset of info?) """
        init_prompt = p.prompt
        init_negative = p.negative_prompt        
        """ ToDo: subseed and strength """
        # init_subseed = p.subseed
        # init_subseed_strength = p.subseed_strength      
        #p.extra_generation_params["image_overlay"] = str(init_img2[0].path)
        
        # opts.img2img_color_correction
        init_color_correction = [processing.setup_color_correction(p.init_images[0])]
        
        sequence =  [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        state.job_count = len(sequence) * batch_count

        def image_data(img_in):
            img = []
            nonlocal init_info
            
            for i in range(len(sequence)):
                pc = copy(p)
                pc.init_images = [img_in[i]]
                pc.n_iter = 1
                pc.batch_size = 1
                if opts.img2img_color_correction:
                    pc.color_corrections = init_color_correction
                state.job = f"Iteration {i + 1}/{len(sequence)}, batch {n + 1}/{batch_count}"
                processed = processing.process_images(pc)
                if init_info is None:                    
                    init_info = processed.info                    
                img.append(processed.images[0])
            return img
        
        # batch_count == 1
        for n in range(batch_count):  
            x = [image_overlay([init_img, init_img2], [1-min(1, max(0, i)), min(1, max(0, i))]) for i in sequence]
            y = image_data(x)
            self.images += y
            self.images_grid += y

        grid = images.image_grid(self.images_grid, rows=batch_count)
        if opts.grid_save:                            
            images.save_image(grid, p.outpath_grids, "img_overlay", init_seed, p.prompt, opts.grid_format, info=init_info, short_filename=opts.grid_extended_filename, grid=True, p=p)
            self.grids.append(grid)
        
        if opts.return_grid:
            self.images = self.grids + self.images       

        # IndexError: list index out of range, line 79
        # ui_common.py
        # def save_files(js_data, images, do_make_zip, index):
        #   ...       
        #   fullfn, txt_fullfn = modules.images.save_image(image, path, "", seed=p.all_seeds[i], prompt=p.all_prompts[i], extension=extension, info=p.infotexts[image_index], grid=is_grid, p=p, save_to_dirs=save_to_dirs)
        #   ...        
        seeds = [init_seed for i in self.images]
        prompts = [init_prompt for i in self.images]
        negative = [init_negative for i in self.images]
        infos = [init_info for i in self.images]
        
        processed = Processed(p, self.images, init_seed, info=init_info, all_seeds=seeds, all_prompts=prompts, all_negative_prompts=negative, infotexts=infos)
        return processed
