from datetime import datetime

ALLOWED_LOG_LEVELS = {"INFO", "ERROR", "WARNING"}


def open_log_file(config) -> dict:
    if not config['run']['logfile']:
        raise ValueError("Error: open_log_file() called without setting a logfile parameter.")

    config['logfp'] = open(config['run']['logfile'], "a", buffering=1, encoding="utf-8")  # line-buffered
    return config


def write_log(config: dict, message: str, level: str = "INFO", stdout: bool = False):
    # Assemble log line
    timestamp = datetime.now().isoformat(timespec="seconds")
    line = f"[{timestamp}] {level:<7} {message}\n"

    # Print to stdout
    if level == "ERROR" or stdout or config['generic']['verbose']:
        print(line)

    # Write to file
    if not config['logfp'] or config['logfp'].closed:
        raise RuntimeError("Error: log file is not available or closed.")

    level = level.upper()
    if level not in ALLOWED_LOG_LEVELS:
        raise ValueError(f"Invalid log level: '{level}'. Use one of: {', '.join(ALLOWED_LOG_LEVELS)}")

    # Write the line
    config['logfp'].write(line)


def close_log_file(config) -> None:
    if config['logfp'] and not config['logfp'].closed:
        write_log(config, "Closing logfile")
        config['logfp'].close()


"""
logfile = open_log_file("analyse.log")

write_log(logfile, "Start analyse van bestanden")
write_log(logfile, "Bestand X verwerkt", level="INFO")
write_log(logfile, "Fout bij bestand Y", level="ERROR")

logfile.close()
"""