import requests
import os
from typing import TypedDict


class SynologyAuthResponse(TypedDict):
    data: TypedDict(
        "SynologyAuthData",
        {"account": str, "device_id": str, "ik_message": str, "is_portal_port": bool, "sid": str, "synotoken": str}
    )
    success: bool

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
    response: SynologyAuthResponse = r.json()
    print(r.text)
    sid = response.get("data").get("sid")
    print(sid)

    # run the task
    params = {
        "api": "SYNO.Entry.Request",
        "method": "request",
        "version": "1",
        "stop_when_error": "false",
        "mode": "sequential",
        "compound": "[{\"api\":\"SYNO.Core.EventScheduler\",\"method\":\"run\",\"version\":1,\"task_name\":\"Sync Media\"}]",
        "SynoToken": response.get("data").get("synotoken")
    }
    r = s.get(f"{host}/webapi/entry.cgi", params=params, verify=verify_ssl)
    print(r.text)

    # logout
    params = {
        "api": "SYNO.API.Auth",
        "version": "6",
        "method": "logout",
        "_sid": sid
    }
    r = s.get(f"{host}/webapi/entry.cgi", params=params, verify=verify_ssl)
    print(r.text)

if __name__ == "__main__":
    main()
