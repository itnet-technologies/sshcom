import argparse
import ast
import os
import stat
import sys
import traceback
import paramiko
import time

import re
import colorama
try:
    def has_letters(input_string):
        return any(char.isalpha() for char in input_string)
    # Function to remove ANSI escape sequences (color codes)
    def remove_color_codes(text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    parser = argparse.ArgumentParser(description='sshcom')
    parser.add_argument('-ssh', '--ssh-commander', help='used when lauching commands', action=argparse.BooleanOptionalAction)
    parser.add_argument('-scp', '--scp-commander', help='used when sending file', action=argparse.BooleanOptionalAction)
    parser.add_argument('-sftp', '--sftp-commander', help='used when sending file', action=argparse.BooleanOptionalAction)
    parser.add_argument('-pu', '--push', help='used when sending file with sftp', action=argparse.BooleanOptionalAction)
    parser.add_argument('-g', '--get', help='used when getting file with sftp', action=argparse.BooleanOptionalAction)
    parser.add_argument('-ho', '--hostname', help='the hostname of the server')
    parser.add_argument('-u', '--username', help='the username of user in the server')
    parser.add_argument('-p', '--password', help='the password of user in the server')
    parser.add_argument('-c', '--command', help='the command to be executed')
    parser.add_argument('-sfo', '--source-folder', help='the folder we want to send or to receive. Note : this flag should be used with the flag -dfo too')
    parser.add_argument('-dfo', '--destination-folder', help='the path where we want to store the folder')
    parser.add_argument('-sf', '--source-file', help='the path of the file we want to send. (eg : /home/me1/files/source.pdf)\n\
                        --source-file can also accept multiple files (eg : ("/home/file1.txt", "/home/file2.txt") ) Note : this flag is required when using -sftp or -scp flag \n\
                        and if multiple file were provided multiple destinations too have to be provided or the flag --source-folder ')
    parser.add_argument('-df', '--destination-file', help=r'the full path for the file location. (eg : /home/me2/files/sent.pdf)\n\
                        --destination-file can also accept multiple destinations (eg : ("/home/file1.txt", "/home/file2.txt") ) Note : this flag is required when using -sftp or -scp flag \n\
                        and if multiple destination were provided multiple source file too have to be provided ')
    args = parser.parse_args()
    # SSH connection details
    # print(args)
    host = args.hostname
    port = 22
    username = args.username
    password = args.password
    command = args.command
    if args.ssh_commander is None and args.sftp_commander is None and args.scp_commander is None :
        # print("choose one protocol by using it's flag. (eg : -scp, -sftp or -ssh)")
        print(parser.print_help())
        sys.exit(1)
    dargs = {
        "hostname" : host,
        "username" : username,
        "password" : password,
        # "command" : command
    }
    dargs2 = {}
    for k,v in dargs.items():
        if v is None:
           dargs2[k] = input(f"{k} : ")
        else:
            dargs2[k] = v
    if args.sftp_commander:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(dargs2["hostname"], username=dargs2['username'], password=dargs2['password'])
        if (args.source_file is None and args.source_folder is None) or (args.destination_file is None and args.destination_folder is None) :
            # print("--source-file and --destination-file flag are required when using -sftp flag")
            print(parser.print_help())
            print(args)
            sys.exit(1)
        sftp = ssh.open_sftp()
        def and_the_dir_be(path):
            try:
                sftp.chdir(path)
            except IOError:
                sftp.mkdir(path)
                # and_the_dir_be(path)
        if args.push : 
            if args.source_folder is not None:
                if args.destination_folder is None:
                    print(parser.print_help())
                    sys.exit(1)
                fp = f"{args.destination_folder}/{args.source_folder.split('/')[-1]}".replace("//", "/")
                base_dir = ""
                for d in fp.split("/"):
                    base_dir += d + "/"
                    and_the_dir_be(base_dir)
                for root, dirs, files in os.walk(args.source_folder):
                    for directory in dirs:
                        remote_dir = os.path.join(fp, directory)
                        sftp.mkdir(remote_dir)  
                    for file in files:
                        local_path = os.path.join(root, file)
                        remote_path = os.path.join(fp, os.path.relpath(local_path, args.source_folder))
                        sftp.put(local_path, remote_path)
        if args.get : 
            if args.source_folder is not None:
                if args.destination_folder is None:
                    print(parser.print_help())
                    sys.exit(1)
                lst = args.source_folder.split("/")[-1]
                if lst == "":
                    lst = args.source_folder.split("/")[-2]
                fp = f'{args.destination_folder}/{lst}'.replace("//", "/")
                if not os.path.exists(fp):
                    os.makedirs(fp)
                def download_dir(remote_path, local_path):
                    for item in sftp.listdir_attr(remote_path):
                        remote_item = remote_path + "/" + item.filename
                        local_item = os.path.join(local_path, item.filename)

                        if stat.S_ISDIR(item.st_mode):
                            os.makedirs(local_item, exist_ok=True)
                            download_dir(remote_item, local_item)
                        else:
                            sftp.get(remote_item, local_item)

                download_dir(args.source_folder, fp)  
        if args.source_file is not None:
            if ("(" and ")") in args.source_file and (args.source_file[0] == "(" and args.source_file[-1] == ")"):
                file_list = ast.literal_eval(args.source_file)
                if args.destination_file is not None:  
                    if ("(" and ")") in args.destination_file and (args.destination_file[0] == "(" and args.destination_file[-1] == ")"):
                        destination_file_list = ast.literal_eval(args.destination_file)
                        for fdl in destination_file_list:
                            if args.get:
                                # print(args.destination_file.replace(args.destination_file.split("/")[-1], ""))
                                if not os.path.exists(fdl.replace(fdl.split("/")[-1], "")):
                                    os.makedirs(fdl.replace(fdl.split("/")[-1], ""))
                            if args.push :
                                base_dir = ""
                                for d in fdl.replace(fdl.split("/")[-1], "").split("/"):
                                    base_dir += d + "/"
                                    and_the_dir_be(base_dir) 
                elif args.destination_folder is not None:
                    destination_file_list = [f"{args.destination_folder}/{file.split('/')[-1]}" for file in file_list]
                    destination_file_list = [file.replace("//", "/") for file in destination_file_list]
                    if args.push :
                        base_dir = ""
                        for d in args.destination_folder.split("/"):
                            base_dir += d + "/"
                            and_the_dir_be(base_dir)   
                    if args.get:
                        # print(args.destination_file.replace(args.destination_file.split("/")[-1], ""))
                        if not os.path.exists(args.destination_folder):
                            os.makedirs(args.destination_folder)
                else:
                    print(parser.print_help())
                    sys.exit(1)
                if len(file_list) != len(destination_file_list):
                    print(parser.print_help())
                    sys.exit(1)
            else:
                file_list = [args.source_file]
                # print(22)
                if args.destination_file is not None:
                    # print(232)
                    destination_file_list = [args.destination_file]
                    if args.get:
                        # print(args.destination_file.replace(args.destination_file.split("/")[-1], ""))
                        if not os.path.exists(args.destination_file.replace(args.destination_file.split("/")[-1], "")):
                            os.makedirs(args.destination_file)
                    if args.push :
                        base_dir = ""
                        for d in args.destination_file.replace(args.destination_file.split("/")[-1], "").split("/"):
                            base_dir += d + "/"
                            and_the_dir_be(base_dir)          
                elif args.destination_folder is not None:
                    destination_file_list = [f"{args.destination_folder}/{file.split('/')[-1]}" for file in file_list]
                    destination_file_list = [file.replace("//", "/") for file in destination_file_list]
                    if args.get:
                        if args.destination_folder is not None:
                            if not os.path.exists(args.destination_folder):
                                os.makedirs(args.destination_folder)
                    if args.push :
                        print("ere22")
                        fp = args.destination_folder
                        print(fp)
                        base_dir = ""
                        print(fp.split("/"))
                        for d in fp.split("/"):
                            base_dir += d + "/"
                            and_the_dir_be(base_dir)
                else:
                    print(parser.print_help())
                    sys.exit(1)
            count = 0 
            for file in file_list:
                # print(file)
                # print(destination_file_list[count])
                if args.push:
                    sftp.put(file, destination_file_list[count])
                if args.get:
                    # print(destination_file_list[count])
                    # print(file)
                    sftp.get(file, destination_file_list[count])
                count += 1
        sftp.close()

        ssh.close()
    if args.scp_commander:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(dargs2["hostname"], username=dargs2['username'], password=dargs2['password'])
        if args.source_file is None or args.destination_file is None:
            # print("--source-file and --destination-file flag are required when using -scp flag")
            print(parser.print_help())
            sys.exit(1)
        sftp = ssh.open_sftp()
        if args.push:
            sftp.put(args.source_file, args.destination_file)
        if args.get:
            sftp.get(args.source_file, args.destination_file)
        sftp.close()

        ssh.close()
    if args.ssh_commander:
        dargs2["command"] = args.command
        if args.command is None :
            dargs2["command"] = input("command :")
        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(dargs2["hostname"], port, dargs2["username"], dargs2["password"])

        # Start an interactive shell
        shell = ssh.invoke_shell()

        # Send sudo su command
        shell.send(f'{dargs2["command"]}\n')
        time.sleep(1)  # Wait for the prompt
        output = ''
        while shell.recv_ready():
            output += shell.recv(1024).decode()
        # Initialize colorama to interpret color codes
        colorama.init()

        # Remove the color codes from the output
        cleaned_output = remove_color_codes(output)

        # Print the cleaned output
        print(output)
        # print(output)
        shell.close()
        ssh.close()
    # pyinstaller -F -n "sshcom" sshcom.py
except:
    # if args.ssh_commander is None and args.sftp_commander is None and args.scp_commander is None :
    #     sys.exit(1)
    # if args.source_file is None or args.destination_file is None:
    #     sys
    print(traceback.format_exc())
    
    print("an error occured")


