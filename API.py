import urllib.request
import json

class Minecraft:
    """Free API from mcapis.us"""
    def ServerInfo(IP, port):
        """Search the Minecraft server and return the informations"""
        info = "https://mcapi.us/server/status?ip="+IP+"&port="+port
        try:
            response = urllib.request.urlopen(info)
        except urllib.error.HTTPError:
            return "error 404"
        content = response.read()
        data = json.loads(content.decode("utf8"))

        if data["status"] == "error" and data['error'] == "invalid hostname or port":
            return "error 404"
        elif data['status'] == "error":
            return "unknow error"

        return data
