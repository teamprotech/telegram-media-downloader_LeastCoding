import sys, os, time
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetAllChatsRequest
from telethon import errors
from datetime import datetime

def log_withTime(message=None, msg_id=None):
    timeStamp = datetime.now().strftime("%d-%b %H:%M:%S")
    if msg_id:
        print("[ERROR] " + timeStamp + " id: " + str(msg_id) + ' : ' + message)
    else:
        print("[INFO] " + timeStamp + ' : ' + message)


def initialize(api_id, api_hash):
    try:
        os.mkdir('downloaded_media')
    except:
        pass
    client = TelegramClient('media_downloader', api_id, api_hash)
    client.start()
    return client

def download_media(client, chat_title, skip_until=None):
    log_withTime("START-Time Marked here...")
    print("Reading the data-stats from File-NOW...")
    with open('last-message-id') as f:
        lines = f.read().splitlines()
        eco_num = int(lines[1].split()[0])
        dm_num = int(lines[2].split()[0])
        whist_num = int(lines[3].split()[0])
        ans_num = int(lines[4].split()[0])
    log_withTime("Below are the Collected-DATA. Cross check with file if NOT-okay break me in 120-seconds!!!")
    print(eco_num, dm_num, whist_num, ans_num)
    time.sleep(120)
    print("Will Continue now, With this data. Watch me!!")
    path = "/datahome2/tele-test/live-zignd/downloaded_media/"
    old_name = "/datahome2/tele-test/live-zignd/downloaded_media/manifest.mp4"
    file_flag = False
    break_msg_looping = False
    new_exists = True
    chats = client(GetAllChatsRequest(except_ids=[]))
    for _, chat in enumerate(chats.chats):
        if chat.title == chat_title:
            print("found chat with title", chat_title)
            print('attemping to iterate over messages to download media')
            skip_until = skip_until and int(skip_until)
            for message in client.iter_messages(chat, offset_id=skip_until):
                if break_msg_looping:
                    break
                elif message.media:
                    while True:
                        print(message.id, message.date, "message has media, downloading")
                        try:
                            client.download_media(message, file='downloaded_media')
                        except errors.FloodWaitError as e:
                            log_withTime("Failed to download THIS-Media...", message.id)
                            print(message.id, message.date, "failed to download media: flood wait error, were asked to wait for", e.seconds, " but will be waiting for", e.seconds + 120)
                            time.sleep(e.seconds + 120)
                            continue
                        except Exception as e:
                            print(message.id, message.date, "failed to download media")
                            log_withTime("Some Un-Handled Exception occured", message.id)
                            raise e
                        print(message.id, message.date, "media downloaded, waiting 10 seconds before the next one")
                        time.sleep(10)
                        log_withTime("Now moving OR renaming file if mainifest OR master-name...")
                        old_manifest = "/datahome2/tele-test/live-zignd/downloaded_media/manifest.mp4"
                        old_master = "/datahome2/tele-test/live-zignd/downloaded_media/master.mp4"
                        if os.path.exists(old_manifest):
                            file_flag = True
                            old_name = old_manifest
                        elif os.path.exists(old_master):
                            file_flag = True
                            old_name = old_master
                        else:
                            print("None of Pre-defined file exists... Should leave as it is ??")
                            
                        if eco_num > 0:
                            new_name = path + "Economics_Lecture_" + str(eco_num) + ".mp4"
                            eco_num = eco_num - 1
                        elif dm_num > 0:
                            new_name = path + "Disater-Management_Lecture_" + str(dm_num) + ".mp4"
                            dm_num = dm_num - 1
                        elif whist_num > 0:
                            new_name = path + "World-History_Lecture_" + str(whist_num) + ".mp4"
                            whist_num = whist_num - 1
                        elif ans_num > 0:
                            new_name = path + "Answer-Writing_Lecture_" + str(ans_num) + ".mp4"
                            whist_num = whist_num - 1
                        else:
                            print("No Pre-Defined naming-Counter remaining-now... STOPPING here and Implement for MORE...")
                            break_msg_looping = True
                            new_exists = False
                        
                        if (file_flag and new_exists):
                            os.rename(old_name, new_name)
                            print(new_name, ": is the new-Name of corresponding msg-id:", message.id)
                        elif new_exists:
                            print(message.id, ":was supposed to be re-Named to: ", new_name)
                            print("So STOPPING now... Check & Implement to catch FURTHER OLD-Names...")
                            break_msg_looping = True
                        else:
                            print(message.id, old_name, " : was supposed to be re-Named in this Last-Session...")
                            
                        print("Saving LAST-Stats to file last-message-id to help in Next-Run...")
                        with open('last-message-id', 'w') as f:
                            f.write(str(message.id))
                            f.write(" : Message-id of Last read msg-Chat \n")
                            f.write(str(eco_num))
                            f.write(" : Last-eco_num \n")
                            f.write(str(dm_num))
                            f.write(" : Last-dm_num \n")
                            f.write(str(whist_num))
                            f.write(" : Last-whist_num \n")
                            f.write(str(ans_num))
                            f.write(" : Last-ans_num \n")
                        break
                else:
                    print(message.id, message.date, "message doesn't have media")
            break
    log_withTime("END-Time Marked here...")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--help":
        print("Example: python main.py --api-id 12345 --api-hash 1ab1ab1ab1ab1ab --chat-title 'Bunker Reborn' --skip-until 123456")
        print("  --api-id and --api-hash you can generate your at https://my.telegram.org")
        print("  --skip-until is optional, should be a message.id, the code iterates over the messages from the newest to the oldest")
        exit()

    if len(sys.argv) < 7:
        print("Missing arguments, check --help")
        exit(1)

    if not (sys.argv[1] == "--api-id" and sys.argv[2] and sys.argv[3] == "--api-hash" and sys.argv[4]):
        print("Missing arguments --api-id and --api-hash (order can't differ from example in --help)")
        exit(1)

    api_id = sys.argv[2]
    api_hash = sys.argv[4]
    client = initialize(api_id, api_hash)

    if not (sys.argv[5] == "--chat-title" and sys.argv[6]):
        print("Missing argument --chat-title (order can't differ from example in --help)")
        exit(1)
    
    chat_title = sys.argv[6]

    skip_until = None
    if len(sys.argv) == 9 and sys.argv[7] == "--skip-until" and sys.argv[8]:
        skip_until = sys.argv[8]
           
    download_media(client, chat_title, skip_until)