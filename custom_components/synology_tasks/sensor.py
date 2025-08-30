import requests
import os

def main():
    verify_ssl = os.getenv("VERIFY_SSL", "True") == "True"
    host = os.getenv("SYNOLOGY_HOST")
    pw = os.getenv("SYNOLOGY_PASSWORD")
    user = os.getenv("SYNOLOGY_USER")

    s = requests.Session()

    params = {
        "api": "SYNO.API.Auth",
        "version": "7",
        "method": "login",
        "enable_syno_token": "yes",
        "account": user,
        "passwd": pw,
    }

    r = s.get(f"{host}/webapi/entry.cgi", params=params, verify=verify_ssl)
    print(r.text)

if __name__ == "__main__":
    main()
