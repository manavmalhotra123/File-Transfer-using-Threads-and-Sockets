import socket
import streamlit as st
import netifaces

BUFFER_SIZE = 4096

def receive_file(conn, file_path):
    """Receives file data from the client and saves it to a file"""
    with open(file_path, 'wb') as file:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            file.write(data)
            print("Received data chunk")

def send_file(conn, file_path):
    """Reads file data and sends it to the client"""
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(BUFFER_SIZE)
            if not data:
                break
            conn.sendall(data)
            print("Sent data chunk")

def get_network_interfaces():
    """Retrieves available network interfaces"""
    interfaces = netifaces.interfaces()
    ip_addresses = []
    for interface in interfaces:
        if_addrs = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
        if if_addrs:
            for if_addr in if_addrs:
                ip_addresses.append(if_addr['addr'])
    return ip_addresses

def client_interface():
    st.title("File Transfer - Client")

    # Get local IP addresses
    ip_addresses = get_network_interfaces()

    selected_interface = st.selectbox("Select Network Interface", ip_addresses)

    PORT = st.number_input("Enter the server port number:", min_value=0, max_value=65535, value=12345)

    file_path = st.text_input("Enter the file path to save:")

    if st.button("Start Transfer"):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
            conn.connect((selected_interface, PORT))
            print(f"Connected to server at {selected_interface}:{PORT}")

            receive_file(conn, file_path)

        st.info("File received successfully")

def server_interface():
    st.title("File Transfer - Server")

    # Get local IP addresses
    ip_addresses = get_network_interfaces()

    selected_interface = st.selectbox("Select Network Interface", ip_addresses)

    PORT = st.number_input("Enter the server port number:", min_value=0, max_value=65535, value=12345)

    file_path = st.text_input("Enter the file path to send:")

    if st.button("Start Server"):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((selected_interface, PORT))
            server.listen(1)
            print(f"Server started on {selected_interface}:{PORT}")

            conn, addr = server.accept()
            print(f"Connected to client at {addr[0]}:{addr[1]}")

            with conn:
                send_file(conn, file_path)

        st.info("File sent successfully")

if __name__ == "__main__":
    mode = st.selectbox("Select Mode", ["Client", "Server"])

    if mode == "Client":
        client_interface()
    else:
        server_interface()
