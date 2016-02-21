# smscenter
Turn the Raspberry Pi into a SMS center using Python

http://hristoborisov.com/index.php/projects/turning-the-raspberry-pi-into-a-sms-center-using-python/

notes:
	Now I use the sshpass program to give the password to ssh. This is necessary because host cannot be anticipated in advance to set public keys acordingly.
	The command looks like: sshpass -p "password" ssh -nNT -R 8080:localhost:22 user@host
