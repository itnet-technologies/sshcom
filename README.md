# SSHCom.py - Remote Server Management Script

SSHCom.py is a Python script that allows users to perform various actions on remote servers using SSH. This script provides a simple and intuitive command-line interface to execute commands on a remote server, transfer files using SFTP or SCP, and download files from the remote server.

## Prerequisites

Before using SSHCom.py, make sure you have the following prerequisites installed:

- Python 3.x: You can download Python from the official website (https://www.python.org/downloads/) and follow the installation instructions for your operating system.

## Getting Started

1. Clone the repository:
git clone <repository-url>
cd SSHCom

2. Install the required dependencies:
pip install -r requirements.txt

3. Usage:

## Usage

SSHCom.py supports the following command-line options:

- `-ssh`, `--ssh-commander`: Execute a command on the remote server. (Requires `-ho`, `-u`, `-p`, and `-c` flags)

- `-scp`, `--scp-commander`: Transfer files to the remote server using SCP. (Requires `-ho`, `-u`, `-p`, `-sf`, and `-df` flags)

- `-sftp`, `--sftp-commander`: Transfer files to the remote server using SFTP. (Requires `-ho`, `-u`, `-p`, `-sf`, and `-df` flags)

- `-pu`, `--push`: Alias for `-sftp` command. Transfer files to the remote server using SFTP.

- `-g`, `--get`: Download files from the remote server using SFTP. (Requires `-ho`, `-u`, `-p`, `-sf`, and `-df` flags)

- `-ho`, `--hostname`: The hostname or IP address of the remote server.

- `-u`, `--username`: The username for authentication on the remote server.

- `-p`, `--password`: The password for authentication on the remote server.

- `-c`, `--command`: The command to be executed on the remote server.

- `-sf`, `--source-file`: The path of the file(s) to transfer or download.

- `-df`, `--destination-file`: The destination path for file transfer or download.

- `-sfo`, `--source-folder`: The folder path to transfer or download multiple files.

- `-dfo`, `--destination-folder`: The destination folder path for multiple file transfers.

## Examples

1. Run a command on the remote server:
python sshcom.py -ssh -ho <hostname> -u <username> -p <password> -c "ls -al"

2. Transfer a file to the remote server using SCP:
python sshcom.py -scp -ho <hostname> -u <username> -p <password> -sf <local-file-path> -df <remote-destination>


3. Transfer a file to the remote server using SFTP:
python sshcom.py -sftp -ho <hostname> -u <username> -p <password> -sf <local-file-path> -df <remote-destination>


4. Download a file from the remote server using SFTP:
python sshcom.py -get -ho <hostname> -u <username> -p <password> -sf <remote-file-path> -df <local-destination>


## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Acknowledgments

The SSHCom.py script was inspired by the need to simplify remote server management tasks and was developed using the Paramiko library.

If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request. We welcome your contributions!
