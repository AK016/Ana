# Advanced 3D Integration of VRoid Models with Ana AI Assistant

This guide outlines the steps to directly integrate 3D VRoid Studio models with Ana AI Assistant, rendering them in real-time rather than using 2D assets.

## Prerequisites

- Ana AI Assistant codebase
- Python 3.x with PyQt5 installed
- VRoid Studio model exported in VRM format
- Basic understanding of 3D rendering concepts

## Required Python Libraries

```bash
pip install pygltflib numpy PyQt5 PyOpenGL pyvrm
```

## Step 1: Create a 3D Character Renderer

First, we need to create a PyQt5 widget that can render 3D models:

```python
# ana/ui/character_3d_view.py

import os
import numpy as np
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QMatrix4x4, QVector3D
from OpenGL.GL import *
import logging

logger = logging.getLogger('Ana.Character3DView')

class Character3DView(QOpenGLWidget):
    """
    3D Character visualization for Ana using VRM models
    """
    
    # Signals
    animation_complete = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        
        # Character state
        self.current_emotion = "neutral"  # neutral, happy, sad, surprised, thinking
        self.is_speaking = False
        self.is_listening = False
        self.energy_level = 0.8  # 0.0 to 1.0
        
        # 3D model properties
        self.model_path = None
        self.model = None
        self.rotation_y = 0.0
        
        # Animation parameters
        self.blend_shapes = {}  # VRM blend shapes/morph targets
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)  # ~60 fps
        
        # Load character model
        self.load_character_model()
        
        logger.info("3D Character view initialized")
    
    def load_character_model(self):
        """Load VRM character model"""
        try:
            # Look for VRM files in the assets directory
            assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'character')
            vrm_files = [f for f in os.listdir(assets_path) if f.endswith('.vrm')]
            
            if vrm_files:
                self.model_path = os.path.join(assets_path, vrm_files[0])
                logger.info(f"Found VRM model: {self.model_path}")
                # The actual loading will happen in initializeGL
            else:
                logger.warning("No VRM models found in assets directory")
        except Exception as e:
            logger.error(f"Error looking for VRM models: {str(e)}")
    
    def initializeGL(self):
        """Initialize OpenGL"""
        # Basic OpenGL setup
        glClearColor(0.1, 0.15, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Load VRM model if available
        if self.model_path:
            try:
                # This is a placeholder - in a real implementation, 
                # you would use a proper VRM loading library
                self.load_vrm_model(self.model_path)
            except Exception as e:
                logger.error(f"Error loading VRM model: {str(e)}")
    
    def load_vrm_model(self, model_path):
        """
        Load a VRM model for rendering
        This is a placeholder - implement with an actual VRM renderer
        """
        logger.info(f"Loading VRM model from: {model_path}")
        # In a real implementation, this would use a library like pyvrm
        # to load and parse the VRM file
        self.model = {"loaded": True, "path": model_path}
        
        # Initialize blend shapes/morph targets for facial expressions
        # VRM has standard blend shapes for expressions
        self.blend_shapes = {
            "neutral": 0.0,
            "happy": 0.0,
            "sad": 0.0,
            "angry": 0.0,
            "surprised": 0.0,
            "relaxed": 0.0,
            "aa": 0.0,  # mouth shapes for speaking
            "ih": 0.0,
            "ou": 0.0,
            "ee": 0.0,
            "oh": 0.0,
            "blink": 0.0
        }
    
    def resizeGL(self, width, height):
        """Handle resize events"""
        glViewport(0, 0, width, height)
    
    def paintGL(self):
        """Render the scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up camera/projection
        self.setup_camera()
        
        if self.model:
            # Render the VRM model
            self.render_character()
        else:
            # Render a placeholder if no model is loaded
            self.render_placeholder()
    
    def setup_camera(self):
        """Set up the camera and projection matrices"""
        # Create perspective projection
        aspect = self.width() / max(1, self.height())
        projection = QMatrix4x4()
        projection.perspective(45, aspect, 0.1, 100.0)
        
        # Create view matrix
        view = QMatrix4x4()
        view.lookAt(
            QVector3D(0, 1.6, 2.0),  # Camera position
            QVector3D(0, 1.4, 0),     # Look at point
            QVector3D(0, 1, 0)        # Up vector
        )
        
        # Set matrices for rendering
        # In a real implementation, you would set these in your shader program
        # This is just a placeholder
    
    def render_character(self):
        """Render the VRM character model"""
        # This is a placeholder for actual rendering code
        # In a real implementation, this would use OpenGL to render the VRM model
        
        # Apply model transformation
        model = QMatrix4x4()
        model.translate(0, 0, 0)
        model.rotate(self.rotation_y, 0, 1, 0)
        
        # Apply blend shapes/morph targets based on current state
        self.apply_blend_shapes()
        
        # Render the model (placeholder)
        logger.debug("Rendering character model")
    
    def apply_blend_shapes(self):
        """Apply blend shapes based on current emotion and state"""
        # Reset all blend shapes
        for shape in self.blend_shapes:
            self.blend_shapes[shape] = 0.0
        
        # Set blend shapes based on emotion
        if self.current_emotion == "happy":
            self.blend_shapes["happy"] = 1.0
        elif self.current_emotion == "sad":
            self.blend_shapes["sad"] = 1.0
        elif self.current_emotion == "surprised":
            self.blend_shapes["surprised"] = 1.0
        elif self.current_emotion == "thinking":
            self.blend_shapes["relaxed"] = 0.5
        else:  # neutral
            self.blend_shapes["neutral"] = 1.0
        
        # Handle blinking
        if hasattr(self, "eye_blink") and self.eye_blink:
            self.blend_shapes["blink"] = 1.0
        
        # Handle speaking
        if self.is_speaking:
            # Cycle through mouth shapes for speaking animation
            time_val = (self.animation_frame % 100) / 100.0
            
            if time_val < 0.2:
                self.blend_shapes["aa"] = 1.0
            elif time_val < 0.4:
                self.blend_shapes["ih"] = 1.0
            elif time_val < 0.6:
                self.blend_shapes["ou"] = 1.0
            elif time_val < 0.8:
                self.blend_shapes["ee"] = 1.0
            else:
                self.blend_shapes["oh"] = 1.0
    
    def render_placeholder(self):
        """Render a placeholder if no model is loaded"""
        # Draw a simple placeholder shape
        glBegin(GL_TRIANGLES)
        glColor3f(0.0, 0.8, 0.8)
        glVertex3f(-0.5, -0.5, 0)
        glVertex3f(0.5, -0.5, 0)
        glVertex3f(0, 0.5, 0)
        glEnd()
    
    def update_animation(self):
        """Update animation parameters for the next frame"""
        if not hasattr(self, "animation_frame"):
            self.animation_frame = 0
        
        self.animation_frame += 1
        self.rotation_y += 0.1 if self.is_listening else 0
        
        # Trigger occasional blink
        if self.animation_frame % 200 == 0:
            self.eye_blink = True
            QTimer.singleShot(150, self._stop_blink)
        
        # Update the view
        self.update()
    
    def _stop_blink(self):
        """Stop blinking"""
        self.eye_blink = False
    
    def set_emotion(self, emotion):
        """Set character emotion"""
        valid_emotions = ["neutral", "happy", "sad", "surprised", "thinking"]
        if emotion in valid_emotions:
            self.current_emotion = emotion
            logger.info(f"Character emotion set to: {emotion}")
        else:
            logger.warning(f"Invalid emotion: {emotion}")
    
    def on_listening(self, is_listening):
        """Handle listening state changes"""
        self.is_listening = is_listening
        if is_listening:
            self.set_emotion("surprised")
            logger.info("Listening started, animating character")
        else:
            self.set_emotion("neutral")
            logger.info("Listening stopped, returning to neutral")
    
    def on_speaking(self, text=None):
        """Handle speaking state changes"""
        self.is_speaking = True
        
        if text:
            # If we have text, estimate duration based on text length
            duration = max(1000, len(text) * 10)
            self.set_emotion("happy")
            
            # Create a timer to stop the speaking animation
            QTimer.singleShot(duration, self._stop_speaking)
            logger.info(f"Speaking started, animating for {duration}ms")
        else:
            # If no text, use a default duration
            QTimer.singleShot(1000, self._stop_speaking)
            logger.info("Speaking started with default duration")
    
    def _stop_speaking(self):
        """Stop speaking animation"""
        self.is_speaking = False
        self.animation_complete.emit()
        logger.info("Speaking animation stopped")
```

## Step 2: Modify Ana to Use the 3D Renderer

Edit Ana's main UI files to use the 3D character renderer:

```python
# ana/ui/main_window.py (or similar)

# Add import for the 3D character view
from ana.ui.character_3d_view import Character3DView

# Then, where the character view is initialized:
# Replace:
# self.character_view = CharacterView(self)
# With:
self.character_view = Character3DView(self)
```

## Step 3: Prepare a VRM Model

1. Create a character in VRoid Studio
2. Export as VRM format with optimized settings
3. Place the VRM file in the `ana/assets/character/` directory
4. Rename it to `character.vrm` for consistent loading

## Step 4: Adding VRM Blend Shape Support

VRM models have standardized blend shapes (morph targets) for facial expressions. To fully utilize these:

```python
# Add to character_3d_view.py

def map_emotion_to_vrm_blendshapes(self, emotion):
    """Map Ana emotions to VRM standard blend shapes"""
    # Reset all blend shapes
    for key in self.blend_shapes:
        self.blend_shapes[key] = 0.0
    
    # Standard VRM blend shapes
    if emotion == "neutral":
        # Neutral has no specific blend shape, just reset all
        pass
    elif emotion == "happy":
        self.blend_shapes["joy"] = 1.0
    elif emotion == "sad":
        self.blend_shapes["sorrow"] = 1.0
    elif emotion == "angry":
        self.blend_shapes["angry"] = 1.0
    elif emotion == "surprised":
        self.blend_shapes["surprised"] = 1.0
    elif emotion == "thinking":
        # Combination for "thinking" look
        self.blend_shapes["lookUp"] = 0.5
        self.blend_shapes["blink_L"] = 0.3
```

## Step 5: Adding Lip Sync for Realistic Speaking

For more realistic speaking animations, add lip sync support:

```python
# Add to character_3d_view.py

def apply_lip_sync(self, text):
    """Apply simple lip sync based on text phonemes"""
    if not text or not self.is_speaking:
        return
    
    # Very basic lip sync - in a real implementation,
    # you'd use a proper text-to-phoneme system
    
    # Get the current position in the text based on time
    text_length = len(text)
    progress = min(1.0, (self.animation_frame * 16) / (text_length * 50))
    current_pos = int(progress * text_length)
    
    if current_pos >= text_length:
        return
    
    # Get current character and map to mouth shape
    current_char = text[current_pos].lower()
    
    # Map characters to mouth shapes
    if current_char in 'aeiou':
        self.blend_shapes["a"] = 1.0 if current_char == 'a' else 0.0
        self.blend_shapes["i"] = 1.0 if current_char == 'i' else 0.0
        self.blend_shapes["u"] = 1.0 if current_char == 'u' else 0.0
        self.blend_shapes["e"] = 1.0 if current_char == 'e' else 0.0
        self.blend_shapes["o"] = 1.0 if current_char == 'o' else 0.0
    else:
        # Consonants - can use different mouth shapes based on consonant groups
        # This is a simplified example
        if current_char in 'pbm':
            self.blend_shapes["p"] = 0.8
        elif current_char in 'fv':
            self.blend_shapes["f"] = 0.8
        elif current_char in 'td':
            self.blend_shapes["t"] = 0.8
        else:
            # Default to neutral mouth
            pass
```

## Step 6: Adding Cyberpunk Lighting Effects

To maintain Ana's cyberpunk aesthetic with 3D models:

```python
# Add to character_3d_view.py

def setup_cyberpunk_lighting(self):
    """Set up cyberpunk-style lighting for the character"""
    # Define teal/cyan light (from left side)
    teal_light_pos = [-2.0, 1.0, 2.0, 1.0]
    teal_light_color = [0.0, 0.8, 0.8, 1.0]
    
    # Define pink/magenta light (from right side)
    pink_light_pos = [2.0, 1.0, 2.0, 1.0]
    pink_light_color = [0.8, 0.2, 0.4, 1.0]
    
    # Define ambient light (dark blue)
    ambient_light_color = [0.05, 0.05, 0.1, 1.0]
    
    # Set up lighting in OpenGL
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    
    # Set ambient light
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient_light_color)
    
    # Set up teal light
    glLightfv(GL_LIGHT0, GL_POSITION, teal_light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, teal_light_color)
    
    # Set up pink light
    glLightfv(GL_LIGHT1, GL_POSITION, pink_light_pos)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, pink_light_color)
```

## Step 7: Handling Different VRM Models

To support different VRM models without code changes:

```python
# Add to character_3d_view.py

def detect_and_load_vrm_model(self):
    """Detect and load available VRM models"""
    assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'character')
    
    # Look for VRM files
    vrm_files = [f for f in os.listdir(assets_path) if f.endswith('.vrm')]
    
    if not vrm_files:
        logger.warning("No VRM models found in assets directory")
        return False
    
    # Prioritize character.vrm if it exists, otherwise use the first one
    if "character.vrm" in vrm_files:
        self.model_path = os.path.join(assets_path, "character.vrm")
    else:
        self.model_path = os.path.join(assets_path, vrm_files[0])
    
    logger.info(f"Selected VRM model: {os.path.basename(self.model_path)}")
    return True
```

## Advanced Features

### Real-time Weather Effects

```python
# Add to character_3d_view.py

def add_weather_effects(self, weather_type):
    """Add weather-based effects to the 3D scene"""
    self.weather_type = weather_type
    
    if weather_type == "rain":
        # Setup rain particle system
        self.setup_particles("rain", 1000, [0.7, 0.7, 1.0, 0.5])
    elif weather_type == "snow":
        # Setup snow particle system
        self.setup_particles("snow", 500, [1.0, 1.0, 1.0, 0.7])
    elif weather_type == "thunderstorm":
        # Setup lightning effects
        self.setup_lightning_effect()
    else:
        # Clear weather effects
        self.clear_weather_effects()

def setup_particles(self, particle_type, count, color):
    """Set up weather particle systems"""
    # Initialize particle arrays
    self.particles = []
    for i in range(count):
        # Create particle with random position and velocity
        particle = {
            "pos": [
                np.random.uniform(-3.0, 3.0),
                np.random.uniform(1.0, 4.0),
                np.random.uniform(-3.0, 3.0)
            ],
            "vel": [
                np.random.uniform(-0.01, 0.01),
                np.random.uniform(-0.1, -0.05) if particle_type == "rain" else np.random.uniform(-0.02, -0.01),
                np.random.uniform(-0.01, 0.01)
            ],
            "size": np.random.uniform(0.01, 0.03) if particle_type == "rain" else np.random.uniform(0.02, 0.05),
            "color": color
        }
        self.particles.append(particle)
```

### Advanced Camera Controls

```python
# Add to character_3d_view.py

def setup_camera_animation(self):
    """Set up camera animations for different states"""
    # Camera properties
    self.camera_pos = QVector3D(0, 1.6, 2.0)
    self.camera_target = QVector3D(0, 1.4, 0)
    self.camera_up = QVector3D(0, 1, 0)
    
    # Camera animation settings
    self.camera_animation_enabled = True
    self.camera_animation_speed = 0.01
    self.camera_animation_radius = 0.2
    self.camera_animation_phase = 0.0

def update_camera_animation(self):
    """Update camera position for subtle animation"""
    if not self.camera_animation_enabled:
        return
    
    # Update animation phase
    self.camera_animation_phase += self.camera_animation_speed
    
    # Calculate new camera position with subtle circular motion
    offset_x = np.sin(self.camera_animation_phase) * self.camera_animation_radius
    offset_z = np.cos(self.camera_animation_phase) * self.camera_animation_radius
    
    # Apply offsets to base camera position
    animated_pos = QVector3D(
        self.camera_pos.x() + offset_x,
        self.camera_pos.y(),
        self.camera_pos.z() + offset_z
    )
    
    # Update view matrix with animated camera
    view = QMatrix4x4()
    view.lookAt(animated_pos, self.camera_target, self.camera_up)
    
    # Apply view matrix for rendering
    # (In actual implementation, this would be applied to shaders)
```

## Compatibility Considerations

1. **Performance**: 3D rendering is more resource-intensive than 2D. Consider adding a fallback to 2D mode for less powerful systems.

2. **Asset Size**: VRM models can be large. Implement a model optimization step to reduce file size for distribution.

3. **Animation Quality**: For best results, make sure your VRM model has properly defined blend shapes for all required expressions.

## Troubleshooting

- **Model Not Appearing**: Check file paths and ensure the VRM file is valid. Try viewing it in a VRM viewer first.
- **Missing Facial Expressions**: Ensure your VRM model has the standard VRM blend shapes defined.
- **Performance Issues**: Reduce model complexity, texture sizes, or implement level-of-detail rendering.
- **Lighting Problems**: Adjust the cyberpunk lighting parameters to work well with your specific model.

## Resources

- [PyOpenGL Documentation](http://pyopengl.sourceforge.net/)
- [VRM Format Specification](https://vrm.dev/en/vrm_spec/)
- [VRoid Studio Documentation](https://vroid.com/en/studio/docs/)
- [Qt 3D Documentation](https://doc.qt.io/qt-5/qt3d-index.html) 