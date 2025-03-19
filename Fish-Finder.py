import os
import time
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class FishFinder:
    def __init__(self):
        self.SPECIES = 'Brook Trout - Wild'
        self.download_count = 0
        self.FOLDER_PATH = Path('C:/Users/bradr/Documents/Programming/Fishing/Stream/Data')
        self.OUTPUT_FILE = 'output.csv'
        self.driver = None

    def setup_driver(self):
        options = FirefoxOptions()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", str(self.FOLDER_PATH))
        
        try:
            self.driver = webdriver.Firefox(options=options)
        except Exception as e:
            print(f" [!] Error initializing WebDriver: {e}")
            exit(1)

    def search_for_species(self, species):
        self.driver.get('https://cteco.uconn.edu/projects/fish/viewer/index.html')
        
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'TabSearch_tablist_SearchFishType'))).click()
        search_fish = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'cboFishType')))
        
        search_fish.send_keys(species)
        search_fish.send_keys(Keys.ARROW_DOWN, Keys.ENTER)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'btnSearchFish_label'))).click()

    def download_data(self):
        streams = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="trunderline"]')))

        for stream in streams:
            stream.click()
            self.download_count += 1

            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'fishDetail_button_title'))).click()
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'fishDownload'))).click()

            print(f" [+] Downloaded Stream {self.download_count} Data...")

            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'filter_button_title'))).click()

        print(" [+] Successfully Downloaded All Stream Data!")

    def merge_csv_files(self):
        merged_df = pd.concat(
            (pd.read_csv(file) for file in self.FOLDER_PATH.glob('*.csv')),
            ignore_index=True
        )

        merged_df.to_csv(self.OUTPUT_FILE, index=False)
        print(f" [+] Successfully Merged CSV files to {self.OUTPUT_FILE}")

    def sort_data(self):
        df = pd.read_csv(self.OUTPUT_FILE)
        if self.SPECIES in df.columns:
            df.sort_values(by=[self.SPECIES], ascending=False, inplace=True)
            df.to_csv('data_sorted.csv', index=False)
            print(" [+] Successfully Sorted Data!")
        else:
            print(f" [!] Column '{self.SPECIES}' not found in data. Skipping sorting.")

    def run(self):
        self.setup_driver()
        print(f" [+] Searching for {self.SPECIES}...")
        self.search_for_species(self.SPECIES)
        self.download_data()
        self.merge_csv_files()
        self.sort_data()

        self.driver.quit()
        print(" [+] Completed all tasks.")

if __name__ == '__main__':
    try:
        bot = FishFinder()
        bot.run()
    except KeyboardInterrupt:
        print("\n [!] Process interrupted by user.")
    except Exception as e:
        print(f" [!] Unexpected error: {e}")
