from config import utelegram_config
import threading

import utelegram

bot = utelegram.ubot(utelegram_config['token'])


def get_message(message):
    print(message)
    
def reply_ping(message):
    print(message)
    
bot.register('/paradox', reply_ping)
bot.set_default_handler(get_message)

bot.send(utelegram_config['messageid'],'pong')

bot.listen()
#t1= threading.Thread(target=bot.listen)



#if __name__ == '__main__':
#    t1.start()
#    while True:
#        pass