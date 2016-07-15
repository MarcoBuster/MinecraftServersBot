#coding: utf-8
import API
import botogram
from datetime import datetime
import sqlite3

import botogram.objects.base
class InlineQuery(botogram.objects.base.BaseObject):
    required = {
        "id": str,
        "from": botogram.User,
        "query": str,
    }
    optional = {
        "location": botogram.Location,
        "offest": str,
    }
    replace_keys = {
        "from": "sender"
    }
botogram.Update.optional["inline_query"] = InlineQuery

bot = botogram.create("TOKEN")

conn = sqlite3.connect('MinecraftBot.db')
c = conn.cursor()

try:
    c.execute('''CREATE TABLE users(userid INTEGER)''')
except:
    pass

@bot.command("start")
def start(chat, message, args):
    """Welcome!"""
    if len(args) == 0:
        message.reply("*Welcome!*"+\
            "\n*Thanks* you very much for starting *me*!"+\
            "\n*How use me*? Do /help!"+
            "\nDo you need more *help*? Contact me! @MarcoBuster")
        c.execute('''DELETE FROM users WHERE userid=?''',(message.sender.id,))
        c.execute('''INSERT INTO users VALUES(?)''',(message.sender.id,))
        conn.commit()
        return
    if args[0] == "inline":
        message.reply("*Inline tutorial*\nThis bot it's inline, too!"+
                "\n[Inline? What does it mean?](https://core.telegram.org/bots/inline)"+\
                "\n*Search Minecraft Servers in any chat:* "+\
                "\n`@MinecraftServersBot serverip:port`")
        return

@bot.command("viewusers")
def viewusers(chat, message, args):
    """View the list and the count of users"""
    if message.sender.id != 26170256: #Only admin command
        message.reply("This command it's only for the admin of the bot")
        return

    c.execute('''SELECT * FROM users''')
    users_list = c.fetchall()
    c.execute('''SELECT COUNT(*) AS count FROM users;''')
    count = c.fetchone()[0]

    message = "<b>This is the list of users who executed /start</b>:\n"
    for res in users_list:
        message = message+str(res[0])+", "

    message = message + "\n<b>In total, there are "+str(count)+" users.</b>"
    chat.send(message)

@bot.command("post")
def post(chat, message, args):
    """Post a message to all users"""
    if message.sender.id != 26170256: #Only admin command
        message.reply("This command it's only for the admin of the bot")
        return

    c.execute('''SELECT * FROM users''')
    users_list = c.fetchall()

    message = " ".join(message.text.split(" ", 1)[1:])

    for res in users_list:
        try:
            bot.chat(res[0]).send(message)
            chat.send("Post sended to "+str(res[0]))
        except botogram.api.ChatUnavailableError:
            c.execute('DELETE FROM users WHERE userid={}'.format(res[0]))
            chat.send("The user "+str(res[0])+" has blocked your bot, so I removed him from the database")
            conn.commit()

    chat.send("<b>Done!</b>\nThe message has been delivered to all users") #Yeah
    conn.commit()

@bot.command("help")
def help(chat, message):
    """Help command"""
    message.reply("<b>How to use this bot?</b>"+
            "\n<b>Server command</b>"+
            "\nWithin this command, you can search for a <b>Minecraft server</b>"+\
            "\nUsage: <code>/server server-ip server-port</code>"+
            "\nIf not <b>specified</b>, the port it's set by <b>default</b> on <code>25565</code>"
            "\nExample: <code>/server mc.mycrazyserver.com 25540</code> (Not working lol)"+
            "\nMore commands will added soon, stay tuned!\n"
            "\nGitHub repostory: http://bit.ly/29FZGA6"+\
            "\nDeveloper: @MarcoBuster"+\
            "\nOther bots: /bots")

@bot.command("bots")
def bots(chat, message):
    """www.github.com/MarcoBuster"""
    message.reply("*Other bots written by @MarcoBuster*: "+\
        "\n🇮🇹 @OrarioTreniBot - Search trains, stations, itineraries and stats. Inline, too!"+\
        "\n🇮🇹 @ClasseVivaBot - Login in your ClasseViva student account, and see grades, agenda and files!"+\
        "\n🇮🇹 @FrancoIlTassista - Italian channel with funny post, daily.")

@bot.command("server")
def server(chat, message, args):
    """Search a Minecraft Server"""
    if len(args) == 0:
        message.reply("<b>Nope</b>"+\
        "\nYou must write <code>/server IP port</code> for search a server.")
        return
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

def process_inline(bot, chains, update):
    user = update.inline_query.sender
    text = update.inline_query.query
    if text == "":
        bot.api.call("answerInlineQuery",{"inline_query_id":update.inline_query.id,\
            "switch_pm_text":"Need help? Click here!",\
            "switch_pm_parameter":"inline",\
            "cache_time":0, "results":'[{"type":"article","id":"2",'\
                '"title":"Hello!","description":"Write a server IP here '\
                'with this format: mc.server.ip port","input_message_content":{"message_text":"'+\
                    '<b>Error</b>\nI must write a IP of a server after <code>@MinecraftServersBot</code>'+\
                    '\nExample: <code>@MinecraftServersBot mc.server.ip port</code>"'+\
                    ',"parse_mode":"HTML"}}]'})
        return

    text = text.split(":")
    IP = ''.join(text[0])
    try:
        port = ''.join(text[1])
    except IndexError:
        port = "25565"

    data = API.Minecraft.ServerInfo(IP, port)

    if data == "error 404":
        bot.api.call("answerInlineQuery",{"inline_query_id":update.inline_query.id,\
            "switch_pm_text":"Need help? Click here!",\
            "switch_pm_parameter":"inline",\
            "cache_time":0, "results":'[{"type":"article","id":"2",'\
                '"title":"Server not found","description":"Error! The IP address '\
                'and the port are correct?","input_message_content":{"message_text":"'+\
                    '<b>Error 404</b>\n<code>Server not found</code>\nUse this format: '+\
                    '<code>@MinecraftServersBot mc.server.ip:port</code>"'+\
                    ',"parse_mode":"HTML"}}]'})
        return

    last_updated =  datetime.fromtimestamp(int(data['last_updated'])).strftime('%d/%m/%Y %H:%M')

    if data['online'] == True:
        start_string, last_online_string = "<b>Online!</b>", "\n"
    else:
        if data['last_online'] == None:
            last_online = "None"
        else:
            last_online = datetime.fromtimestamp(int(data['last_online'])).strftime('%d/%m/%Y %H:%M')
        start_string, last_online_string = "<b>Offline!</b>", "\n<b>Last online</b>: "+last_online+"\n"
    text = start_string+\
                "\n<b>IP</b>: "+IP+" (<code>"+str(data['players']['now'])+\
                "</code><b>/</b><code>"+str(data['players']['max'])+"</code>)"+\
                "\n<b>Version</b>: "+data['server']['name']+\
                last_online_string+\
                "<b>Last updated</b>: "+last_updated

    bot.api.call("answerInlineQuery",{"inline_query_id":update.inline_query.id,\
        "switch_pm_text":"Go to the bot for more functions",\
        "switch_pm_parameter":"inline",\
        "cache_time":0, "results":'[{"type":"article","id":"2",'\
            '"title":"Server found!","description":"Tap here to view '\
            'the informations about this server","input_message_content":'\
            '{"message_text":"'+text+'","parse_mode":"HTML"}}]'})


bot.register_update_processor("inline_query", process_inline)

@bot.chat_unavailable
def remove_user(chat, reason):
    '''If chat it's unavailable, remove the user'''
    c.execute('''DELETE FROM users WHERE userid=?''',(message.sender.id,))
    conn.commit()

if __name__ == "__main__":
    bot.run()
