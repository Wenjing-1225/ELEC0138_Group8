# ELEC0138 Group 8 – Security and Privacy challenges in a File Upload App

## Overview

This project aims to analyze and address Security and Privacy challenges in a web-based app (File Upload App) by applying threat modeling and mitigation methods. 

Several cyber attacks targeting common vulnerabilities are designed and implemented. Also, relevant mitigation measures are presented.

A vedio presentation of this project can be seen:


## Group Members

- Wenjing Hu
- Zoe Qian
- Andreas Tyrovolas


## Features

ELEC0138_Group8/
├── Attack/            # Contains different attacks and relevant mitigation methods
├── static/            # Functions of uploading documents
├── templates/         # HTML templates for the web interface
├── environment.yml    # Conda environment definition
├── initialize_db.py   # Script to initialize the database
├── requirements.txt   # Python package dependencies
└── system.py          # Main application script



## Installation

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
   python system.py
   ```


   The web interface should now be accessible at `http://localhost:5000/`.


