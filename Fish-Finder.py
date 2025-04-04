import os
import time
from pathlib import Path
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, WebDriverException
from contextlib import contextmanager

class FishFinder:
    def __init__(self):
        self.species = 'Brook Trout - Wild'
        self.download_count = 0
        self.folder_path = Path('C:/Users/bradr/Documents/Programming/Fishing/Stream/Data')
        self.output_file = 'output.csv'
        self.sorted_file = 'data_sorted.csv'
        self.driver = None
        self.wait_timeout = 10
        
        self.folder_path.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _webdriver_context(self):
        try:
            yield self._setup_driver()
        finally:
            if self.driver:
                self.driver.quit()

    def _setup_driver(self):
        options = FirefoxOptions()
        options.add_argument('--headless')
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", str(self.folder_path))
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

        try:
            return webdriver.Firefox(options=options)
        except WebDriverException as e:
            raise Exception(f"Failed to initialize WebDriver: {e}")

    def _wait_for_element(self, by, value, timeout=None):
        timeout = timeout or self.wait_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def search_for_species(self):
        self.driver.get('https://cteco.uconn.edu/projects/fish/viewer/index.html')
        
        try:
            self._wait_for_element(By.ID, 'TabSearch_tablist_SearchFishType').click()
            search_fish = self._wait_for_element(By.ID, 'cboFishType')
            search_fish.send_keys(self.species, Keys.ARROW_DOWN, Keys.ENTER)
            self._wait_for_element(By.ID, 'btnSearchFish_label').click()
        except TimeoutException as e:
            raise Exception(f"Search failed: {e}")

    def download_data(self):
        try:
            streams = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="trunderline"]'))
            )
            
            for i, stream in enumerate(streams, 1):
                try:
                    stream.click()
                    self.download_count += 1
                    
                    self._wait_for_element(By.ID, 'fishDetail_button_title').click()
                    self._wait_for_element(By.ID, 'fishDownload').click()
                    
                    time.sleep(0.5)
                    
                    self._wait_for_element(By.ID, 'filter_button_title').click()
                    print(f" [+] Downloaded Stream {self.download_count} Data...")
                except TimeoutException:
                    print(f" [!] Failed to download stream {i}. Skipping...")
                    continue
                    
            print(" [+] Successfully Downloaded All Stream Data!")
        except TimeoutException:
            print(" [!] Failed to locate streams.")

    def process_csv_files(self):
        csv_files = list(self.folder_path.glob('*.csv'))
        if not csv_files:
            print(" [!] No CSV files found to process.")
            return

        try:
            merged_df = pd.concat(
                (pd.read_csv(file, low_memory=False) for file in csv_files),
                ignore_index=True
            )
            
            merged_df.drop_duplicates(inplace=True)
            
            merged_df.to_csv(self.output_file, index=False)
            print(f" [+] Merged {len(csv_files)} CSV files to {self.output_file}")

            if self.species in merged_df.columns:
                merged_df.sort_values(by=[self.species], ascending=False, inplace=True)
                merged_df.to_csv(self.sorted_file, index=False)
                print(f" [+] Sorted data saved to {self.sorted_file}")
            else:
                print(f" [!] Column '{self.species}' not found in data.")

        except pd.errors.EmptyDataError:
            print(" [!] One or more CSV files were empty.")
        except Exception as e:
            print(f" [!] Error processing CSV files: {e}")

    def run(self):
        print(f" [+] Starting search for {self.species}...")
        try:
            with self._webdriver_context() as driver:
                self.driver = driver
                self.search_for_species()
                self.download_data()
                self.process_csv_files()
            print(" [+] Completed all tasks successfully.")
        except Exception as e:
            print(f" [!] Process failed: {e}")

if __name__ == '__main__':
    try:
        bot = FishFinder()
        bot.run()
    except KeyboardInterrupt:
        print("\n [!] Process interrupted by user.")
    except Exception as e:
        print(f" [!] Unexpected error: {e}")
