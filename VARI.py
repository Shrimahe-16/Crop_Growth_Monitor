from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from datetime import datetime

# ========== Configuration ==========
output_folder = 'vari_outputs_date'
csv_path = 'vari_analysis_date.csv'

os.makedirs(output_folder, exist_ok=True)

def compute_vari_and_save(img_path='test2.jpg'):
    if not os.path.exists(img_path):
        print(f"❌ Error: Image '{img_path}' not found.")
        return

    # === Load RGB image ===
    rgb_img = Image.open(img_path).convert('RGB')
    rgb = np.asarray(rgb_img).astype(float)

    red = rgb[..., 0]
    green = rgb[..., 1]
    blue = rgb[..., 2]

    # === Compute VARI ===
    vari = (green - red) / (green + red - blue + 1e-5)

    # === Plot and Save Heatmap ===
    '''plt.figure(figsize=(8, 6))
    plt.imshow(vari, cmap='RdYlGn', vmin=-1, vmax=1)
    plt.colorbar(label='VARI')
    plt.title('VARI Heatmap')
    plt.axis('off')
    plt.show()'''

    # === Save Heatmap as Image ===
    vari_scaled = ((vari + 1) / 2 * 255).astype(np.uint8)
    vari_image = Image.fromarray(vari_scaled)
    output_image_name = f"vari_{os.path.splitext(os.path.basename(img_path))[0]}.png"
    output_image_path = os.path.join(output_folder, output_image_name)
    vari_image.save(output_image_path)

    # === Reload for Consistency ===
    vari_scaled = np.array(Image.open(output_image_path).convert('L')).astype(float)
    vari = (vari_scaled / 255.0) * 2 - 1

    # === Compute Statistics ===
    mean_vari = np.mean(vari)
    total_pixels = vari.size
    healthy = (vari > 0.5)
    moderate = (vari > 0.2) & (vari <= 0.5)
    sparse = (vari >= 0.0) & (vari <= 0.2)
    barren = (vari < 0.0)

    upload_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    stats = {
        "DateTime": upload_datetime,
        "Image Name": os.path.basename(img_path),
        "Mean VARI": mean_vari,
        "Healthy (%)": (np.sum(healthy) / total_pixels) * 100,
        "Moderate (%)": (np.sum(moderate) / total_pixels) * 100,
        "Sparse (%)": (np.sum(sparse) / total_pixels) * 100,
        "Non-Vegetated (%)": (np.sum(barren) / total_pixels) * 100
    }

    # === Save to CSV ===
    df_new = pd.DataFrame([stats])
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.to_csv(csv_path, index=False)

    # === Console Report ===
    print(f"\n📊 VARI Analysis for Image: {os.path.basename(img_path)}")
    print(f"Date and Time of Processing: {upload_datetime}")
    print(f"Mean VARI: {mean_vari:.3f}")
    print(f"- Healthy Vegetation (>0.5): {stats['Healthy (%)']:.2f}%")
    print(f"- Moderate Vegetation (0.2–0.5): {stats['Moderate (%)']:.2f}%")
    print(f"- Sparse Vegetation (0–0.2): {stats['Sparse (%)']:.2f}%")
    print(f"- Non-Vegetated (<0): {stats['Non-Vegetated (%)']:.2f}%")
    print(f"✅ VARI image saved to: {output_image_path}")
    print(f"✅ Analysis results updated in: {csv_path}")
pass

if __name__ == "__main__":
    compute_vari_and_save("RGB_Images\\Test_1_RGB.jpg")