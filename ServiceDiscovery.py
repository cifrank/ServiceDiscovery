from flask import Flask, jsonify
import consul
import socket
import threading
import time

# Configuración
SERVICE_NAME = "example-service"
SERVICE_PORT = 5000
CONSUL_HOST = "127.0.0.1"
CONSUL_PORT = 8500

# Crear una instancia de Flask
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello from example service!"})

def register_service():
    c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

    # Obtenemos la IP del host
    hostname = socket.gethostname()
    service_ip = socket.gethostbyname(hostname)

    # Registramos el servicio
    c.agent.service.register(
        SERVICE_NAME,
        service_id=SERVICE_NAME + "-" + service_ip,
        address=service_ip,
        port=SERVICE_PORT,
        tags=["example"]
    )

    print(f"[INFO] Servicio registrado: {SERVICE_NAME} ({service_ip}:{SERVICE_PORT})")

def deregister_service():
    c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)
    hostname = socket.gethostname()
    service_ip = socket.gethostbyname(hostname)

    c.agent.service.deregister(SERVICE_NAME + "-" + service_ip)
    print(f"[INFO] Servicio eliminado: {SERVICE_NAME}")

def discover_services():
    c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)
    index = None

    while True:
        # Consultamos los servicios
        index, data = c.catalog.services(index=index)
        print("[INFO] Servicios disponibles:", data)
        time.sleep(5)

if __name__ == "__main__":
    try:
        # Registramos el servicio en Consul
        register_service()

        # Iniciamos un hilo para descubrir servicios
        discovery_thread = threading.Thread(target=discover_services, daemon=True)
        discovery_thread.start()

        # Ejecutamos la aplicación Flask
        app.run(host="0.0.0.0", port=SERVICE_PORT)
    except KeyboardInterrupt:
        # Eliminamos el servicio de Consul al interrumpir la ejecución
        deregister_service()
