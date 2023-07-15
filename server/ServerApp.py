import logging
import socket
import threading
from queue import Queue
import streamlit as st
import netifaces
from pynotifier import Notification

BUFFER_SIZE = 4096

# Pipeline
class Pipeline:
    def __init__(self, capacity):
        self.queue = Queue(capacity)

    def put_data(self, data):
        self.queue.put(data)

    def get_data(self):
        return self.queue.get()

def producer(pipeline, file):
    """Simulates reading file and producing data"""
    while True:
        data = file.read(BUFFER_SIZE)
        if not data:
            break
        pipeline.put_data(data)
        logging.info("Produced data chunk")

def consumer(pipeline, conn):
    """Simulates consuming data and sending it over the socket"""
    while True:
        data = pipeline.get_data()
        if not data:
            break
        conn.sendall(data)
        logging.info("Sent data chunk")

def get_local_ip_addresses():
    """Get the local IP addresses of the server"""
    ip_addresses = []
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            ipv4_addresses = addresses[netifaces.AF_INET]
            for ipv4 in ipv4_addresses:
                ip_addresses.append(ipv4['addr'])
    return ip_addresses

def server_interface():
    st.title("File Transfer - Server")

    # Drag and drop file selection
    file = st.file_uploader("Select a file", type=["txt", "pdf", "png", "jpg"])

    # Get local IP addresses
    ip_addresses = get_local_ip_addresses()

    selected_ip = st.selectbox("Select IP Address", ip_addresses)

    if st.button("Start Transfer") and file is not None:
        pipeline = Pipeline(capacity=10)
        producer_thread = threading.Thread(target=producer, args=(pipeline, file), daemon=True)

        # Socket communication
        HOST = selected_ip  # Selected IP address
        PORT = 12345

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen(1)
            logging.info(f"Server listening on {HOST}:{PORT}")

            ip_addresses_str = "\n".join(ip_addresses)
            Notification(
                title="Server Started",
                description=f"Listening on: {selected_ip}",
                duration=10
            ).send()

            conn, addr = s.accept()
            logging.info(f"Connected by {addr}")

            consumer_thread = threading.Thread(target=consumer, args=(pipeline, conn), daemon=True)

            producer_thread.start()
            consumer_thread.start()

            producer_thread.join()
            consumer_thread.join()

        st.info("File transfer completed")

if __name__ == "__main__":
    server_interface()
