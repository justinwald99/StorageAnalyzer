import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import matplotlib.pyplot as plt

from interactions_module import ebay_interaction

# Configure Chrome options for incognito mode
chrome_options = Options()
chrome_options.add_argument("--incognito")

# Initialize results list
results = []
full_storage_data = []  # To store full storage contents

# Websites to test, with interaction functions
websites = [
    {
        "url": "https://www.ebay.com",
        "interaction_func": ebay_interaction  # Placeholder for actual interaction function, if any
    },
    {
        "url": "https://www.cnn.com",
        "interaction_func": None  # Placeholder for actual interaction function, if any
    },
    {
        "url": "https://www.docs.google.com",
        "interaction_func": None  # Placeholder for actual interaction function, if any
    }
]

# Function to collect storage data
def collect_storage_data(driver, mode, website):
    try:
        # Collect localStorage, sessionStorage, IndexedDB
        local_storage = driver.execute_script("return window.localStorage;")
        session_storage = driver.execute_script("return window.sessionStorage;")

        # IndexedDB collection
        indexed_db_data = driver.execute_script("""
            return new Promise((resolve, reject) => {
                let result = [];
                let request = indexedDB.databases();
                request.then((dbs) => {
                    dbs.forEach((db) => {
                        result.push(db.name);
                    });
                    resolve(result);
                }).catch((err) => reject(err));
            });
        """)

        # Append summary results to the list
        results.append({
            "website": website,
            "mode": mode,
            "localStorage": len(local_storage),
            "sessionStorage": len(session_storage),
            "indexedDB": len(indexed_db_data)
        })

        # Append full storage contents for JSON output
        full_storage_data.append({
            "website": website,
            "mode": mode,
            "localStorage": local_storage,
            "sessionStorage": session_storage,
            "indexedDB": indexed_db_data
        })
    except Exception as e:
        print(f"Error collecting storage data on {website} in {mode} mode: {str(e)}")

# Abstract function to run tests in a specific mode
def run_tests(websites, mode="normal", options=None):
    # Initialize WebDriver
    driver = webdriver.Chrome(options=options) if options else webdriver.Chrome()

    # Loop through each website and perform the test
    for site in websites:
        test_website(driver, site['url'], mode=mode, interaction_func=site['interaction_func'])

    # Close the browser after the tests
    driver.quit()

# Function to visit and interact with websites
def test_website(driver, website, mode="normal", interaction_func=None):
    try:
        driver.get(website)
        print(f"Testing {website} in {mode} mode...")

        # Run the provided interaction function, if any
        if interaction_func:
            interaction_func(driver)
        else:
            print(f"No custom interactions provided for {website}.")
        time.sleep(2)
        # Collect storage data
        collect_storage_data(driver, mode, website)
    except Exception as e:
        print(f"Error testing {website} in {mode} mode: {str(e)}")

# Run tests in normal mode
run_tests(websites, mode="normal")

# Run tests in incognito mode
run_tests(websites, mode="incognito", options=chrome_options)

# Convert results to a DataFrame
df = pd.DataFrame(results)

# Summary of the results
summary = df.groupby(['website', 'mode']).sum()
print("Summary of Results:")
print(summary)

# Plotting the storage data across the websites in normal vs incognito mode
fig, ax = plt.subplots(figsize=(10, 6))

df.groupby(['website', 'mode'])[['localStorage', 'sessionStorage', 'indexedDB']].sum().unstack().plot(kind='bar', ax=ax)

plt.title('Storage Data Counts Across Websites (Normal vs Incognito Mode)')
plt.xlabel('Websites')
plt.ylabel('Count of Stored Entries')
plt.xticks(rotation=45)
plt.tight_layout()

# Show the plot
plt.show()

# Save summary results to CSV
df.to_csv("storage_analysis_results.csv", index=False)

# Save full storage contents to JSON
with open("storage_analysis_full.json", "w") as json_file:
    json.dump(full_storage_data, json_file, indent=4)

print("Results saved to storage_analysis_results.csv and storage_analysis_full.json")
