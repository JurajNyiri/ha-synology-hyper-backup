from datetime import datetime

LOG_TIME_FORMAT = "%Y/%m/%d %H:%M:%S"


def search_logs(log_list: list[dict], task_name: str) -> dict | None:
    """
    Return the most recent log entry for the given task name.
    Looks for events like "[Network][<task>] Backup integrity check is finished..."
    """
    matches = []
    needle = f"][{task_name}]"
    for entry in log_list:
        event = entry.get("event", "")
        if needle not in event:
            continue
        try:
            when = datetime.strptime(entry["time"], LOG_TIME_FORMAT)
        except Exception:
            continue
        matches.append((when, entry))
    if not matches:
        return None
    matches.sort(key=lambda tup: tup[0], reverse=True)
    return matches[0][1]
