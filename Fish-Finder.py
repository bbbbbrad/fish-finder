import time, os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class fish_finder():
    def __init__(self):
        self.SPECIES = 'Brook Trout - Wild'
        self.RAN = 0
        self.FOLDER_PATH = 'C:\\Users\\bradr\\Documents\\Programming\\Fishing\\Stream\\Data'
        self.OUTPUT_FILE = 'output.csv'
        self.driver = None

    def setup_driver(self):
        options = FirefoxOptions()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", 'C:\\Users\\bradr\\Documents\\Programming\\Fishing\\Stream\\Data')
        self.driver = webdriver.Firefox(options=options)

    def search_for_species(self, species):
        self.driver.get('https://cteco.uconn.edu/projects/fish/viewer/index.html')
        self.driver.find_element(By.ID, 'TabSearch_tablist_SearchFishType').click()
        time.sleep(1)
        search_fish = self.driver.find_element(By.ID, 'cboFishType')
        search_fish.send_keys(species)
        time.sleep(1)
        search_fish.send_keys(Keys.ARROW_DOWN)
        search_fish.send_keys(Keys.ENTER)
        time.sleep(1)
        self.driver.find_element(By.ID, 'btnSearchFish_label').click()

    def download_data(self):
        streams = self.driver.find_elements(By.XPATH, '//*[@id="trunderline"]')
        for stream in streams:
            stream.click()
            self.RAN += 1
            time.sleep(1)
            self.driver.find_element(By.ID, 'fishDetail_button_title').click()
            time.sleep(2)
            self.driver.find_element(By.ID, 'fishDownload').click()
            print(' [+] Downloaded Stream ' + str(self.RAN) + ' Data...')
            time.sleep(2)
            self.driver.find_element(By.ID, 'filter_button_title').click()
            time.sleep(1)
        print(' [+] Sucessfully Downloaded All Stream Data!')

    def merge_csv_files(self):
        merged_df = pd.DataFrame()
        for filename in os.listdir(self.FOLDER_PATH):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.FOLDER_PATH, filename)
                df = pd.read_csv(file_path)
                merged_df = pd.concat([merged_df, df], ignore_index=True)
        merged_df.to_csv(self.OUTPUT_FILE, index=False)
        print(f" [+] Sucessfully Merged CSV files to {self.OUTPUT_FILE}")

    def sort_data(self):
        df = pd.read_csv(self.OUTPUT_FILE)
        df.sort_values([self.SPECIES], axis=0, ascending=[False], inplace=True)
        df.to_csv('data_sorted.csv', index=False)
        print(' [+] Sucessfully Sorted Data!')

    def run(self):
        self.setup_driver()
        print(f' [+] Searching for {self.SPECIES}')
        self.search_for_species(self.SPECIES)
        time.sleep(2)
        self.download_data()
        time.sleep(1)
        self.merge_csv_files()
        time.sleep(1)
        self.sort_data()
        
if __name__ == '__main__':
    try:
        os.system('cls')
        bot = fish_finder()
        bot.run()
    except KeyboardInterrupt:
        os.system('cls')