#!/usr/bin/env python3
# Ana AI Assistant - Events Module (Minimal Implementation)

import logging
from typing import Dict, Callable, List, Any

logger = logging.getLogger('Ana.Events')

# Global event handlers dictionary
_event_handlers: Dict[str, List[Callable]] = {}

def register_event_handler(event_name: str, handler_func: Callable) -> bool:
    """Register an event handler function for a specific event"""
    global _event_handlers
    
    if event_name not in _event_handlers:
        _event_handlers[event_name] = []
    
    _event_handlers[event_name].append(handler_func)
    logger.debug(f"Registered handler for event: {event_name}")
    return True

def trigger_event(event_name: str, *args, **kwargs) -> bool:
    """Trigger an event, calling all registered handlers"""
    global _event_handlers
    
    if event_name not in _event_handlers:
        return False
    
    for handler in _event_handlers[event_name]:
        try:
            handler(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in event handler for {event_name}: {str(e)}")
    
    return True

def unregister_event_handler(event_name: str, handler_func: Callable) -> bool:
    """Unregister an event handler function"""
    global _event_handlers
    
    if event_name not in _event_handlers:
        return False
    
    if handler_func in _event_handlers[event_name]:
        _event_handlers[event_name].remove(handler_func)
        logger.debug(f"Unregistered handler for event: {event_name}")
        return True
    
    return False 