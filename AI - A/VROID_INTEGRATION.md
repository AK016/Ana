# Integrating VRoid Studio Characters with Ana AI Assistant

This guide will walk you through the process of integrating a custom female character created in VRoid Studio with the Ana AI Assistant.

## Prerequisites

- [VRoid Studio](https://vroid.com/en/studio) installed on your computer (available for Windows and macOS)
- Ana AI Assistant codebase
- Python 3.x with PyQt5 installed

## Step 1: Create Your Character in VRoid Studio

1. Download and install VRoid Studio from [the official website](https://vroid.com/en/studio)
2. Launch VRoid Studio and create a new project
3. Design your female character:
   - Customize facial features, hair, and clothing
   - Focus on creating a character that matches Ana's aesthetic (cyberpunk style with subtle dual-colored lighting)
   - Consider adding cyan/teal highlights on one side and pink/magenta on the other for the cyberpunk effect
   - Keep the character's appearance professional and suitable for an AI assistant

## Step 2: Export Your Character from VRoid Studio

1. In VRoid Studio, click on the "Export" button
2. Select "VRM" as the export format
   - VRM is a standard 3D avatar format optimized for real-time applications
3. Configure export settings:
   - Set texture resolution to a reasonable size (1024x1024 or 2048x2048)
   - Enable "Reduce file size" option if available
4. Save the VRM file to your computer

## Step 3: Prepare the Character for Ana

Ana currently uses 2D PNG assets for character visualization, so we need to render the 3D VRM model into 2D assets:

### Option A: Manual Screenshot Method (Simple)

1. Open the VRM file in VRoid Studio or a VRM viewer
2. Position the camera to capture front-facing views of your character in different expressions
3. Take screenshots for each required state:
   - Neutral expression
   - Speaking expression
   - Listening expression
   - Thinking expression
4. Edit the screenshots in an image editor to:
   - Remove the background (make it transparent)
   - Crop to focus on the face/upper body
   - Resize to 400x400 pixels
   - Save as PNG files with appropriate names (e.g., `base.png`, `eyes_neutral.png`, etc.)

### Option B: Automated Rendering (Advanced)

For a more professional integration, we can create a small Python script that renders the VRM model in different poses:

1. Install required libraries:
   ```bash
   pip install pygltflib pillow numpy
   ```

2. Create a Python script that:
   - Loads the VRM model
   - Sets up different expressions (using VRM's blend shape system)
   - Renders each expression to a separate PNG image
   - Saves the images in the required format for Ana

## Step 4: Replace Ana's Character Assets

1. Locate Ana's character assets folder:
   ```
   ana/assets/character/
   ```

2. Back up the original assets:
   ```bash
   cp -r ana/assets/character/ ana/assets/character_backup/
   ```

3. Replace the assets with your VRoid-derived images:
   - `base.png` - Main face/head image
   - `hair.png` - Hair layer
   - `eyes_*.png` - Eye expressions (neutral, happy, sad, surprised, thinking, blink)
   - `mouth_*.png` - Mouth expressions (neutral, happy, sad, surprised, thinking, speak1, speak2, speak3)
   - `eyebrows_*.png` - Eyebrow expressions (neutral, happy, sad, surprised, thinking)
   - Any effect images you want to keep from the original assets

## Step 5: Adjust the Character View Code (Optional)

If your character has different proportions or requires specific adjustments:

1. Open `ana/ui/character_view.py`
2. Modify the rendering parameters in methods like:
   - `_paint_face`
   - `_paint_realistic_eyes`
   - `_paint_realistic_mouth`
   - Adjust colors, positions, and sizes to match your character

## Step 6: Test Your Integration

1. Launch Ana:
   ```bash
   python3 -m ana.main
   ```

2. Observe your new character and make any necessary adjustments
3. Test different states (speaking, listening) to ensure all expressions work correctly

## Advanced Integration: Using 3D Models Directly (Future Enhancement)

For a future enhancement, you could modify Ana to render the VRM model directly in 3D:

1. Use a Python VRM/glTF library to load the model
2. Create a QT3D or OpenGL-based renderer in PyQt5
3. Replace the existing 2D character view with a 3D one
4. Use VRM's blend shape system to animate facial expressions

## Troubleshooting

- If images appear with incorrect transparency, check that your PNG files have proper alpha channels
- If the character appears too large or small, adjust the image sizes or modify the rendering code
- If facial expressions don't look right, try recreating them with different expressions in VRoid Studio

## Resources

- [VRoid Studio Documentation](https://vroid.com/en/studio)
- [VRM Format Documentation](https://vrm.dev/en/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/) 