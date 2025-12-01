import time, queue, threading, requests
from typing import Dict, Any
from src.colony import Colony
from src.subsystems import Subsystem, SubsystemType

COMMURL = "https://communicationservice-production.up.railway.app"

class Service:
    def __init__(self, interval: int = 5, run_for_minutes: int = 10, colony: Colony = Colony(max_ants=100, initial_food_stock=1000, ant_lifespan_minutes=1.5)):
        self.interval = interval
        self.run_for_minutes = run_for_minutes
        self.calls = 0
        self.messageIds = []
        self.messageQueue = queue.Queue()
        self.colony = colony
        
        # Threading control
        self._stop_event = threading.Event()
        self._thread = None
        self.end_time = 0

    def get_status(self) -> Dict[str, Any]:
        return {
            'interval': self.interval,
            'run_for_minutes': self.run_for_minutes,
            'end_time': str(self.end_time),
            'messages_pending': self.messageQueue.qsize(), # Adjusted for clearer status
            'calls': self.calls,
            'is_running': self._thread.is_alive() if self._thread else False
        }

    def service_start(self):
        """Starts the service in a background thread."""
        if self._thread and self._thread.is_alive():
            print("Service is already running.")
            return

        print("Starting service...")
        # Reset the stop event
        self._stop_event.clear()
        
        # Recalculate end_time relative to when start is called
        self.end_time = time.time() + (60 * self.run_for_minutes)
        
        # Start the background thread
        # self._run_loop() # for debuggin
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def service_stop(self):
        """Stops the background service."""
        if not self._thread or not self._thread.is_alive():
            print("Service is not running.")
            return

        print("Stopping service...")
        # Signal the thread to stop
        self._stop_event.set()
        # Wait for the thread to finish its current iteration
        self._thread.join()
        print("Service stopped.")

    def _run_loop(self):
        """Internal method that runs the main loop."""
        # Loop while time remains AND we haven't been asked to stop
        while time.time() < self.end_time and not self._stop_event.is_set():
            self.calls += 1
            try:
                # 1. Poll for messages
                response = requests.get(COMMURL + "/api/mensaje/S03_REI")
                if response.status_code == 200:
                    data = response.json()
                    for message in data:
                        if message['id'] not in self.messageIds:
                            self.messageIds.append(message['id'])
                            self.messageQueue.put(message)

                # 2. Process the queue
                self._process_queue()

            except Exception as e:
                print(f"Error in service loop: {e}")

            # Wait for interval, but wake up immediately if stop is called
            self._stop_event.wait(self.interval)

    def _process_queue(self):
        """Helper method to process messages in the queue."""
        while not self.messageQueue.empty():
            message = self.messageQueue.get()
            
            try:
                contenido = message["mensaje"]
                tipo = contenido["tipo"]
                emisor = message["emisor"]
                
                subsystem = Subsystem.get_by_name(emisor)
                
                if subsystem and subsystem.name == SubsystemType.DEFENSE.value:
                    self._handle_defense_logic(tipo, contenido)
                    
            except Exception as e:
                print(f"Error processing individual message: {e}")

    def _handle_defense_logic(self, tipo, contenido):
        """Logic specific to the Defense subsystem."""
        if tipo == "solicitud_hormigas":
            datos = contenido["contenido"]
            request_ref = datos["request_ref"]
            threat_id = datos["threat_id"]
            ants_needed = datos["ants_needed"]

            ant_response = self.colony.request_ants(
                subsystem_name=SubsystemType.DEFENSE.value, 
                quantity=ants_needed
            )

            package = {
                "emisor": "S03_REI",
                "receptor": f"{SubsystemType.DEFENSE.value}",
                "mensaje": {
                    "tipo": "asignacion_hormigas" if ant_response["success"] else "rechazo_hormigas",
                    "contenido": {
                        "request_ref": request_ref,
                        "threat_id": threat_id,
                        "assignment_successful": ant_response["success"]
                    }
                }
            }

            if ant_response["success"]:
                ants = []
                for ant in ant_response["ants"]:
                    ants.append(ant.to_dict())
                package["mensaje"]["contenido"]["ants"] = ants
            else:
                package["mensaje"]["contenido"]["motivo"] = "insuficientes"

            requests.post(COMMURL + "/api/mensaje", json=package)

        elif tipo == "resultado_ataque":
            datos = contenido["contenido"]
            survivors = datos["survivors"]
            for ant in survivors:
                self.colony.return_ant(ant["id"])