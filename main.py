import sys, os, time
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetAllChatsRequest
from telethon import errors
from datetime import datetime
import glob

# Printing download progress
def callback(current, total):
    with open(".config/data_log", "w") as file:
        file.write(str(current))
    global count_called; global bytes_old; global no_change; global no_change2; global total_called
    total_called += 1
    if count_called > 700:
        print('Downloaded', current, 'out of', total, 'bytes: {:.2%}'.format(current / total))
        print("Calling_Count is = ", count_called)
        count_called = 0
    else:
        count_called += 1
    if bytes_old < current:
        bytes_old = current
        no_change = 0
        no_change2 = 0
    else:
        no_change += 1
        no_change2 += 1
    if no_change > 300:
        log_withTime("[CALLBACK] [BREAK] Download HANGED since last 300-Call !! Let-break & re-Start...")
        no_change = 0
        log_withTime("[CALLBACK] [BREAK] [EXIT] Calling Exit & re-Execute through atexit-Modlue...")
        exit()
    if no_change2 > 5:
        no_change2 = 0
        log_withTime("Download-Progress looks stucked in last 5-calls !!!")
        print("Current Value of no_change is: "+ str(no_change) + " & of no_change2 is: " + str(no_change2))

def clean_broken_downloads():
    for file in glob.glob('downloaded_media/master*'):
        print("Deleting file: ", file)
        os.remove(file)
    for file in glob.glob('downloaded_media/manifest*'):
        print("Deleting file: ", file)
        os.remove(file)

def log_withTime(message=None, msg_id=None):
    timeStamp = datetime.now().strftime("%d-%b %H:%M:%S")
    if msg_id:
        print("[ERROR] " + timeStamp + " id: " + str(msg_id) + ' : ' + message)
    else:
        print("[INFO] " + timeStamp + ' : ' + message)

def loop_whole_process():
    global client2
    print("[EXEC] Disconnecting Client First to avoid -sqLite-db-lock issues...")
    client2.disconnect()
    print("[EXEC] Client Disconnected... Now Speeping for 180-Seconds to cool tele-server !!!")
    time.sleep(180)
    print("[EXEC] after-sleep, Now Clearing orphaned-downloads...")
    clean_broken_downloads()
    log_withTime("Done with Clearing, Will re-Execute NOW....Watch...")
    with open('.config/api_details') as f:
        lines = f.read().splitlines()
        chat_title = lines[2]
    client2.start()
    print("[EXEC] Client Connected Back...")
    file = open('.config/last_parameters')
    lines = file.readlines()
    skip_until = lines[0].split()[0]
    file.close()
    print("[INFO] skip_until: As per .config/last_parameters file data SET to: ", skip_until)
    print("[EXEC] Passing controll to MAIN-download_media finally...")
    download_media(client2, chat_title, skip_until)

def initialize(api_id, api_hash):
    try:
        os.mkdir('downloaded_media')
    except:
        pass
    client = TelegramClient('media_downloader', api_id, api_hash)
    client.start()
    return client

def download_media(client, chat_title, skip_until=None):
    global client2
    client2 = client
    log_withTime("START-Time Marked here...")
    print("Reading the data-stats from File-NOW...")
    with open('.config/last_parameters') as f:
        lines = f.read().splitlines()
        art_num = int(lines[1].split()[0])
        amhienv_num = int(lines[2].split()[0])
        env_num = int(lines[3].split()[0])
        ethics_num = int(lines[4].split()[0])
        recam_num = int(lines[5].split()[0])
        polity_num = int(lines[6].split()[0])
    log_withTime("Below are the Collected-DATA. Cross check with file if NOT-okay break me in 60-seconds!!!")
    print(art_num, amhienv_num, env_num, ethics_num, recam_num, polity_num)
    time.sleep(60)
    print("Will Continue now, With this data. Watch me!!")
    break_msg_looping = False
    re_Do_All = False
    dir_path = "downloaded_media/"
    chats = client(GetAllChatsRequest(except_ids=[]))
    chat_found = False
    for _, chat in enumerate(chats.chats):
        if chat.title == chat_title:
            chat_found = True
            print("found chat with title", chat_title)
            print('attemping to iterate over messages to download media')
            skip_until = skip_until and int(skip_until)
            for message in client.iter_messages(chat, offset_id=skip_until):
                if break_msg_looping:
                    break
                if message.media:
                    if art_num > 0:
                        lect_Name = "Art_And_Culture"
                        lect_Num = art_num
                        art_num = art_num - 1
                    elif amhienv_num > 0:
                        lect_Name = "Ancient_And_Medival_History"
                        lect_Num = amhienv_num
                        amhienv_num = amhienv_num - 1
                    elif env_num > 0:
                        lect_Name = "Environment_Ecology"
                        lect_Num = env_num
                        env_num = env_num - 1
                    elif ethics_num > 0:
                        lect_Name = "Ethics"
                        lect_Num = ethics_num
                        ethics_num = ethics_num - 1
                    elif recam_num > 0:
                        lect_Name = "Recorded_Ancient_And_Medival"
                        lect_Num = recam_num
                        recam_num = recam_num - 1
                    elif polity_num > 0:
                        lect_Name = "Polity"
                        lect_Num = polity_num
                        polity_num = polity_num - 1
                    else:
                        print("No Pre-Defined naming-Counter remaining-now... STOPPING here and Implement for MORE...")
                        print("[STOPPED] at current media with msg-id: ", message.id)
                        break
                    new_name = dir_path + lect_Name + "_Lecture_" + str(lect_Num) + ".mp4"
                    while True:
                        print(message.id, message.date, "message has media, downloading")
                        global count_called; global bytes_old; global no_change; global no_change2; global total_called
                        log_withTime("Clearing flags of COUNTS to be used inside-CALLBACK function!!!!")
                        count_called = 0; bytes_old = 0; no_change = 0; no_change2 = 0; total_called = 0
                        try:
                            down_path = client.download_media(message, file='downloaded_media', progress_callback=callback)
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
                            break
                        except Exception as e:
                            print(message.id, message.date, "failed to download media")
                            log_withTime("Some Un-Handled Exception occured", message.id)
                            raise e
                        media_size = round(message.file.size/1024/1024)
                        print("[COUNTS] THIS media had byte-Size:= ", media_size, "And total_called was:=", total_called)
                        print(message.id, message.date, "media downloaded, waiting 10 seconds before the next one")
                        time.sleep(10)
                        log_withTime("Now moving OR renaming file if mainifest OR master-name...")
                        os.rename(down_path, new_name)
                        print(new_name, ": is the new-Name of corresponding msg-id:", message.id)
                        print("Saving LAST-Stats to file .config/last_parameters to help in Next-Run...")
                        with open('.config/last_parameters', 'w') as f:
                            f.write(str(message.id))
                            f.write(" : Message-id of Last read msg-Chat \n")
                            f.write(str(art_num))
                            f.write(" : Last-art_num \n")
                            f.write(str(amhienv_num))
                            f.write(" : Last-amhienv_num \n")
                            f.write(str(env_num))
                            f.write(" : Last-env_num \n")
                            f.write(str(ethics_num))
                            f.write(" : Last-ethics_num \n")
                            f.write(str(recam_num))
                            f.write(" : Last-recam_num \n")
                            f.write(str(polity_num))
                            f.write(" : Last-polity_num \n")
                        break
                else:
                    print(message.id, message.date, "message doesn't have media")
            break
    if not chat_found:
        log_withTime("Given Chat is NOT Found !! Pls cross check it...")
    if re_Do_All:
        log_withTime("Flag found to be TRUE for re-Executing self-Fully...")
        print("[EXEC] Now Calling the -loop_whole_process- part...")
        loop_whole_process()
    else:
        log_withTime("END-Time Marked here...")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--fileconfig":
        log_withTime("[Starting with File_Based configs stored locally...")
        print("Fetching parameters from config-file...")
        with open('.config/api_details') as f:
            lines = f.read().splitlines()
            api_id = int(lines[0].split()[0])
            api_hash = lines[1].split()[0]
            chat_title = lines[2]
        file = open('.config/last_parameters')
        lines = file.readlines()
        skip_until = lines[0].split()[0]
        file.close()
        print("Clearing any broken downloads...")
        clean_broken_downloads()
        client = initialize(api_id, api_hash)
        print("[INFO] skip_until: As per .config/last_parameters file data SET to: ", skip_until)
        print("Giving control to main download_media-Fun...")

    else:
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