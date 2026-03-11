"""
VELOCITY A-OS: BASE DRONE CLASS
Abstract base class for all swarm workers
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class Drone(ABC):
    """Abstract base class for drone workers"""
    
    def __init__(self, drone_id: str, config: Dict = None):
        self.id = drone_id
        self.config = config or {}
        self.capabilities: List[str] = []
        self.running = False
        self.task_queue: asyncio.Queue = asyncio.Queue()
        
    @abstractmethod
    async def initialize(self):
        """Initialize drone"""
        pass
    
    @abstractmethod
    async def execute(self, task: Dict):
        """Execute a task"""
        pass
    
    async def run(self):
        """Main drone loop"""
        await self.initialize()
        self.running = True
        
        while self.running:
            try:
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                await self.execute(task)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"[DRONE {self.id}] Error: {e}")
    
    async def shutdown(self):
        """Shutdown drone"""
        self.running = False
        print(f"[DRONE {self.id}] Shutdown complete")
