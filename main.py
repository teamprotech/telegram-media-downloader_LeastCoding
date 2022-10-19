import sys, os, time
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetAllChatsRequest
from telethon import errors
from datetime import datetime
import glob

def log_withTime(message=None, msg_id=None):
    timeStamp = datetime.now().strftime("%d-%b %H:%M:%S")
    if msg_id:
        print("[ERROR] " + timeStamp + " id: " + str(msg_id) + ' : ' + message)
    else:
        print("[INFO] " + timeStamp + ' : ' + message)

def loop_whole_process():
    with open('.config/api-details') as f:
        lines = f.read().splitlines()
        api_id = lines[0].split()[0]
        api_hash = lines[1].split()[0]
        chat_title = lines[2]
    client = initialize(api_id, api_hash)
    print("[EXEC] Client Connected Back...")
    file = open('last-message-id')
    lines = file.readlines()
    skip_until = lines[0].split()[0]
    file.close()
    print("[INFO] skip_until: As per last-message-id file data SET to: ", skip_until)
    print("[EXEC] Passing controll to MAIN-download_media finally...")
    download_media(client, chat_title, skip_until)

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
        sec_num = int(lines[1].split()[0])
        ir_num = int(lines[2].split()[0])
        st_num = int(lines[3].split()[0])
        bs_num = int(lines[4].split()[0])
        modhist_num = int(lines[5].split()[0])
        maps_num = int(lines[6].split()[0])
        geo_num = int(lines[7].split()[0])
    log_withTime("Below are the Collected-DATA. Cross check with file if NOT-okay break me in 60-seconds!!!")
    print(sec_num, ir_num, st_num, bs_num, modhist_num, maps_num, geo_num)
    time.sleep(60)
    print("Will Continue now, With this data. Watch me!!")
    break_msg_looping = False
    re_Do_All = False
    dir_path = "downloaded_media/"
    chats = client(GetAllChatsRequest(except_ids=[]))
    for _, chat in enumerate(chats.chats):
        if chat.title == chat_title:
            print("found chat with title", chat_title)
            print('attemping to iterate over messages to download media')
            skip_until = skip_until and int(skip_until)
            for message in client.iter_messages(chat, offset_id=skip_until):
                if break_msg_looping:
                    break
                if sec_num > 3:
                    lect_Name = "Security"
                    lect_Num = sec_num
                    sec_num = sec_num - 1
                elif ir_num > 0:
                    lect_Name = "International_Relations"
                    lect_Num = ir_num
                    ir_num = ir_num - 1
                elif st_num > 0:
                    lect_Name = "Science_Tech"
                    lect_Num = st_num
                    st_num = st_num - 1
                elif bs_num > 0:
                    lect_Name = "Basic_Science"
                    lect_Num = bs_num
                    bs_num = bs_num - 1
                elif modhist_num > 0:
                    lect_Name = "Modern_History"
                    lect_Num = modhist_num
                    modhist_num = modhist_num - 1
                elif maps_num > 0:
                    lect_Name = "Mapping"
                    lect_Num = maps_num
                    maps_num = maps_num - 1
                elif geo_num > 0:
                    lect_Name = "Geography_GS"
                    lect_Num = geo_num
                    geo_num = geo_num -1
                else:
                    print("No Pre-Defined naming-Counter remaining-now... STOPPING here and Implement for MORE...")
                    print("[STOPPED] at current media with msg-id: ", message.id)
                    break
                new_name = dir_path + lect_Name + "_Lecture_" + str(lect_Num) + ".mp4"

                if message.media:
                    while True:
                        print(message.id, message.date, "message has media, downloading")
                        try:
                            down_path = client.download_media(message, file='downloaded_media')
                        except errors.FloodWaitError as e:
                            log_withTime("Failed to download THIS-Media...", message.id)
                            print(message.id, message.date, "failed to download media: flood wait error, were asked to wait for", e.seconds, " but will be waiting for", e.seconds + 120)
                            time.sleep(e.seconds + 120)
                            continue
                        except errors.FileReferenceExpiredError as err:
                            log_withTime("Failed to download This-media: FileReferenceExpiredError has occured...", message.id)
                            print("Type is: ", type(err))
                            print("Message is: ", err)
                            print("[EXEC] Setting Flags to re-Execute")
                            re_Do_All = True
                            break_msg_looping = True
                            print("[EXEC] Clearing orphaned-downloads...")
                            for file in glob.glob('downloaded_media/master*'):
                                print("Deleting file: ", file)
                                os.remove(file)
                            for file in glob.glob('downloaded_media/manifest*'):
                                print("Deleting file: ", file)
                                os.remove(file)
                            print("Done with Clearing, Will re-Execute NOW....Watch...")
                            break
                        except Exception as e:
                            print(message.id, message.date, "failed to download media")
                            log_withTime("Some Un-Handled Exception occured", message.id)
                            raise e
                        print(message.id, message.date, "media downloaded, waiting 10 seconds before the next one")
                        time.sleep(10)
                        log_withTime("Now moving OR renaming file if mainifest OR master-name...")
                        os.rename(down_path, new_name)
                        print(new_name, ": is the new-Name of corresponding msg-id:", message.id)
                        print("Saving LAST-Stats to file last-message-id to help in Next-Run...")
                        with open('last-message-id', 'w') as f:
                            f.write(str(message.id))
                            f.write(" : Message-id of Last read msg-Chat \n")
                            f.write(str(sec_num))
                            f.write(" : Last-sec_num \n")
                            f.write(str(ir_num))
                            f.write(" : Last-ir_num \n")
                            f.write(str(st_num))
                            f.write(" : Last-st_num \n")
                            f.write(str(bs_num))
                            f.write(" : Last-bs_num \n")
                            f.write(str(modhist_num))
                            f.write(" : Last-modhist_num \n")
                            f.write(str(maps_num))
                            f.write(" : Last-maps_num \n")
                            f.write(str(geo_num))
                            f.write(" : Last-geo_num \n")
                        break
                else:
                    print(message.id, message.date, "message doesn't have media")
            break
    if re_Do_All:
        log_withTime("Flag found to be TRUE for re-Executing self-Fully...")
        print("[EXEC] Disconnecting Client First to avoid -sqLite-db-lock issues...")
        client.disconnect()
        print("[EXEC] Client Disconnected... Now Speeping for 180-Seconds to cool tele-server !!!")
        time.sleep(180)
        print("[EXEC] Now Calling the -loop_whole_process- part...")
        loop_whole_process()
    else:
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