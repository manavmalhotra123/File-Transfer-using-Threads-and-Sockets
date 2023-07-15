import socket
import streamlit as st

BUFFER_SIZE = 4096

def receive_file(conn, file_path):
    """Receives file data from the server and saves it to a file"""
    with open(file_path, 'wb') as file:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            file.write(data)
            print("Received data chunk")

def client_interface():
    st.title("File Transfer - Client")

    # Get local IP addresses
    ip_addresses = socket.gethostbyname_ex(socket.gethostname())[2]

    selected_ip = st.selectbox("Select Server IP Address", ip_addresses)

    PORT = st.number_input("Enter the server port number:", min_value=0, max_value=65535, value=12345)

    file_path = st.text_input("Enter the file path to save:")

    if st.button("Start Transfer"):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
            conn.connect((selected_ip, PORT))
            print(f"Connected to server at {selected_ip}:{PORT}")

            receive_file(conn, file_path)

        st.info("File received successfully")

if __name__ == "__main__":
    client_interface()
