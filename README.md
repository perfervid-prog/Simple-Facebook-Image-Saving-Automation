# FB Image Saver Pro 📸

A powerful and flexible Facebook image automation tool that allows you to save entire photo galleries with ease. Featuring both a non-intrusive **Basic Mode** (GUI-assisted manual saving) and a fully automated **Pro Mode** (Playwright-driven background saving).

## ✨ Features

- **🚀 Pro Mode (Browser Driven)**
  - Fully automated gallery traversal using Playwright.
  - Automatically handles Facebook's "+X" image grids.
  - Detects the end of a gallery or circular loops to prevent infinite scrolling.
  - Works with persistent browser profiles (log in once, stay logged in).
- **🖱️ Basic Mode (Manual Focus)**
  - Uses PyAutoGUI for non-intrusive automation.
  - Great for saving a specific number of images from any open browser window.
  - Custom delay and naming controls.
- **🎨 Modern UI**
  - Sleek dark-mode interface built with `customtkinter`.
  - Real-time progress tracking and console logs.
  - Remembers your favorite save folders.

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/perfervid-prog/Simple-Facebook-Image-Saving-Automation.git
   cd Simple-Facebook-Image-Saving-Automation
   ```

2. **Create a virtual environment (Optional but Recommended):**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers (Required for Pro Mode):**
   ```bash
   playwright install chromium
   ```

## 🚀 Usage

### Running the App
Execute the main script or use the provided batch file:
```bash
python main.py
```
Or simply run `run_saver.bat` on Windows.

### Mode Breakdown
- **Basic Mode**: Point your mouse at the first image in your browser gallery, click "RUN BASIC AUTO", and wait 5 seconds. The script will take over and use keyboard shortcuts to save images sequentially.
- **Pro Mode**: Paste a Facebook post URL (or leave it blank to start from your feed), click "RUN PRO AUTO". A browser window will open. Once you are in theater mode (viewing a photo), the script will automatically detect the gallery and save everything.

## 📦 Project Structure

- `main.py`: Entry point for the application.
- `ui.py`: CustomTkinter-based GUI implementation.
- `browser_engine.py`: Pro Mode logic using Playwright.
- `fb_post_image_saver.py`: Basic Mode logic using PyAutoGUI.
- `requirements.txt`: Python dependencies.

## ⚠️ Disclaimer
This tool is for personal use and educational purposes only. Please respect Facebook's Terms of Service and the privacy of other users.

## 🤝 Contributing
Feel free to fork the project and midify it as you like. Pull requests are welcome!
