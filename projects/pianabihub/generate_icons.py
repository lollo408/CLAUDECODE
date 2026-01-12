"""
Generate PWA icons for Piana BI Hub
Creates 192x192 and 512x512 PNG icons with brand colors
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """Create a square icon with brand colors and text"""
    # Create image with purple background
    img = Image.new('RGB', (size, size), color='#7c3aed')
    draw = ImageDraw.Draw(img)

    # Draw white circle in center (80% of size)
    circle_size = int(size * 0.8)
    circle_margin = (size - circle_size) // 2
    draw.ellipse(
        [circle_margin, circle_margin, size - circle_margin, size - circle_margin],
        fill='#ffffff'
    )

    # Draw purple "PBI" text in center
    try:
        # Try to use a nice font if available
        font_size = int(size * 0.25)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    text = "PBI"
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2

    draw.text((text_x, text_y), text, fill='#7c3aed', font=font)

    # Save the image
    img.save(output_path, 'PNG')
    print(f"Created {output_path} ({size}x{size})")

if __name__ == '__main__':
    icons_dir = os.path.join(os.path.dirname(__file__), 'static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    # Generate both icon sizes
    create_icon(192, os.path.join(icons_dir, 'icon-192.png'))
    create_icon(512, os.path.join(icons_dir, 'icon-512.png'))

    print("\n✅ PWA icons generated successfully!")
