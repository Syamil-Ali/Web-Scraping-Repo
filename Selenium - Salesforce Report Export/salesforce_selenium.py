from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
import time
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import traceback



#---------------------------- BUTTON CLICK FUNCTION  -----------------------#

def click_button(driver, by_type, value):
    
    if by_type == 'CSS_SELECTOR':
        wait(driver, 120).until(EC.visibility_of_element_located((By.CSS_SELECTOR, value)))
        button = driver.find_element(By.CSS_SELECTOR, value)
    elif by_type == 'XPATH':
        wait(driver, 120).until(EC.visibility_of_element_located((By.XPATH, value)))
        button = driver.find_element(By.XPATH, value)
    elif by_type == 'ID':
        wait(driver, 120).until(EC.visibility_of_element_located((By.ID, value)))
        button = driver.find_element(By.ID, value)

        
    button.click()
    return button


#---------------------------- SALESFORCE LOGIN  -----------------------#
# Login thru company SSO

def salesforce_login(driver):

    driver.get("company_url")


    time.sleep(15)

 
    login_button_sso = driver.find_element("xpath","//*[contains(text(), 'text-here')]") # text button value
    login_button_sso.click()

    time.sleep(10)

    # Login Credential
    email = ''
    password = ''

    # Email box
    email_box = driver.find_element(By.ID, 'i0116')
    email_box.send_keys(email)

    # Next button
    confirm_button = driver.find_element(By.ID, 'idSIButton9') 
    confirm_button.click()

    time.sleep(10)

    # Password box
    password_box = driver.find_element(By.ID, 'i0118')
    password_box.send_keys(password)

    # Submit button
    confirm_button = driver.find_element(By.ID, 'idSIButton9')
    confirm_button.click()


    try:
        wait(driver, 50).until(EC.visibility_of_element_located((By.ID, "oneHeader")))
    except:
        
        pass


    # go to report page
    report_url = ''
    driver.get(report_url)


    # ----- Mini Step to handle notification ----------

    # click the noti button
    noti_button_class = ".headerButtonBody"
    noti_xclass = '//*[@id="oneHeader"]/div[2]/span/div[2]/ul/li[6]'
    noti_button = click_button(driver, 'XPATH', noti_xclass)

    try:
        mark_as_all_read = "//a[text()='Mark all as read']"
        mark_button = click_button(driver, 'XPATH', mark_as_all_read)
        print('marked as all read click')
    except:
        pass
    time.sleep(2)

    noti_button = click_button(driver, 'XPATH', noti_xclass)
    # ----- mini step to handle notification (end) ----------

    # 

    # Wait for the iframe to be available and switch to it
    wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))

    time.sleep(2)



#---------------------------- SALESFORCE REPORT AND EXPORT  -----------------------#


def salesforce_report(driver, filter_text, account_report):

    # The idea
    # 1. click filter button
    # 2. filter based on a field
    # 3. fill in the field
    # 4. click apply button
    # 5. click dropdown button
    # 6. click save button until a timeframe exist
    # 7. 2 report, - Account & Opportunity


    if account_report == 'Account':
        acc_report_url = ''
        driver.get(acc_report_url)

        wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))

        time.sleep(2)
    else:
        pass

    
    # click the filter button
    filter_class_name = '.action-bar-action-toggleFilter.reportAction.report-action-toggleFilter.slds-button.slds-not-selected.slds-button_icon-border'
    click_button(driver, 'CSS_SELECTOR', filter_class_name) # click filter button
    print('clicked the filter button')

    # to wait until mdm id is visible and click
    xpath_mdm_field = "//button[span[text()='']]" # text field filter
    click_button(driver, 'XPATH', xpath_mdm_field)

    # to wait and click the search field
    input_field = 'undefined-input'
    input_button = click_button(driver, 'ID', input_field)

    # enter the value
    input_button.clear()
    input_button.send_keys(filter_text)


    # to wait and click the apply button
    apply_button_xpath = "//button[text()='Apply']"
    click_button(driver, 'XPATH', apply_button_xpath)


    # click filter button again - or reconsider putting additional timeframe here
    click_button(driver, 'CSS_SELECTOR', filter_class_name)


    # --- mission - to save report first

    # click the dropdown button
    dropdown_button_class = '.slds-dropdown-trigger.slds-dropdown-trigger_click.slds-button_last'
    click_button(driver, 'CSS_SELECTOR', dropdown_button_class)
    print('clicked dropdown button')


    # click the save report
    time.sleep(1)
    save_field = "//span[text()='Save']"
    click_button(driver, 'XPATH', save_field)
    print('clicked save button')



    # explicitly wait until save
    driver.switch_to.default_content()

    if account_report == 'Account':
        save_popup_add = '.toastMessage.slds-text-heading--small.forceActionsText'
        save_popup_xpath = """//span[text()='Report "Accounts Segment Report" was saved']"""
        wait(driver, 100).until(EC.visibility_of_element_located((By.XPATH, save_popup_xpath)))


        # Change to Classic view # Need to click to change profile first
        driver.get('') # url to swith from lightning to classic view
        time.sleep(10)
        driver.get('') # go to the report again
        time.sleep(10)

    else:
        save_popup_add = '.toastMessage.slds-text-heading--small.forceActionsText'
        save_popup_xpath = """//span[text()='Report "Account Opportunity Draft" was saved']"""
        wait(driver, 100).until(EC.visibility_of_element_located((By.XPATH, save_popup_xpath)))

        # Change to Classic view # Need to click to change profile first
        driver.get('')
        time.sleep(4)
        time.sleep(4)
        driver.get('')
        time.sleep(10)



#---------------------------- SELENIUM END HERE -----------------------#


#---------------------------- TO GET THE TABLE -----------------------#

def salesforce_table_extract(driver):

    # get the table using bs4
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all table elements
    tables = soup.find_all("table")

    winner = []
    len_store = []

    # check the total count of table 
    for index, table in enumerate(tables):

        tbl_str = str(table)  # Convert the table to a string if necessary
        df_salesforce = pd.read_html(StringIO(tbl_str))[0]
        
        #df_salesforce = pd.read_html(str(tables[index]))[0]
        
        #print(index)
        if 'MDM Id' in df_salesforce.columns:
            
            # get the len shape
            len_df = df_salesforce.shape[0]
            
            winner.append(index)
            len_store.append(len_df)
            

    # get the winner
    index_of_max_value = len_store.index(max(len_store))

    winner_df = winner[index_of_max_value]
    
    # apply the winner
    df_salesforce = pd.read_html(StringIO(str(tables[winner_df])))[0]
    df_salesforce = df_salesforce.dropna(how='all')

    # drop last rows
    df_salesforce = df_salesforce.dropna(subset=['Owner Role','Opportunity Owner', 'Account Name', 'Opportunity Name'], how='all')


    # cleaning up df

    #df_salesforce = pd.read_html(str(tables[6]))[0]
    df_salesforce_copy = df_salesforce[~df_salesforce['Account Name'].str.contains('Grand Totals \\(', na=False)].copy()


    # change the 4 columns to float
    # Assuming 'Price' is the column with values like 'USD 0.00'
    df_salesforce_copy['Item Sub-Total'] = df_salesforce_copy['Item Sub-Total'].str.replace(',', '')
    df_salesforce_copy['Item Sub-Total'] = df_salesforce_copy['Item Sub-Total'].str.replace('USD ', '').astype(float)

    return df_salesforce_copy

#df_salesforce_copy

#---------------------------- TO GET THE TABLE END -----------------------#






def salesforce_table_extract_account(driver):

    # get the table using bs4
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #tbl = soup.find("table")

    # Find all table elements
    tables = soup.find_all("table")

    winner = []
    len_store = []

    # check the total count of table 
    for index, table in enumerate(tables):

        #print(f'account table found: {index}')
        
        df_salesforce = pd.read_html(StringIO(str(tables[index])))[0]
        
        #print(index)
        if 'MDM Id' in df_salesforce.columns:
            
            # get the len shape
            len_df = df_salesforce.shape[0]
            
            winner.append(index)
            len_store.append(len_df)
            

    # get the winner
    index_of_max_value = len_store.index(max(len_store))

    winner_df = winner[index_of_max_value]

    # apply the winner
    df_salesforce = pd.read_html(StringIO(str(tables[winner_df])))[0]
    df_salesforce = df_salesforce.dropna(how='all')

    # drop last row
    df_salesforce = df_salesforce.dropna(subset=['Account Owner', 'Account Name', 'Account ID'], how='all')


    #df_salesforce = pd.read_html(str(tables[6]))[0]
    df_salesforce_copy = df_salesforce[~df_salesforce['Account Name'].str.contains('Grand Totals \\(', na=False)].copy()


    return df_salesforce_copy



################### START ###########################
def start(df):

    # 1. Get the MDM ID
    filter_text = ''


    # 2. Open Up Chrome
    try:
        cService = webdriver.ChromeService() #executable_path= chromdriver_path
        driver = webdriver.Chrome(service = cService)

        width = 1200
        height = 800
        driver.set_window_size(width, height)

        driver.get('chrome://settings/clearBrowserData') # to clear any saved browswer data

    except:
        # driver = 
        pass


    # 3. Login to Salesforce
    salesforce_login(driver)


    # 4. Generate Opp Report - Salesforce
    print('* Opportunity Table - START *')
    for retry in range(3):
        try:
            salesforce_report(driver, filter_text, 'Opportunity')
            time.sleep(1)
            break
        except:
            print(e)
            traceback.print_exc()
            driver.refresh()
    opp_df = salesforce_table_extract(driver)
    print('Opportunity Table - PASS')

    print('----')


    # 5. Generate Account Report - Salesforce
    print('* Account Table - START *')
    for retry in range(3):
        try:
            salesforce_report(driver, filter_text, 'Account')
            time.sleep(1)
            break
        except Exception as e:
            print(e)
            traceback.print_exc()
            driver.refresh()
    account_df = salesforce_table_extract_account(driver)
    print('Account Table - PASS')



    # 6. Convert back to Salesforce Lightning Format for easy future use
    try:
        wait(driver, 120).until(EC.visibility_of_element_located((By.CLASS_NAME, "switch-to-lightning")))

        # to swith to lightning coz got weird interaction if not
        lightning_convert = driver.find_element(By.CLASS_NAME,"switch-to-lightning")
        lightning_convert.click()
            
    except:
        pass

    return driver, opp_df, account_df, driver.get_cookies()