import json
import logging
import mimetypes
import socket
import time
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

BASE_DIR = Path(__file__).resolve().parent
BUFFER_SIZE = 1024
HTTP_PORT = 3000
HTTP_HOST = "0.0.0.0"
SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 5000


class HttpInit(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        logging.info(self.path)
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
        size = self.headers.get("Content-Length")
        data = self.rfile.read(int(size))

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()

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
    host: str = SOCKET_HOST,
    port: int = SOCKET_PORT,
) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socket_server:
        socket_server.bind((host, port))
        logging.info("Starting socket server")
        try:
            while True:
                msg, address = socket_server.recvfrom(BUFFER_SIZE)
                logging.info(f"Socket received {address}: {msg}")
                save_form_data(msg)
        except KeyboardInterrupt:
            pass
        finally:
            socket_server.close()

    logging.info("Socket server stopped")


def run_http_server(http_server: ThreadingHTTPServer) -> None:
    logging.info("Starting http server")
    http_server.serve_forever()
    logging.info("HTTP server stopped")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")

    http_server = ThreadingHTTPServer((HTTP_HOST, HTTP_PORT), HttpInit)
    logging.info(f"Starting http server on {HTTP_HOST}:{HTTP_PORT}")

    server = Thread(target=run_http_server, args=(http_server,))

    server_socket = Thread(
        target=run_socket_server,
        args=(SOCKET_HOST, SOCKET_PORT),
    )

    server.start()
    server_socket.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        logging.info("Stopping servers...")
        http_server.shutdown()
        http_server.server_close()

        logging.info("Waiting HTTP thread...")
        server.join()
        logging.info("HTTP thread joined")

        logging.info("Waiting socket thread...")
        server_socket.join()
        logging.info("Socket thread joined")

        logging.info("Servers stopped")
