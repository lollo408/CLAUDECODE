"""
Generate PWA icons for Piana BI Hub using the Piana Technology logo
Creates 192x192 and 512x512 PNG icons with white background
"""

from PIL import Image
import os

def create_icon_with_logo(size, logo_path, output_path):
    """Create a square icon with white background and centered logo"""
    # Create white background
    icon = Image.new('RGB', (size, size), color='#FFFFFF')

    # Open and resize logo
    logo = Image.open(logo_path)

    # Calculate logo size (80% of icon size to add padding)
    logo_size = int(size * 0.75)

    # Resize logo maintaining aspect ratio
    logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

    # Calculate position to center logo
    logo_x = (size - logo.width) // 2
    logo_y = (size - logo.height) // 2

    # Paste logo (handle transparency if present)
    if logo.mode == 'RGBA':
        icon.paste(logo, (logo_x, logo_y), logo)
    else:
        icon.paste(logo, (logo_x, logo_y))

    # Save the image
    icon.save(output_path, 'PNG')
    print(f"Created {output_path} ({size}x{size})")

if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    logo_path = os.path.join(script_dir, 'static', 'piana_logo.png')
    icons_dir = os.path.join(script_dir, 'static', 'icons')

    os.makedirs(icons_dir, exist_ok=True)

    # Generate both icon sizes
    create_icon_with_logo(192, logo_path, os.path.join(icons_dir, 'icon-192.png'))
    create_icon_with_logo(512, logo_path, os.path.join(icons_dir, 'icon-512.png'))

    print("\nPWA icons generated successfully with Piana logo on white background!")
