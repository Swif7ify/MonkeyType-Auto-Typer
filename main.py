from bs4 import BeautifulSoup
import pyautogui
import keyboard
import time
import threading
import customtkinter as ctk
import subprocess
import random
from selenium import webdriver


def get_text_to_type(driver):
    time.sleep(0.5)
    src = driver.page_source
    soup = BeautifulSoup(src, "html.parser")

    div = soup.find_all("div", class_=["word"])
    text = ""

    for i in div:
        if "typed" not in i.get("class", []):
            text += i.text + " "
        else:
            continue
    return text.strip()


def get_timer_duration(driver):
    """Get the initial timer duration from the active button inside the time div"""
    try:
        src = driver.page_source
        soup = BeautifulSoup(src, "html.parser")
        
        time_div = soup.find("div", id="premidSecondsLeft")
        if time_div:
            duration_text = time_div.get_text().strip()
            print(f"Found timer duration: {duration_text} seconds")
            return int(duration_text)
        
        return None
    except Exception as e:
        print(f"Error getting timer duration: {e}")
        return None

def type_text(text):
    pyautogui.typewrite(text, interval=0.005)
    pyautogui.press("space")


stop_typing = False
typing_speed = 0.01 
driver = None
bot_running = False


class MonkeyTypeBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("MonkeyType Auto Typer")
        self.geometry("450x520")
        
        # Set up grid layout for responsive resizing
        self.grid_columnconfigure(0, weight=1)
        
        # Status label for displaying current bot state
        self.status_label = ctk.CTkLabel(self, text="Status: Ready", font=ctk.CTkFont(size=16, weight="bold"))
        self.status_label.grid(row=0, column=0, padx=20, pady=10)
        
        # Button to launch Chrome and open MonkeyType
        self.open_btn = ctk.CTkButton(
            self, text="Open Browser", command=self.open_browser,
            height=40, font=ctk.CTkFont(size=14)
        )
        self.open_btn.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        # Button to start the typing bot and listen for hotkey
        self.start_btn = ctk.CTkButton(
            self, text="Start Bot (Ctrl+Alt+T)", command=self.start_bot,
            height=40, font=ctk.CTkFont(size=14), state="disabled"
        )
        self.start_btn.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        # Button to stop the typing bot
        self.stop_btn = ctk.CTkButton(
            self, text="Stop Bot", command=self.stop_bot,
            height=40, font=ctk.CTkFont(size=14), state="disabled"
        )
        self.stop_btn.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        # Frame for typing speed controls
        self.speed_frame = ctk.CTkFrame(self)
        self.speed_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.speed_frame.grid_columnconfigure(1, weight=1)
        
        self.speed_label = ctk.CTkLabel(self.speed_frame, text="Typing Speed:", font=ctk.CTkFont(size=14))
        self.speed_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.speed_value_label = ctk.CTkLabel(self.speed_frame, text=f"{typing_speed:.3f}s", font=ctk.CTkFont(size=14))
        self.speed_value_label.grid(row=0, column=2, padx=10, pady=5)
        
        self.speed_slider = ctk.CTkSlider(
            self.speed_frame, from_=0.001, to=0.1, number_of_steps=99,
            command=self.update_speed
        )
        self.speed_slider.set(typing_speed)
        self.speed_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # Button to close all Chrome and chromedriver processes
        self.quit_btn = ctk.CTkButton(
            self, text="Quit All Browsers", command=self.quit_browsers,
            height=40, font=ctk.CTkFont(size=14), fg_color="red", hover_color="darkred"
        )
        self.quit_btn.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        
        # Frame for selecting typing mode (bot/human)
        self.mode_frame = ctk.CTkFrame(self)
        self.mode_frame.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        self.mode_frame.grid_columnconfigure(1, weight=1)
        
        self.mode_label = ctk.CTkLabel(self.mode_frame, text="Typing Mode:", font=ctk.CTkFont(size=14))
        self.mode_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.typing_mode = ctk.StringVar(value="bot")
        self.bot_radio = ctk.CTkRadioButton(self.mode_frame, text="Bot (Fast)", variable=self.typing_mode, value="bot")
        self.bot_radio.grid(row=0, column=1, padx=10, pady=5)
        
        self.human_radio = ctk.CTkRadioButton(self.mode_frame, text="Human (Natural)", variable=self.typing_mode, value="human")
        self.human_radio.grid(row=0, column=2, padx=10, pady=5)
        
        # Instructions section for user guidance
        self.info_label = ctk.CTkLabel(self, text="Instructions:", font=ctk.CTkFont(size=14, weight="bold"))
        self.info_label.grid(row=7, column=0, padx=20, pady=(10, 5))
        
        self.info_text = ctk.CTkTextbox(self, height=320, font=ctk.CTkFont(size=12))
        self.info_text.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.info_text.insert("1.0", 
            "1. Click 'Open Browser' to launch MonkeyType\n"
            "2. Click 'Start Bot' to begin listening\n"
            "3. Press Ctrl+Alt+T to start auto-typing\n"
            "4. Select Bot (fast) or Human (natural) mode\n"
            "5. Bot stops automatically when timer expires\n"
            "6. Use 'Stop Bot' to stop listening\n"
            "7. Use 'Quit All Browsers' to close Chrome"
        )
        self.info_text.configure(state="disabled")
        
        # Handle window close event for cleanup
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def update_status(self, message):
        self.status_label.configure(text=f"Status: {message}")
        self.update()
    
    def update_speed(self, value):
        global typing_speed
        typing_speed = float(value)
        self.speed_value_label.configure(text=f"{typing_speed:.3f}s")
    
    def open_browser(self):
        try:
            self.update_status("Opening browser...")
            
            def open_browser_thread():
                global driver
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_argument("--disable-infobars")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-logging")
                chrome_options.add_argument("--disable-gpu-logging")
                chrome_options.add_argument("--disable-extensions-logging")
                chrome_options.add_argument("--log-level=3")
                chrome_options.add_argument("--silent")
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--disable-features=VizDisplayCompositor")
                
                driver = webdriver.Chrome(options=chrome_options)
                driver.get("https://monkeytype.com/")
                
                self.after(0, lambda: self.update_status("Browser opened - Ready to start bot"))
                self.after(0, lambda: self.start_btn.configure(state="normal"))
                self.after(0, lambda: self.open_btn.configure(state="disabled"))
            
            threading.Thread(target=open_browser_thread, daemon=True).start()
            
        except Exception as e:
            self.update_status(f"Error opening browser: {str(e)}")
    
    def start_bot(self):
        global bot_running, driver
        if not driver:
            self.update_status("Please open browser first")
            return
        
        bot_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        # Start the bot logic in a background thread
        bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        bot_thread.start()
        
        self.update_status("Bot started - Press Ctrl+Alt+T to begin")
    
    def stop_bot(self):
        global bot_running, stop_typing
        bot_running = False
        stop_typing = True
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.update_status("Bot stopped")
    
    def quit_browsers(self):
        global driver, bot_running, stop_typing
        try:
            bot_running = False
            stop_typing = True
            
            if driver:
                driver.quit()
                driver = None
            
            # Kill all Chrome processes
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                         capture_output=True, shell=True)
            subprocess.run(["taskkill", "/f", "/im", "chromedriver.exe"], 
                         capture_output=True, shell=True)
            
            self.update_status("All browsers closed")
            self.open_btn.configure(state="normal")
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="disabled")
            
        except Exception as e:
            self.update_status(f"Error closing browsers: {str(e)}")
    
    def run_bot(self):
        global driver, bot_running, stop_typing
        first_run = True
        
        while bot_running:
            try:
                if first_run:
                    self.after(0, lambda: self.update_status("Waiting for Ctrl+Alt+T..."))
                    keyboard.wait("ctrl+alt+t")
                    first_run = False
                else:
                    self.after(0, lambda: self.update_status("Test finished! Press Ctrl+Alt+T for next"))
                    keyboard.wait("ctrl+alt+t")
                
                if not bot_running:
                    break
                
                self.after(0, lambda: self.update_status("Auto-typing started..."))
                stop_typing = False
                
                # Retrieve the typing test duration from the web page
                timer_duration = get_timer_duration(driver)
                if timer_duration is None:
                    timer_duration = 60
                
                start_time = time.time()
                
                # Start a background thread to monitor the timer
                timer_thread = threading.Thread(target=timer_monitor, args=(start_time, timer_duration), daemon=True)
                timer_thread.start()
                
                # Main typing loop: continue until timer expires or stopped
                while not stop_typing and bot_running:
                    text_to_type = get_text_to_type(driver)
                    
                    if text_to_type and not stop_typing and bot_running:
                        if self.typing_mode.get() == "human":
                            type_text_human(text_to_type)
                        else:
                            type_text_fast(text_to_type)
                        # Allow MonkeyType to update the word list after typing
                        time.sleep(0.1)
                    else:
                        if bot_running and not stop_typing:
                            # If no words are available, trigger MonkeyType to load more
                            print("No more words found, triggering new words...")
                            pyautogui.press("space")  # Simulate keypress to load more words
                            time.sleep(0.2)  # Wait for new words to appear
                            # Attempt to fetch and type new words
                            text_to_type = get_text_to_type(driver)
                            if text_to_type and not stop_typing and bot_running:
                                if self.typing_mode.get() == "human":
                                    type_text_human(text_to_type)
                                else:
                                    type_text_fast(text_to_type)
                            else:
                                # If still no words, wait before retrying
                                time.sleep(0.5)
                
            except Exception as e:
                self.after(0, lambda: self.update_status(f"Bot error: {str(e)}"))
                break
    
    def on_closing(self):
        global bot_running, stop_typing, driver
        bot_running = False
        stop_typing = True
        if driver:
            driver.quit()
        self.destroy()

def timer_monitor(start_time, timer_duration):
    """Background thread to monitor elapsed time and stop typing when timer expires."""
    global stop_typing
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= timer_duration:
            print(f"\nTimer finished ({timer_duration} seconds)! Stopping auto-type...")
            stop_typing = True
            break
        time.sleep(0.05)  # Check every 0.05 seconds for more responsive stopping


def type_text_human(text):
    """Simulate human typing with random delays and occasional pauses."""
    global stop_typing
    
    words = text.split()
    for word in words:
        if stop_typing:
            return
        # Type each character with a random delay to mimic human typing
        for char in word:
            if stop_typing:
                return
            pyautogui.write(char)
            # Random delay between keystrokes (5-15ms for natural typing)
            delay = random.uniform(0.005, 0.015)
            time.sleep(delay)
            # Occasionally pause longer to simulate human hesitation
            if random.random() < 0.02:
                time.sleep(random.uniform(0.2, 0.5))
        if not stop_typing:
            pyautogui.press("space")
            # Short pause between words for realism
            time.sleep(random.uniform(0.1, 0.3))


def type_text_fast(text):
    """Type text at maximum speed, checking for stop signal after each word."""
    global stop_typing
    
    words = text.split()
    for word in words:
        if stop_typing:
            return
        # Type the whole word quickly
        pyautogui.write(word, interval=typing_speed)
        # Check for stop signal after each word
        if stop_typing:
            return
        pyautogui.press("space")


def main():
    # Set CustomTkinter appearance
    ctk.set_appearance_mode("dark") 
    ctk.set_default_color_theme("blue")  
    
    # Create and run GUI
    app = MonkeyTypeBotGUI()
    app.mainloop()



if __name__ == "__main__":
    main()

