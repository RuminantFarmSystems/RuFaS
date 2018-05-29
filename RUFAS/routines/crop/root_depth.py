def calculate_z_root(crop):
    fr_root = 0.4 - 0.2 * crop.fr_PHU # What is fr_root used for ? -Andy
    
    if crop.crop_type == "perennial":
        crop.z_root = crop.z_root_max
    elif crop.crop_type == "annual" and crop.fr_PHU > 0.4:
        crop.z_root = crop.z_root_max
    else: # crop_type == "annual" and self.fr_PHU <= 0.4
        crop.z_root = 2.5 * crop.fr_PHU * crop.z_root_max
        
