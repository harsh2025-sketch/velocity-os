"""
VELOCITY A-OS: SENSES MANAGER
Central hub for all sensory input (vision, audio, proprioception)
"""

import asyncio
from typing import Dict, Optional
from .ears.stream import AudioStream
from .eyes.retina import ScreenRetina
from .sentry.watcher import EnvironmentWatcher


class SensesManager:
    """
    Manages all sensory subsystems and provides unified interface
    """
    
    def __init__(self):
        self.audio_stream: Optional[AudioStream] = None
        self.screen_retina: Optional[ScreenRetina] = None
        self.environment_watcher: Optional[EnvironmentWatcher] = None
        self.running = False
        
    async def initialize(self):
        """Initialize all sensory subsystems"""
        print("[SENSES] Initializing sensory cortex...")
        
        try:
            self.audio_stream = AudioStream()
            await self.audio_stream.initialize()
            
            self.screen_retina = ScreenRetina()
            await self.screen_retina.initialize()
            
            self.environment_watcher = EnvironmentWatcher()
            await self.environment_watcher.initialize()
            
            self.running = True
            print("[SENSES] All sensory systems online [OK]")
            return True
        except Exception as e:
            print(f"[SENSES] Initialization failed: {e}")
            return False
    
    async def process_sensory_input(self):
        """Main sensory processing loop"""
        tasks = []
        
        if self.audio_stream:
            tasks.append(self.audio_stream.stream())
        if self.screen_retina:
            tasks.append(self.screen_retina.capture_and_analyze())
        if self.environment_watcher:
            tasks.append(self.environment_watcher.watch())
        
        if tasks:
            await asyncio.gather(*tasks)
    
    async def get_screen_content(self) -> Optional[Dict]:
        """Get current screen analysis"""
        if self.screen_retina:
            return await self.screen_retina.get_analysis()
        return None
    
    async def get_audio_input(self) -> Optional[str]:
        """Get transcribed audio"""
        if self.audio_stream:
            return await self.audio_stream.get_transcription()
        return None
    
    async def shutdown(self):
        """Shutdown all sensory systems"""
        self.running = False
        if self.audio_stream:
            await self.audio_stream.shutdown()
        if self.screen_retina:
            await self.screen_retina.shutdown()
        if self.environment_watcher:
            await self.environment_watcher.shutdown()
