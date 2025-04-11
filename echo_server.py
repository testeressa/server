import socket
from http import HTTPStatus
from urllib.parse import parse_qs, urlparse


def handle_request(client_socket):
    request_data = client_socket.recv(4096).decode('utf-8')
    if not request_data:
        return

    request_lines = request_data.split('\r\n')
    request_line = request_lines[0]
    method = request_line.split()[0]

    headers = request_lines[1:]
    headers_dict = {}
    for header in headers:
        if ': ' in header:
            key, value = header.split(': ', 1)
            headers_dict[key] = value

    url = request_line.split()[1]
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    status_code = 200
    if 'status' in query_params:
        try:
            status_code = int(query_params['status'][0])
        except (ValueError, IndexError):
            status_code = 200

    try:
        status_phrase = HTTPStatus(status_code).phrase
    except ValueError:
        status_code = 200
        status_phrase = HTTPStatus(status_code).phrase

    status_line = f"{status_code} {status_phrase}"

    client_address = client_socket.getpeername()

    response_headers = [
        f"Request Method: {method}",
        f"Request Source: {client_address}",
        f"Response Status: {status_line}"
    ]

    for key, value in headers_dict.items():
        response_headers.append(f"{key}: {value}")

    response_body = '\r\n'.join(response_headers)

    response = (
        f"HTTP/1.1 {status_line}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(response_body)}\r\n"
        "\r\n"
        f"{response_body}"
    )

    client_socket.sendall(response.encode('utf-8'))


def run_server(host='127.0.0.1', port=8080):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Echo server is running on http://{host}:{port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            handle_request(client_socket)
            client_socket.close()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server_socket.close()


# run_server()
