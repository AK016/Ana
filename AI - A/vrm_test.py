#!/usr/bin/env python3
# VRM Test - Create placeholder assets for testing VRoid integration with Ana

import os
import sys
import time
import argparse
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Create placeholder assets for testing VRoid integration')
    parser.add_argument('--output', '-o', default='ana/assets/character_test', 
                        help='Output directory for character assets (default: ana/assets/character_test)')
    parser.add_argument('--name', '-n', default='VRoid Test',
                        help='Name to display on the placeholder assets')
    return parser.parse_args()

def create_test_assets(output_dir, name):
    """Create test character assets"""
    print(f"Creating test character assets in: {output_dir}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create basic character assets
    try:
        # Base face - create a circular face with cyberpunk styling
        base = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
        draw = ImageDraw.Draw(base)
        
        # Draw face shape
        draw.ellipse((100, 50, 300, 300), fill=(255, 240, 235))
        
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("Arial", 20)
        except IOError:
            font = ImageFont.load_default()
        
        # Add text label
        draw.text((150, 320), f"VRoid: {name}", fill=(0, 220, 200), font=font)
        
        # Add cyberpunk elements
        draw.line((50, 150, 100, 150), fill=(0, 220, 200), width=2)
        draw.line((300, 150, 350, 150), fill=(220, 50, 100), width=2)
        
        # Save base face
        base_path = os.path.join(output_dir, 'base.png')
        base.save(base_path)
        print(f"Created base.png")
        
        # Hair layer
        hair = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
        draw = ImageDraw.Draw(hair)
        
        # Draw simple hair shape
        points = [(150, 50), (250, 50), (300, 150), (350, 200), 
                  (300, 300), (200, 350), (100, 300), (50, 200), (100, 150)]
        draw.polygon(points, fill=(20, 25, 30, 200))
        
        # Add highlights
        draw.line((130, 100, 140, 300), fill=(0, 220, 200, 120), width=3)
        draw.line((270, 100, 260, 300), fill=(220, 50, 100, 120), width=3)
        
        # Save hair
        hair_path = os.path.join(output_dir, 'hair.png')
        hair.save(hair_path)
        print(f"Created hair.png")
        
        # Eyes
        eye_states = ['neutral', 'happy', 'sad', 'surprised', 'thinking', 'blink']
        for state in eye_states:
            eyes = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
            draw = ImageDraw.Draw(eyes)
            
            # Different eye shapes based on state
            if state == 'blink':
                # Closed eyes
                draw.line((150, 180, 180, 180), fill=(40, 40, 50), width=2)
                draw.line((220, 180, 250, 180), fill=(40, 40, 50), width=2)
            elif state == 'happy':
                # Happy eyes - curved upward
                draw.ellipse((150, 170, 180, 190), fill=(245, 245, 250), outline=(40, 40, 50), width=1)
                draw.ellipse((220, 170, 250, 190), fill=(245, 245, 250), outline=(40, 40, 50), width=1)
                # Irises
                draw.ellipse((160, 175, 170, 185), fill=(20, 180, 220))
                draw.ellipse((230, 175, 240, 185), fill=(20, 180, 220))
            elif state == 'sad':
                # Sad eyes - droopy
                draw.ellipse((150, 175, 180, 190), fill=(245, 245, 250), outline=(40, 40, 50), width=1)
                draw.ellipse((220, 175, 250, 190), fill=(245, 245, 250), outline=(40, 40, 50), width=1)
                # Irises
                draw.ellipse((160, 178, 170, 188), fill=(20, 180, 220))
                draw.ellipse((230, 178, 240, 188), fill=(20, 180, 220))
            elif state == 'surprised':
                # Surprised eyes - wide
                draw.ellipse((145, 170, 185, 195), fill=(245, 245, 250), outline=(40, 40, 50), width=1)
                draw.ellipse((215, 170, 255, 195), fill=(245, 245, 250), outline=(40, 40, 50), width=1)
                # Irises
                draw.ellipse((160, 178, 170, 188), fill=(20, 180, 220))
                draw.ellipse((230, 178, 240, 188), fill=(20, 180, 220))
            else:
                # Neutral eyes
                draw.ellipse((150, 170, 180, 190), fill=(245, 245, 250), outline=(40, 40, 50), width=1)
                draw.ellipse((220, 170, 250, 190), fill=(245, 245, 250), outline=(40, 40, 50), width=1)
                # Irises
                draw.ellipse((160, 175, 170, 185), fill=(20, 180, 220))
                draw.ellipse((230, 175, 240, 185), fill=(20, 180, 220))
            
            # Save eyes
            eyes_path = os.path.join(output_dir, f'eyes_{state}.png')
            eyes.save(eyes_path)
            print(f"Created eyes_{state}.png")
        
        # Mouth
        mouth_states = ['neutral', 'happy', 'sad', 'surprised', 'thinking', 'speak1', 'speak2', 'speak3']
        for state in mouth_states:
            mouth = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
            draw = ImageDraw.Draw(mouth)
            
            # Different mouth shapes based on state
            if state == 'happy':
                # Happy mouth - curved upward
                draw.arc((180, 230, 220, 250), 0, 180, fill=(40, 30, 35), width=2)
            elif state == 'sad':
                # Sad mouth - curved downward
                draw.arc((180, 240, 220, 260), 180, 360, fill=(40, 30, 35), width=2)
            elif state == 'surprised' or state.startswith('speak'):
                # Open mouth
                size = 10 if state == 'surprised' else 5 + int(state[-1]) * 3
                draw.ellipse((190, 240, 210, 240 + size), fill=(150, 60, 80), outline=(40, 30, 35), width=1)
            else:
                # Neutral/thinking mouth
                draw.line((185, 240, 215, 240), fill=(40, 30, 35), width=2)
            
            # Save mouth
            mouth_path = os.path.join(output_dir, f'mouth_{state}.png')
            mouth.save(mouth_path)
            print(f"Created mouth_{state}.png")
        
        # Eyebrows
        eyebrow_states = ['neutral', 'happy', 'sad', 'surprised', 'thinking']
        for state in eyebrow_states:
            eyebrows = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
            draw = ImageDraw.Draw(eyebrows)
            
            # Different eyebrow shapes based on state
            if state == 'happy':
                # Happy eyebrows - slightly raised
                draw.line((145, 155, 185, 150), fill=(20, 25, 30), width=3)
                draw.line((215, 150, 255, 155), fill=(20, 25, 30), width=3)
            elif state == 'sad':
                # Sad eyebrows - inner points down
                draw.line((145, 150, 185, 160), fill=(20, 25, 30), width=3)
                draw.line((215, 160, 255, 150), fill=(20, 25, 30), width=3)
            elif state == 'surprised':
                # Surprised eyebrows - raised
                draw.line((145, 145, 185, 145), fill=(20, 25, 30), width=3)
                draw.line((215, 145, 255, 145), fill=(20, 25, 30), width=3)
            elif state == 'thinking':
                # Thinking eyebrows - one raised
                draw.line((145, 150, 185, 150), fill=(20, 25, 30), width=3)
                draw.line((215, 145, 255, 155), fill=(20, 25, 30), width=3)
            else:
                # Neutral eyebrows
                draw.line((145, 150, 185, 150), fill=(20, 25, 30), width=3)
                draw.line((215, 150, 255, 150), fill=(20, 25, 30), width=3)
            
            # Save eyebrows
            eyebrows_path = os.path.join(output_dir, f'eyebrows_{state}.png')
            eyebrows.save(eyebrows_path)
            print(f"Created eyebrows_{state}.png")
        
        # Create a README with instructions
        readme_path = os.path.join(output_dir, 'README.md')
        with open(readme_path, 'w') as f:
            f.write("# VRoid Test Character Assets for Ana\n\n")
            f.write("These are test assets to simulate VRoid integration.\n\n")
            f.write("## Usage\n\n")
            f.write("1. Modify ana/ui/character_view.py to load assets from this directory\n")
            f.write("2. Launch Ana to see the test character\n")
            f.write("3. Replace with actual VRoid assets when ready\n")
        
        print(f"Created README.md with instructions")
        return True
        
    except Exception as e:
        print(f"Error creating test assets: {str(e)}")
        return False

def main():
    """Main function"""
    args = parse_arguments()
    
    # Create test assets
    if create_test_assets(args.output, args.name):
        print(f"\nSuccessfully created test character assets in: {args.output}")
        print("\nTo use these assets with Ana:")
        print("1. Run Ana with the following command:")
        print("   python3 -m ana.main --character-path character_test")
        print("   (Assuming Ana has a command line option for character path)")
        print("\n2. Or modify ana/ui/character_view.py to load assets from:")
        print(f"   {args.output}")
        return 0
    
    print("Failed to create test character assets")
    return 1

if __name__ == "__main__":
    sys.exit(main()) 