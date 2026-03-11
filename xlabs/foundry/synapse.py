import zmq
import json
import threading

class Synapse:
    """
    The Nervous System. Uses ZeroMQ PUB/SUB for <1ms IPC.
    """
    def __init__(self, mode='client', port=5555):
        self.context = zmq.Context()
        self.port = port
        self.mode = mode
        
        if mode == 'queen':
            # Queen publishes commands, subscribes to data
            self.pub_socket = self.context.socket(zmq.PUB)
            self.pub_socket.bind(f"tcp://*:{port}")
            
            self.sub_socket = self.context.socket(zmq.SUB)
            self.sub_socket.bind(f"tcp://*:{port+1}")
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
            
        else: # Drone
            # Drones subscribe to commands, publish data
            self.sub_socket = self.context.socket(zmq.SUB)
            self.sub_socket.connect(f"tcp://localhost:{port}")
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
            
            self.pub_socket = self.context.socket(zmq.PUB)
            self.pub_socket.connect(f"tcp://localhost:{port+1}")

    def broadcast(self, topic, payload):
        """Send a message to the Swarm"""
        message = f"{topic} {json.dumps(payload)}"
        self.pub_socket.send_string(message)

    def listen(self, callback):
        """Blocking listener loop"""
        while True:
            try:
                message = self.sub_socket.recv_string()
                topic, payload_str = message.split(" ", 1)
                payload = json.loads(payload_str)
                callback(topic, payload)
            except Exception as e:
                print(f"Synapse Error: {e}")
