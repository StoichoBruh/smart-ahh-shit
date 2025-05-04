# USB Encryptor Tool

A Python-based tool designed to encrypt and manage external drives. The program allows users to securely format drives, set up encryption with a password, and create complex folder structures. It also enables users to access secured folders by entering the correct password.

## Features

- **Drive Selection**: Choose a drive or folder to work with.
- **Password Setup and Verification**:
  - If no password is found, users are prompted to set a new password.
  - If a password is already set, users are asked to enter the password. If correct, the tool unlocks the secured folder.
- **Drive Formatting**: Format the selected drive, removing all existing files and folders.
- **Folder Creation**: Generate a random folder structure with multiple levels of nested directories.
- **Password and Folder Path Storage**: The program securely stores the encryption password and folder path in hidden text files on the drive.
- **Log Generation**: A log of all actions is generated and can be saved for later review.

## How It Works

1. **Drive Selection**: 
   - Select the drive or folder you want to encrypt.
   
2. **Password Setup/Verification**:
   - If no password exists on the drive, you will be prompted to set one.
   - If a password exists, enter it to access the secured folder. If the entered password is correct, the folder path stored on the drive will be opened. If incorrect, an error message will appear.

3. **Drive Formatting**: 
   - If you choose to format the drive, all files and folders will be removed from the drive to ensure it's clean and ready for encryption.

4. **Folder Creation**:
   - The tool will generate random folder names and create a hierarchical folder structure with multiple levels.

5. **Password and Folder Path Storage**:
   - The encryption password and the folder path will be stored in hidden text files on the drive for secure retrieval.

6. **Encryption Completion**:
   - Once the setup is complete, the encryption is active, and a log is available to review what actions were performed.
   
7. **Accessing Secure Folder**:
   - After entering the correct password, users can access the secured folder.
required libraries:
pip install psutil

