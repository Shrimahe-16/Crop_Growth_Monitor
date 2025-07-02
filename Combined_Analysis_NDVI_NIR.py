from PIL import Image
import numpy as np
from matplotlib.colors import ListedColormap
import os
import pandas as pd
import glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from VARI import compute_vari_and_save
from NDVI import compute_ndvi_from_images

def combined_ndvi_vari_analysis(rgb_image_path, nir_image_path,
                                ndvi_folders=None, vari_folder=None,
                                ndvi_threshold=0.55, vari_threshold=0.175):
    """
    Performs combined NDVI and VARI analysis using RGB and NIR images.
    Returns the matplotlib figure for embedding in GUI.
    """
    # Set base folder explicitly
    base_folder = r"S:\RVCE\4th_sem\MCP\PBL\Display"
    base_name = os.path.splitext(os.path.basename(rgb_image_path))[0]

    # Run NDVI and VARI computations
    compute_vari_and_save(rgb_image_path)
    compute_ndvi_from_images(rgb_image_path, nir_image_path)

    # Auto-find NDVI/VARI output folders
    if ndvi_folders is None:
        ndvi_folders = sorted(glob.glob(os.path.join(base_folder, "ndvi_output*")), reverse=True)
    if vari_folder is None:
        vari_folder = os.path.join(base_folder, "vari_outputs_date")

    if not ndvi_folders:
        print("No NDVI output folder found.")
        return None

    ndvi_folder = ndvi_folders[0]

    # Validate folder existence
    if not os.path.exists(ndvi_folder):
        print(f"NDVI folder does not exist: {ndvi_folder}")
        return None
    if not os.path.exists(vari_folder):
        print(f"VARI folder does not exist: {vari_folder}")
        return None

    # Debug: list files in folder
    print("Files in NDVI folder:", os.listdir(ndvi_folder))
    print("Files in VARI folder:", os.listdir(vari_folder))

    # Auto-find NDVI and VARI image paths
    def find_image(folder, base_name, indicator):
        for file in os.listdir(folder):
            fname = file.lower()
            if fname == f"{indicator}_{base_name.lower()}.png" or \
               fname == f"{base_name.lower()}_{indicator}.png":
                return os.path.join(folder, file)
        return None

    ndvi_img_path = find_image(ndvi_folder, base_name, "ndvi")
    vari_img_path = find_image(vari_folder, base_name, "vari")

    if ndvi_img_path is None:
        print(f"NDVI image for {base_name} not found in {ndvi_folder}.")
        return None
    if vari_img_path is None:
        print(f"VARI image for {base_name} not found in {vari_folder}.")
        return None

    # Load CSV stats
    ndvi_csv_path = os.path.join(base_folder, "ndvi_analysis_date.csv")
    if not os.path.exists(ndvi_csv_path):
        print(f"NDVI CSV not found: {ndvi_csv_path}")
        return None

    # Load grayscale images
    ndvi_img = Image.open(ndvi_img_path).convert('L')
    vari_img = Image.open(vari_img_path).convert('L')
    ndvi_array = np.array(ndvi_img) / 255.0
    vari_array = np.array(vari_img) / 255.0

    # Load CSV stats
    ndvi_df = pd.read_csv(ndvi_csv_path)
    ndvi_stats = ndvi_df.iloc[-1]

    # Combined mask generation
    combined_mask = np.zeros_like(ndvi_array)
    combined_mask[(ndvi_array >= ndvi_threshold) & (vari_array >= vari_threshold)] = 1
    combined_mask[(ndvi_array >= ndvi_threshold) & (vari_array < vari_threshold)] = 2

    # Create ONE figure
    fig, axs = plt.subplots(1, 3, figsize=(12, 4), dpi=150)

    # ---------- NDVI Plot ----------
    im1 = axs[0].imshow(ndvi_array, cmap='RdYlGn', vmin=0, vmax=1)
    axs[0].set_title(f"NDVI: {os.path.basename(ndvi_img_path)}", fontsize=10)
    axs[0].axis('off')
    fig.colorbar(im1, ax=axs[0], fraction=0.046, pad=0.04)

    # ---------- Combined NDVI + VARI Plot ----------
    cmap_combined = ListedColormap(['red', 'green', 'blue'])
    im_combined = axs[1].imshow(combined_mask, cmap=cmap_combined, vmin=0, vmax=2)
    axs[1].set_title("NDVI + VARI Combined", fontsize=10)
    axs[1].axis('off')
    cbar_combined = fig.colorbar(im_combined, ax=axs[1], ticks=[0, 1, 2], fraction=0.046, pad=0.04)
    cbar_combined.ax.set_yticklabels(['Non-Veg', 'Healthy', 'Potential Stress'], fontsize=7)

    # ---------- Histogram ----------
    axs[2].hist(ndvi_array.flatten(), bins=50, alpha=0.5, label='NDVI', color='green')
    axs[2].hist(vari_array.flatten(), bins=50, alpha=0.5, label='VARI', color='orange')
    axs[2].axvline(ndvi_threshold, color='green', linestyle='--', label='NDVI Threshold')
    axs[2].axvline(vari_threshold, color='orange', linestyle='--', label='VARI Threshold')
    axs[2].set_title("Threshold Histogram", fontsize=10)
    axs[2].set_xlabel("Value", fontsize=8)
    axs[2].set_ylabel("Pixel Count", fontsize=8)
    axs[2].tick_params(axis='both', which='major', labelsize=7)
    axs[2].legend(fontsize=6, loc='upper left')

    plt.tight_layout(pad=1.0)
    return fig

if __name__ == "__main__":
    compute_vari_and_save(r"RGB_Images\Test_1_RGB.jpg")
    compute_ndvi_from_images(r"S:\RVCE\4th_sem\MCP\PBL\Display\RGB_Images\Test_1_RGB.jpg",
                             r"NIR_Images\Test_1_NIR.jpg")
    combined_ndvi_vari_analysis(r"RGB_Images\Test_1_RGB.jpg", r"NIR_Images\Test_1_NIR.jpg")