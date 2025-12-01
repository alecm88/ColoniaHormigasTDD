from typing import Dict, List, Optional, Any
from src.main import app, colony
from src.subsystems import Subsystem, SubsystemType
import time, requests, queue

COMMURL = "https://communicationservice-production.up.railway.app"

class Service: 
    def __init__(self, interval: int = 5, run_for_minutes: int = 10):
        self.interval = interval
        self.run_for_minutes = run_for_minutes
        self.end_time = time.time() + (60 * run_for_minutes)
        self.calls = 0
        self.messageIds = []
        self.messageQueue = queue.Queue()

    def get_status(self) -> Dict[str, Any]:
        return {
            'interval': self.interval,
            'run_for_minutes': self.run_for_minutes,
            'end_time': self.end_time,
            'messages': self.messageQueue,
            'calls': self.calls
        }
    
    def run_for_duration(self):
        # Loop while the current time is less than the end time
        while time.time() < self.end_time:
            self.calls += 1
            try:
                response = requests.get(COMMURL + "/api/mensaje/S03_REI")
                if (response.status_code == 200):
                    data = response.json()
                    for message in data:
                        if (message['id'] not in self.messageIds):
                            self.messageIds.append(message['id'])
                            self.messageQueue.put(message)
                
                # Process the queue: This should be done in a separate function call asynchronously
                while not self.messageQueue.empty():
                    message = self.messageQueue.get()
                    contenido = message["mensaje"]
                    tipo = contenido["tipo"]
                    emisor = message["emisor"]
                    if (Subsystem.get_by_name(emisor)):
                        # Cadena de defense
                        if (Subsystem.get_by_name(emisor).name == SubsystemType.DEFENSE.value):
                            if (tipo == "solicitud_hormigas"):
                                datos = contenido["contenido"]
                                request_ref = datos["request_ref"]
                                threat_id = datos["threat_id"]
                                ants_needed = datos["ants_needed"]
                                # ant_response = client.post("/ants/request", json={"subsystem_name": SubsystemType.DEFENSE})
                                ant_response = colony.request_ant(SubsystemType.DEFENSE.value)
                                if(ant_response):
                                    package = {
                                        "emisor": "S03_REI",
                                        "receptor": f"{SubsystemType.DEFENSE.value}",
                                        "mensaje": {
                                            "tipo": "asignacion_hormigas",
                                            "contenido": {
                                                "request_ref": request_ref,
                                                "threat_id": threat_id,
                                                "ants": ant_response.to_dict(),
                                                "assignment_successful": True
                                            }
                                        }
                                    }
                                else:
                                    package = {
                                        "emisor": "S03_REI",
                                        "receptor": f"{SubsystemType.DEFENSE.value}",
                                        "mensaje": {
                                            "tipo": "rechazo_hormigas",
                                            "contenido": {
                                                "request_ref": request_ref,
                                                "threat_id": threat_id,
                                                "motivo": "insuficientes",
                                                "assignment_successful": False
                                            }
                                        }
                                    }
                                requests.post(COMMURL + "/api/mensaje", json=package)
                            elif (tipo == "resultado_ataque"):
                                datos = contenido["contenido"]
                                threat_id = datos["threat_id"]
                                survivors = datos["survivors"]
                                for ant in survivors:
                                    colony.return_ant(ant["id"])

            except Exception as e:
                print(f"Error: {e}")

            time.sleep(self.interval)