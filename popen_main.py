import os, time
import sys
import subprocess

print("[PARENT] [START] Main file started now...")
print("[PARENT] Doing initial setup and First-Time startup of Child..")

old_data = 0
n = 0
nochange_count = 0
child_exited_normally = False

print("[PARENT] [BEFORE-CALL] STARTING-Child... Now Will loop & check every 180-Seconds")
child_proc = subprocess.Popen(["python", "main.py", "--fileconfig"])
print("[PARENT] [AFTER-CALL] Child-Statred with proc-pid: = ", child_proc.pid)


while True:
	if child_exited_normally:
		print("[PARENT] Child closed clean on its own. So terminating my-self !!!")
		break
	if nochange_count > 4:
		print("[PARENT] [HANGED??] Still data Not-Changed since last 5-checks.or 15-Minutes or 900-Seconds..NO-CHANGE")
		print("[PARENT] Need to work on Child & restart it !!!!")
		nochange_count = 0
		n = 60
		while True:
			child_exit_staus = child_proc.poll()
			if child_exit_staus == 0:
				print("[PARENT] Child completed Normally with Exit-Status:", child_exit_staus)
				child_exited_normally = True
				break
			elif child_exit_staus == None:
				print("[PARENT] Child is live... with status -const_None is: = ", child_exit_staus)
				print("[PARENT] Killing Child now...for Fresh-Start...")
				child_proc.terminate()
				time.sleep(2)
			else:
				print("[PARENT] Child terminated with Status: = ", child_exit_staus)
				print("[PARENT] [BEFORE-CALL] Sleeping for further 240-Seconds...BEFORE...Re-Starting child-AGAIN...")
				time.sleep(240)
				child_proc = subprocess.Popen(["python", "main.py", "--fileconfig"])
				print("[PARENT] [AFTER-CALL] Child-Statred with proc-pid: = ", child_proc.pid)
				break
	else:
		#print("[PARENT] Data is Changing... So wait in my Loop...")
		n = 0

	#print("[PARENT] [SLEEP] Waiting this time for Seconds =: ", n + 20)
	time.sleep(180 + n)
	#print("[PARENT] [WAKE] Reading data_log for changes...")
	with open('data_log') as file:
		lines = file.read().splitlines()
		new_data = int(lines[0].split()[0])
	if old_data == new_data:
		nochange_count += 1
	else:
		nochange_count = 0

	old_data = new_data

print("[PARENT] [END] Main Ends here...")
