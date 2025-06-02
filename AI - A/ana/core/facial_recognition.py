#!/usr/bin/env python3
# Ana AI Assistant - Facial Recognition Module

import os
import cv2
import time
import logging
import threading
import numpy as np
from typing import Callable, Dict, Any, Optional

logger = logging.getLogger('Ana.FacialRecognition')

class FacialRecognition:
    """Facial recognition module for Ana AI Assistant"""
    
    def __init__(self, settings):
        """Initialize facial recognition with settings"""
        self.settings = settings
        self.running = False
        self.camera_index = 0  # Default camera index
        self.detection_interval = 0.1  # Seconds between detections
        self.emotion_interval = 1.0  # Seconds between emotion detections
        
        # Callback functions
        self.on_face_detected = None
        self.on_face_lost = None
        self.on_emotion_detected = None
        
        # State variables
        self.face_detected = False
        self.last_emotion_time = 0
        self.current_emotion = "neutral"
        
        # Load models
        self._load_models()
        
        logger.info("Facial recognition initialized")
    
    def _load_models(self):
        """Load face detection and emotion recognition models"""
        try:
            # Load face detection model (OpenCV's Haar Cascade)
            model_path = os.path.join(
                os.path.dirname(__file__), 
                "..", "assets", "models", "haarcascade_frontalface_default.xml"
            )
            
            # If model doesn't exist, try to get it from OpenCV's installation
            if not os.path.exists(model_path):
                cv2_path = os.path.dirname(cv2.__file__)
                model_path = os.path.join(cv2_path, "data", "haarcascade_frontalface_default.xml")
            
            self.face_cascade = cv2.CascadeClassifier(model_path)
            if self.face_cascade.empty():
                logger.error("Could not load face detection model")
                raise Exception("Face detection model not found")
                
            logger.info("Face detection model loaded")
            
            # For emotion recognition, we would normally load a more sophisticated model
            # For simplicity, we'll use a basic approach here
            self.emotion_detection_available = False
            
            # Try to load a more advanced face detection model (DNN based)
            try:
                # These paths would point to your model files
                prototxt_path = os.path.join(
                    os.path.dirname(__file__), 
                    "..", "assets", "models", "deploy.prototxt"
                )
                model_path = os.path.join(
                    os.path.dirname(__file__), 
                    "..", "assets", "models", "res10_300x300_ssd_iter_140000.caffemodel"
                )
                
                if os.path.exists(prototxt_path) and os.path.exists(model_path):
                    self.face_net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
                    self.advanced_face_detection = True
                    logger.info("Advanced face detection model loaded")
                else:
                    self.advanced_face_detection = False
            except:
                self.advanced_face_detection = False
        
        except Exception as e:
            logger.error(f"Error loading facial recognition models: {str(e)}")
            self.face_cascade = None
    
    def start(self):
        """Start facial recognition in a separate thread"""
        if self.face_cascade is None:
            logger.error("Cannot start facial recognition: models not loaded")
            return False
            
        self.running = True
        threading.Thread(target=self._recognition_loop, daemon=True).start()
        logger.info("Facial recognition started")
        return True
    
    def stop(self):
        """Stop facial recognition"""
        self.running = False
        logger.info("Facial recognition stopped")
    
    def _recognition_loop(self):
        """Main facial recognition loop"""
        try:
            # Initialize camera
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                logger.error("Could not open camera")
                self.running = False
                return
                
            logger.info("Camera opened successfully")
            
            # Main loop
            while self.running:
                # Capture frame-by-frame
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Could not read frame from camera")
                    time.sleep(1)  # Wait before retrying
                    continue
                
                # Detect faces
                faces = self._detect_faces(frame)
                
                # Process detection results
                if len(faces) > 0:
                    # Face detected
                    if not self.face_detected:
                        self.face_detected = True
                        face_data = {"count": len(faces), "positions": faces}
                        
                        # Call callback if set
                        if self.on_face_detected:
                            self.on_face_detected(face_data)
                    
                    # Process emotions periodically
                    current_time = time.time()
                    if current_time - self.last_emotion_time > self.emotion_interval:
                        self.last_emotion_time = current_time
                        emotion = self._detect_emotion(frame, faces[0])
                        
                        # Call callback if emotion changed and callback is set
                        if emotion != self.current_emotion and self.on_emotion_detected:
                            self.current_emotion = emotion
                            self.on_emotion_detected(emotion)
                else:
                    # No face detected
                    if self.face_detected:
                        self.face_detected = False
                        
                        # Call callback if set
                        if self.on_face_lost:
                            self.on_face_lost()
                
                # Wait before next detection
                time.sleep(self.detection_interval)
            
            # Release the camera when done
            cap.release()
            
        except Exception as e:
            logger.error(f"Error in facial recognition loop: {str(e)}")
            self.running = False
    
    def _detect_faces(self, frame):
        """Detect faces in the frame"""
        if self.advanced_face_detection:
            return self._detect_faces_dnn(frame)
        else:
            return self._detect_faces_haar(frame)
    
    def _detect_faces_haar(self, frame):
        """Detect faces using Haar Cascade"""
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return faces
    
    def _detect_faces_dnn(self, frame):
        """Detect faces using DNN model"""
        # Get frame dimensions
        h, w = frame.shape[:2]
        
        # Create a blob from the image
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 1.0,
            (300, 300), (104.0, 177.0, 123.0)
        )
        
        # Pass the blob through the network
        self.face_net.setInput(blob)
        detections = self.face_net.forward()
        
        # Process detections
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            # Filter based on confidence
            if confidence > 0.5:
                # Convert to face rectangle coordinates
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                x1, y1, x2, y2 = box.astype("int")
                
                # Convert to format expected by other functions
                faces.append((x1, y1, x2-x1, y2-y1))
        
        return faces
    
    def _detect_emotion(self, frame, face):
        """
        Detect emotion from face
        
        This is a simplified implementation. In a real system, you would use
        a more sophisticated emotion recognition model.
        """
        # For demonstration, return a random emotion
        # In a real implementation, this would use an actual emotion recognition model
        import random
        emotions = ["neutral", "happy", "sad", "surprised", "angry"]
        weights = [0.6, 0.2, 0.1, 0.05, 0.05]  # More likely to be neutral
        
        return random.choices(emotions, weights=weights)[0] 