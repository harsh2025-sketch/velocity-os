import multiprocessing
import time
from .synapse import Synapse
from .drones import scout, sentry, analyst

class Queen:
    def __init__(self):
        self.synapse = Synapse(mode='queen')
        self.drones = {}

    def spawn(self, drone_type, task_id, params):
        """
        Spawns a new Drone process.
        """
        print(f"👑 Queen: Spawning {drone_type} for Task {task_id}")
        
        if drone_type == 'scout':
            target = scout.run
        elif drone_type == 'sentry':
            target = sentry.run
        else:
            print("Unknown Drone Type")
            return

        p = multiprocessing.Process(target=target, args=(params,))
        p.start()
        self.drones[task_id] = p

    def run(self):
        print("👑 Queen: Reigning over the Swarm...")
        # Listen for results from Drones
        self.synapse.listen(self.handle_drone_report)

    def handle_drone_report(self, topic, data):
        if topic == "TASK_COMPLETE":
            print(f"✅ Task {data['id']} Finished: {data['result']}")
            # Kill the drone process to save RAM
            if data['id'] in self.drones:
                self.drones[data['id']].terminate()
                del self.drones[data['id']]

if __name__ == "__main__":
    q = Queen()
    q.run()
        self.running = True
        
        while self.running:
            try:
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                # Route task to appropriate drone
                drone_id = await self._route_task(task)
                if drone_id and drone_id in self.drones:
                    await self.drones[drone_id].execute(task)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"[QUEEN] Coordination error: {e}")
    
    async def _route_task(self, task: Dict) -> Optional[str]:
        """Determine which drone should handle the task"""
        task_type = task.get("type", "")
        
        for drone_id, drone in self.drones.items():
            if task_type in drone.capabilities:
                return drone_id
        
        return None
    
    async def shutdown(self):
        """Graceful shutdown of all drones"""
        self.running = False
        for drone in self.drones.values():
            await drone.shutdown()
        print("[QUEEN] Swarm shutdown complete")
