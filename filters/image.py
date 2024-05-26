def func(log_data):
    return (
        log_data["method"] == "Network.responseReceived"
        and log_data["params"]["type"] == "Image"
    )
