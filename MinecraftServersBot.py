import API
import botogram
from datetime import datetime

bot = botogram.create("TOKEN")

@bot.command("start")
def start(chat, message, args):
    """Welcome!"""
    message.reply("*Welcome!*"+\
        "\n*Thanks* you very much for starting *me*!"+\
        "\n*How use me*? Do /help!"+
        "\nDo you need more *help*? Contact me! @MarcoBuster")

@bot.command("help")
def help(chat, message):
    """Help command"""
    message.reply("<b>How to use this bot?</b>"+
            "\n<b>Server command</b>"+
            "\nWithin this command, you can search for a <b>Minecraft server</b>"+\
            "\nUsage: <code>/server server-ip server-port</code>"+
            "\nIf not <b>specified</b>, the port it's set by <b>default</b> on <code>25565</code>"
            "\nExample: <code>/server mc.mycrazyserver.com 25540</code> (Not working lol)"+
            "\nMore commands will added soon, stay tuned!")

@bot.command("server")
def server(chat, message, args):
    """Search a Minecraft Server"""
    IP = args[0]

    if len(args) == 1:
        port = "25565"
    else:
        port = args[1]

    data = API.Minecraft.ServerInfo(IP, port)

    if data == "error 404":
        message.reply("*Error*\n_Error 404: not found_"+\
            "\nThe IP address (`"+IP+"`) or the port (`"+port+"`) is invalid.")
        return

    if data == "unknow error":
        message.reply("*Error*\n_Unknow error_"+\
            "\nMaybe a internal server error, sorry :(")
        return

    last_updated =  datetime.fromtimestamp(int(data['last_updated'])).strftime('%d/%m/%Y %H:%M')

    if data['online'] == True:
        start_string, last_online_string = "✅<b>Online!</b>", "\n"
    else:
        if data['last_online'] == None:
            last_online = "None"
        else:
            last_online = datetime.fromtimestamp(int(data['last_online'])).strftime('%d/%m/%Y %H:%M')
        start_string, last_online_string = "❌<b>Offline!</b>", "\n<b>Last online</b>: "+last_online+"\n"
    message.reply(start_string+\
                "\n<b>IP</b>: "+IP+" (<code>"+str(data['players']['now'])+"</code><b>/</b><code>"+str(data['players']['max'])+"</code>)"+\
                "\n<b>Version</b>: "+data['server']['name']+\
                last_online_string+\
                "<b>Last updated</b>: "+last_updated, syntax="HTML")

if __name__ == "__main__":
    bot.run()
