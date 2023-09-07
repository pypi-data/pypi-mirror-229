import torch
import speedster
# from pruna_engine.models.stable_diffusion_controlnet.load_model import load_sd_controlnet_model
# from pruna_engine.models.clip.load_model import load_clip, load_tokenizer
from pruna_engine.PrunaModel import PrunaModel

# Encryption
import os
import zipfile
import struct
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import tempfile
import shutil

# Define the model loading functions for various model types
model_loaders = [
    ('torch', torch.load),
    ('standard', speedster.load_model),
    # ('clip', load_clip),
    # ('controlnet', load_sd_controlnet_model),
]


def load_model(model_path, api_key, verify_url='http://johnrachwan.pythonanywhere.com/verify'):
    """
    Function to load an encrypted model.

    Args:
        model_path (str): The path of the model to load.
        api_key (str): The API key for the PrunaModel.
        verify_url (str, optional): The verification URL for the PrunaModel. Defaults to
            'http://johnrachwan.pythonanywhere.com/verify'.

    Raises:
        ValueError: If no model can be loaded with any of the defined loaders.
        FileNotFoundError: If the model file does not exist.

    Returns:
        PrunaModel: The loaded model.
    """
    # TODO: Handle secret key management
    temp_path = decrypt(model_path)

    # Reorder the loaders based on the model_path
    # reordered_model_loaders = sorted(model_loaders, key=lambda x: x[0] in model_path, reverse=True)

    model = None
    for loader_name, loader_func in model_loaders:
        try:
            model = loader_func(temp_path)
            model = PrunaModel(model, api_key=api_key, verify_url=verify_url)
            break
        except Exception as e:
            pass
            # print(f"Failed to load model with {loader_name}: {e}")

    # Clean up temporary path
    shutil.rmtree(temp_path)

    if model is None:
        raise ValueError("Could not load model with any of the provided loaders.")
    else:
        print("Model loaded successfully")

    return model


def create_zip_folder(directory):
    # Create a zip file for the directory
    zipf = zipfile.ZipFile(directory + '.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(directory):
        for file in files:
            # This will place files at the root of the zip file, i.e., it will not include the top directory
            zipf.write(os.path.join(root, file), arcname=file)
    zipf.close()
    return directory + '.zip'


def encrypt(filename, key=b'secret'):
    chunksize = 64 * 1024
    outfile = filename + ".enc"
    filesize = os.path.getsize(filename)
    IV = Random.new().read(16)

    encryptor = AES.new(getKey(key), AES.MODE_CBC, IV)

    with open(filename, 'rb') as infile:
        with open(outfile, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(IV)

            while True:
                chunk = infile.read(chunksize)

                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

    # Delete the zip file after encrypting it
    os.remove(filename)


def decrypt(filename, key=b'secret'):
    chunksize = 24 * 1024

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    outfile_path = os.path.join(temp_dir, os.path.basename(filename[:-4]))  # The path of the decrypted zip file

    with open(filename, 'rb') as infile:
        filesize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        IV = infile.read(16)

        decryptor = AES.new(getKey(key), AES.MODE_CBC, IV)

        with open(outfile_path, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break

                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(filesize)

    # Unzip the file to the temporary directory
    with zipfile.ZipFile(outfile_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Delete the decrypted zip file
    os.remove(outfile_path)

    # Return the temporary directory
    return temp_dir


def getKey(password):
    hasher = SHA256.new(password)
    return hasher.digest()
