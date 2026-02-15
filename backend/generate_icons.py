from PIL import Image, ImageDraw

def create_icon(size, filename, color=(59, 130, 246)):
    # Create image with background
    img = Image.new('RGB', (size, size), color=color)
    draw = ImageDraw.Draw(img)
    
    # Draw a simple white checkmark to represent 'Pickr'
    # Coordinates for a checkmark
    padding = size // 4
    points = [
        (padding, size // 2),
        (size // 2, size - padding),
        (size - padding, padding)
    ]
    draw.line(points, fill='white', width=size // 10)
    
    img.save(filename)
    print(f"Created {filename}")

import os
public_dir = r"d:\code\GitHub\Personal\Pickr\frontend\public"
if not os.path.exists(public_dir):
    os.makedirs(public_dir)

create_icon(192, os.path.join(public_dir, "pwa-192x192.png"))
create_icon(512, os.path.join(public_dir, "pwa-512x512.png"))
create_icon(180, os.path.join(public_dir, "apple-touch-icon.png"))
create_icon(32, os.path.join(public_dir, "favicon.ico"), color=(255, 255, 255))
