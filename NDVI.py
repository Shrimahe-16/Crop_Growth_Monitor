from PIL import Image
import numpy as np
import os
import pandas as pd
from datetime import datetime

def compute_ndvi_from_images(
        rgb_image_path,
        nir_image_path,
        output_folder='ndvi_outputs_date',
        csv_path='ndvi_analysis_date.csv'
    ):
    """
    Computes NDVI from a single RGB image and a NIR image.
    Saves the NDVI heatmap, computes statistics, and updates the CSV log.
    """

    os.makedirs(output_folder, exist_ok=True)

    if not os.path.exists(rgb_image_path):
        print(f"❌ RGB image '{rgb_image_path}' not found.")
        return
    if not os.path.exists(nir_image_path):
        print(f"❌ NIR image '{nir_image_path}' not found.")
        return

    # === Load RGB and NIR images ===
    rgb_img = Image.open(rgb_image_path).convert('RGB')
    nir_img = Image.open(nir_image_path).convert('L')

    red = np.asarray(rgb_img)[..., 0].astype(float) / 255.0
    nir = np.asarray(nir_img).astype(float) / 255.0

    # === Compute NDVI ===
    ndvi = (nir - red) / (nir + red + 1e-5)

    # === Scale to 0–255 and save image ===
    ndvi_scaled = ((ndvi + 1) / 2 * 255).astype(np.uint8)
    ndvi_image = Image.fromarray(ndvi_scaled)

    base_name = os.path.splitext(os.path.basename(rgb_image_path))[0]
    output_image_name = f"{base_name}_ndvi.png"
    output_image_path = os.path.join(output_folder, output_image_name)
    ndvi_image.save(output_image_path)

    # === Rescale for consistent analysis ===
    ndvi = (ndvi_scaled / 255.0) * 2 - 1

    # === Compute statistics ===
    mean_ndvi = np.mean(ndvi)
    total_pixels = ndvi.size
    healthy = (ndvi > 0.6)
    moderate = (ndvi > 0.2) & (ndvi <= 0.6)
    sparse = (ndvi >= 0.0) & (ndvi <= 0.2)
    barren = (ndvi < 0.0)

    upload_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    stats = {
        "DateTime": upload_datetime,
        "RGB Image": os.path.basename(rgb_image_path),
        "NIR Image": os.path.basename(nir_image_path),
        "NDVI Image": output_image_name,
        "Mean NDVI": mean_ndvi,
        "Healthy (%)": (np.sum(healthy) / total_pixels) * 100,
        "Moderate (%)": (np.sum(moderate) / total_pixels) * 100,
        "Sparse (%)": (np.sum(sparse) / total_pixels) * 100,
        "Non-Vegetated (%)": (np.sum(barren) / total_pixels) * 100
    }

    # === Update CSV ===
    df_new = pd.DataFrame([stats])
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_csv(csv_path, index=False)

    # === Console Report ===
    print(f"\n📊 NDVI Analysis for {os.path.basename(rgb_image_path)} and {os.path.basename(nir_image_path)}:")
    print(f"Date and Time of Processing: {upload_datetime}")
    print(f"Mean NDVI: {mean_ndvi:.3f}")
    print(f"- Healthy Vegetation (>0.6): {stats['Healthy (%)']:.2f}%")
    print(f"- Moderate Vegetation (0.2–0.6): {stats['Moderate (%)']:.2f}%")
    print(f"- Sparse Vegetation (0–0.2): {stats['Sparse (%)']:.2f}%")
    print(f"- Non-Vegetated (<0): {stats['Non-Vegetated (%)']:.2f}%")
    print(f"✅ Saved NDVI image to: {output_image_path}")
    print(f"✅ Analysis results updated in: {csv_path}")

if __name__ == "__main__":
    compute_ndvi_from_images("RGB_Images\\Test_1_RGB.jpg", "NIR_Images\\Test_1_NIR.jpg")