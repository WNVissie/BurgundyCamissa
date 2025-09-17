# How to Install and Test the Employee Shift Roster App on a Mac

## 1. Unzip the App

- Download the zip file to your Mac.
- Double-click the zip file to extract it.
- You will see a folder called `employee-shift-roster-app` (or similar).

---

## 2. Install Prerequisites

- Open the **Terminal** app (find it in Applications > Utilities).
- Type the following and press Enter to install Homebrew (if not already installed):

  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```

- Install Python and Node.js:

  ```bash
  brew install python@3.11 node
  ```

---

## 3. Set Up the Backend

- In Terminal, go to the backend folder:

  ```bash
  cd ~/Downloads/employee-shift-roster-app/shift-roster-backend
  ```

- Create and activate a Python environment:

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- Install backend requirements:

  ```bash
  pip install -r requirements.txt
  ```

- Start the backend server:

  ```bash
  flask run
  ```

  The backend will start and show a message like:
  ```
  * Running on http://127.0.0.1:5000/
  ```

---

## 4. Set Up the Frontend

- Open a new Terminal window.
- Go to the frontend folder:

  ```bash
  cd ~/Downloads/employee-shift-roster-app/shift-roster-frontend
  ```

- Install frontend dependencies:

  ```bash
  npm install
  ```

- Start the frontend app:

  ```bash
  npm start
  ```

  The app will open in your browser (usually at [http://localhost:3000](http://localhost:3000)).

---

## 5. Test the App

- Open your browser and go to [http://localhost:3000](http://localhost:3000).
- Log in and test the features as described in the user guide.

---

## 6. Stop the App

- To stop the backend or frontend, go to the Terminal window and press `Control + C`.

---

## Troubleshooting

- If you have any issues, contact your system administrator or refer to the user guide included in the app folder.

---

## Summary

Unzip, install Python/Node, run backend and frontend, test in browser.
No coding required!