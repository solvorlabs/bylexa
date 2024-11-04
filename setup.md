# Setup Guide

## Introduction

Welcome to the setup guide for our project. This guide will help you install and run the application on your local machine. Follow the steps below to get started.

---

## Prerequisites

- **Node.js** and **npm** installed on your machine.
- **Python** installed (preferably Python 3.6 or higher).
- **pip** (Python package installer) installed.
- Access to the project repository.

---

## Installation Steps

### 1. Clone the Repository

Clone the project repository to your local machine using Git.

```bash
git clone <repository_url>
```

---

### 2. Install Server Dependencies

Navigate to the `server` directory and install the required npm packages.

```bash
cd server
npm install
```

---

### 3. Install Web User Dependencies

Navigate to the `web_user` directory and install the necessary npm packages.

```bash
cd ../web_user
npm install
```

---

### 4. Set Up Environment Variables

Both the `server` and `web_user` directories contain an `.env.example` file. You need to create a `.env` file in each directory.

#### For the Server

1. In the `server` directory:

   ```bash
   cp .env.example .env
   ```

2. Open the `.env` file and fill in the required keys and variables.

#### For the Web User Interface

1. In the `web_user` directory:

   ```bash
   cp .env.example .env
   ```

2. Open the `.env` file and fill in the necessary configuration details.

---

### 5. Run the Server

Start the development server by running the following command in the `server` directory:

```bash
npm run dev
```

---

### 6. Install the Python Client (`bylexa`)

Navigate to the `os_interaction` folder to install the `bylexa` Python client.

1. Change to the `os_interaction` directory:

   ```bash
   cd ../os_interaction
   ```

2. Install the `bylexa` package:

   ```bash
   pip install -e .
   ```

---

### 7. Login with `bylexa`

Use the credentials you created on the website to log in.

```bash
bylexa login
```

- You will be prompted to enter your **email** and **password**.

---

### 8. Start the Python Client

Start the `bylexa` client to connect with your backend server.

```bash
bylexa start
```

- **Note**: When prompted for a **room code**, simply press **Enter** to skip this step and avoid the room connection.

---

### 9. Test the Setup

With both the server and the Python client running, you can now test the application.

1. Open your web browser and navigate to the **website**.

2. Go to the **Python Client Manager** section.

3. From there, you can **send commands** to test the interaction between the server and your Python client.

---

## Additional Notes

- Ensure all services are running simultaneously:
  - The **server** (`npm run dev` in the `server` directory).
  - The **Python client** (`bylexa start` in the `os_interaction` directory).

- If you encounter any issues, check the terminal output for error messages and ensure all environment variables are correctly set.

---

## Contact Information

For further assistance, please contact **@exploring-solver (Aman)**.

---

# LICENSE

**Copyright © 2023 [@exploring-solver (Aman)]**

---

**All rights reserved.**

This software and associated documentation files (the "Software") are provided exclusively for **personal** and **educational** purposes.

- **Non-Commercial Use**: You may **not** use this Software for commercial purposes without explicit permission from the owner.

- **No Redistribution**: You may **not** distribute, modify, transmit, reuse, or repost the Software in any form without prior written permission from the owner.

---

For permissions or inquiries, please contact **@exploring-solver (Aman)**.

---

**Disclaimer**: This License does not grant you any rights to use the author's name, logo, or trademarks.

---

**Note**: Unauthorized use of this Software may violate copyright, trademark, and other laws.