#!/usr/bin/env python3
# VRM to Ana - Extract images from VRM models for Ana AI Assistant
# This script helps convert VRoid Studio models to Ana-compatible assets

import os
import sys
import time
import argparse
import json
import base64
from PIL import Image
import io
import numpy as np
from pathlib import Path

try:
    from pygltflib import GLTF2
except ImportError:
    print("Error: Required package 'pygltflib' not installed.")
    print("Please install it using: pip install pygltflib")
    sys.exit(1)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Convert VRM files to Ana character assets')
    parser.add_argument('vrm_file', help='Path to the VRM file')
    parser.add_argument('--output', '-o', default='ana/assets/character', 
                        help='Output directory for character assets (default: ana/assets/character)')
    parser.add_argument('--backup', '-b', action='store_true',
                        help='Backup existing character assets before replacing')
    return parser.parse_args()

def extract_vrm_textures(vrm_file, output_dir):
    """Extract textures from a VRM file"""
    print(f"Loading VRM file: {vrm_file}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the VRM file
    gltf = GLTF2().load(vrm_file)
    
    # Extract VRM metadata
    vrm_metadata = None
    for extension in gltf.extensions.values():
        if isinstance(extension, dict) and "VRM" in extension:
            vrm_metadata = extension["VRM"]
            break
    
    if vrm_metadata:
        # Print basic info about the model
        print(f"VRM Model: {vrm_metadata.get('meta', {}).get('title', 'Unknown')}")
        print(f"Author: {vrm_metadata.get('meta', {}).get('author', 'Unknown')}")
    
    # Extract textures
    print("Extracting textures...")
    extracted_textures = []
    
    for i, image in enumerate(gltf.images):
        # Handle different ways textures can be stored
        if hasattr(image, 'uri') and image.uri:
            if image.uri.startswith('data:image'):
                # Extract base64 encoded image
                mime_type, b64data = image.uri.split(',', 1)
                image_data = base64.b64decode(b64data)
                img = Image.open(io.BytesIO(image_data))
                
                # Save image
                texture_name = f"texture_{i}.png"
                texture_path = os.path.join(output_dir, texture_name)
                img.save(texture_path)
                extracted_textures.append((texture_path, img.size))
                
            elif os.path.exists(os.path.join(os.path.dirname(vrm_file), image.uri)):
                # Copy external image
                src_path = os.path.join(os.path.dirname(vrm_file), image.uri)
                texture_name = f"texture_{i}.png"
                texture_path = os.path.join(output_dir, texture_name)
                
                img = Image.open(src_path)
                img.save(texture_path)
                extracted_textures.append((texture_path, img.size))
        
        elif hasattr(gltf, 'bufferViews') and hasattr(image, 'bufferView') and image.bufferView is not None:
            # Extract from buffer view
            buffer_view = gltf.bufferViews[image.bufferView]
            buffer = gltf.buffers[buffer_view.buffer]
            
            # Handle buffer data
            if hasattr(buffer, 'uri') and buffer.uri and buffer.uri.startswith('data:application/octet-stream;base64,'):
                buffer_data = base64.b64decode(buffer.uri.split(',', 1)[1])
                
                # Extract image data from buffer
                start = buffer_view.byteOffset
                end = start + buffer_view.byteLength
                image_data = buffer_data[start:end]
                
                # Save image
                img = Image.open(io.BytesIO(image_data))
                texture_name = f"texture_{i}.png"
                texture_path = os.path.join(output_dir, texture_name)
                img.save(texture_path)
                extracted_textures.append((texture_path, img.size))
    
    print(f"Extracted {len(extracted_textures)} textures")
    return extracted_textures

def create_ana_assets(textures, output_dir):
    """Create Ana-compatible character assets from VRM textures"""
    print("Creating Ana character assets...")
    
    # Find the main face/head texture (usually the largest texture or a specific one)
    main_texture = None
    largest_size = 0
    
    for texture_path, size in textures:
        area = size[0] * size[1]
        if area > largest_size:
            largest_size = area
            main_texture = texture_path
    
    if not main_texture:
        print("Error: Could not find a suitable main texture")
        return False
    
    # Create basic character assets
    try:
        # Base face
        main_img = Image.open(main_texture)
        base_path = os.path.join(output_dir, 'base.png')
        main_img.save(base_path)
        print(f"Created base.png")
        
        # Create placeholder assets for required parts
        # In a real implementation, you would extract these from the VRM model
        # or use AI to generate appropriate facial parts
        
        # Eyes
        eye_states = ['neutral', 'happy', 'sad', 'surprised', 'thinking', 'blink']
        for state in eye_states:
            # Create a placeholder eye image
            eyes_img = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
            eyes_path = os.path.join(output_dir, f'eyes_{state}.png')
            eyes_img.save(eyes_path)
            print(f"Created placeholder for eyes_{state}.png")
        
        # Mouth
        mouth_states = ['neutral', 'happy', 'sad', 'surprised', 'thinking', 'speak1', 'speak2', 'speak3']
        for state in mouth_states:
            # Create a placeholder mouth image
            mouth_img = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
            mouth_path = os.path.join(output_dir, f'mouth_{state}.png')
            mouth_img.save(mouth_path)
            print(f"Created placeholder for mouth_{state}.png")
        
        # Eyebrows
        eyebrow_states = ['neutral', 'happy', 'sad', 'surprised', 'thinking']
        for state in eyebrow_states:
            # Create a placeholder eyebrow image
            eyebrow_img = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
            eyebrow_path = os.path.join(output_dir, f'eyebrows_{state}.png')
            eyebrow_img.save(eyebrow_path)
            print(f"Created placeholder for eyebrows_{state}.png")
        
        # Hair - use the main texture for now
        hair_path = os.path.join(output_dir, 'hair.png')
        main_img.save(hair_path)
        print(f"Created hair.png (placeholder)")
        
        # Create a README with instructions
        readme_path = os.path.join(output_dir, 'README.md')
        with open(readme_path, 'w') as f:
            f.write("# VRoid Character Assets for Ana\n\n")
            f.write("These assets were generated from a VRoid Studio model.\n\n")
            f.write("## Notes\n\n")
            f.write("- The placeholder assets (eyes, mouth, eyebrows) need to be customized manually.\n")
            f.write("- Extract the facial features from the main texture and create proper transparent PNGs.\n")
            f.write("- Make sure all assets are 400x400 pixels with transparent backgrounds.\n")
        
        print(f"Created README.md with instructions")
        return True
        
    except Exception as e:
        print(f"Error creating Ana assets: {str(e)}")
        return False

def backup_existing_assets(output_dir):
    """Backup existing character assets"""
    if not os.path.exists(output_dir):
        return True
        
    backup_dir = f"{output_dir}_backup_{int(time.time())}"
    try:
        import shutil
        import time
        
        # Create backup
        shutil.copytree(output_dir, backup_dir)
        print(f"Backed up existing assets to: {backup_dir}")
        return True
    except Exception as e:
        print(f"Error backing up assets: {str(e)}")
        return False

def main():
    """Main function"""
    args = parse_arguments()
    
    # Check if VRM file exists
    if not os.path.exists(args.vrm_file):
        print(f"Error: VRM file not found: {args.vrm_file}")
        return 1
    
    # Backup existing assets if requested
    if args.backup and os.path.exists(args.output):
        if not backup_existing_assets(args.output):
            print("Failed to backup existing assets. Aborting.")
            return 1
    
    # Extract textures
    textures = extract_vrm_textures(args.vrm_file, args.output)
    
    # Create Ana assets
    if textures:
        if create_ana_assets(textures, args.output):
            print(f"\nSuccessfully created Ana character assets in: {args.output}")
            print("\nNext steps:")
            print("1. Edit the placeholder assets to create proper facial features")
            print("2. Start Ana to see your new character")
            print("3. Adjust character_view.py if needed for better integration")
            return 0
    
    print("Failed to create Ana character assets")
    return 1

if __name__ == "__main__":
    sys.exit(main()) 