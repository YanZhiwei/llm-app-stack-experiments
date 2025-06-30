import sys

import httpx


def send_message(message: str, url: str = "http://localhost:9999/a2a/message"):
    payload = {
        "message": {
            "role": "user",
            "parts": [
                {
                    "kind": "text",
                    "text": message
                }
            ]
        }
    }
    response = httpx.post(url, json=payload)
    print("Status:", response.status_code)
    print("Response:", response.text)


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "hello"
    send_message(msg)
