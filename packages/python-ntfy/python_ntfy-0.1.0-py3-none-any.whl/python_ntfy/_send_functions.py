import json, requests


def send(self, message: str, title: str = None, format_as_markdown: bool = False):
    """
    Send a text based message to the server

    :param message: The message to send
    :param title: The title of the message. Optional
    :param format_as_markdown: If true, the message will be formatted as markdown. Optional
    :return: The response from the server

    :examples:
    response = client.send(message="Example message")
    response = client.send(message="Example message", title="Example title")
    response = client.send(message="*Example markdown*", format_as_markdown=True)
    """
    headers = {
        "Title": title,
        "Markdown": "true" if format_as_markdown else "false",
    }

    response = json.loads(
        requests.post(url=self.url, data=message, headers=headers, auth=self._auth).text
    )
    return response


def send_file(self, file: str, title: str = None):
    """
    Send a file to the server

    :param file_path: The path to the file to send
    :param title: The title of the file. Optional
    :return: The response from the server

    :examples:
    response = client.send_file(file_path="example.txt")
    """
    headers = {"Title": title, "Filename": file.split("/")[-1]}

    with open(file, "rb") as file:
        response = json.loads(
            requests.post(
                url=self.url, data=file, headers=headers, auth=self._auth
            ).text
        )
    return response
