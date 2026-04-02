import json
import logging
import mimetypes
import socket
import time
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Event, Thread

BASE_DIR = Path(__file__).resolve().parent
BUFFER_SIZE = 1024
HTTP_PORT = 8080
HTTP_HOST = "0.0.0.0"
SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 4000


class HttpInit(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case "/":
                self.send_html("index.html")
            case "/message":
                self.send_html("message.html")
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_statics(file)
                else:
                    self.send_html("error.html", 404)

    def do_POST(self) -> None:
        size = self.headers["Content-Length"]
        data = self.rfile.read(int(size))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SOCKET_HOST, SOCKET_PORT))
            client_socket.sendall(data)

        self.header_return(302, "Location", "/message")

    def send_html(self, filename: str, status_code: int = 200) -> None:
        self.header_return(status_code)

        path = BASE_DIR / "templates" / filename

        with open(path, "rb") as file:
            self.wfile.write(file.read())

    def send_statics(self, filename: Path, status_code: int = 200) -> None:
        self.send_response(status_code)
        mime_type, _ = mimetypes.guess_type(str(filename))
        if mime_type is not None:
            self.send_header("Content-Type", mime_type)
        else:
            self.send_header("Content-Type", "text/plain")
        self.end_headers()

        with open(filename, "rb") as file:
            self.wfile.write(file.read())

    def header_return(
        self,
        status_code: int = 200,
        content: str = "Content-type",
        typing: str = "text/html",
    ) -> None:
        self.send_response(status_code)
        self.send_header(content, typing)
        self.end_headers()


def save_form_data(data: bytes) -> None:
    filename = BASE_DIR / "storage" / "data.json"
    parse_data = urllib.parse.unquote_plus(data.decode())
    try:
        parse_dict: dict[str, str] = {
            k: v for k, v in [value.split("=") for value in parse_data.split("&")]
        }
        with open(filename, encoding="utf-8") as file:
            open_file = json.load(file)

        open_file[str(datetime.now())] = parse_dict

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(open_file, file, ensure_ascii=False, indent=4)
    except OSError as err:
        logging.error(err)


def run_socket_server(
    stop_event: Event, host: str = SOCKET_HOST, port: int = SOCKET_PORT
) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server:
        socket_server.bind((host, port))
        socket_server.listen()
        socket_server.settimeout(1)
        while not stop_event.is_set():
            try:
                conn, address = socket_server.accept()
            except TimeoutError:
                continue
            logging.info(f"Socket received {address}")
            with conn:
                data = conn.recv(BUFFER_SIZE)
                if data:
                    save_form_data(data)

    logging.info("Socket server stopped")


def run_http_server(http_server: HTTPServer) -> None:
    logging.info("Starting http server")
    http_server.serve_forever()
    logging.info("HTTP server stopped")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")

    stop_event = Event()

    http_server = HTTPServer((HTTP_HOST, HTTP_PORT), HttpInit)

    server = Thread(target=run_http_server, args=(http_server,))

    server_socket = Thread(
        target=run_socket_server, args=(stop_event, SOCKET_HOST, SOCKET_PORT)
    )

    server.start()
    server_socket.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        logging.info("Stopping servers...")
        stop_event.set()
        http_server.shutdown()
        http_server.server_close()

        logging.info("Waiting HTTP thread...")
        server.join()
        logging.info("HTTP thread joined")

        logging.info("Waiting socket thread...")
        server_socket.join()
        logging.info("Socket thread joined")

        logging.info("Servers stopped")
