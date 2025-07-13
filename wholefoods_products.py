import time, csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoAlertPresentException

def get_visible_products(driver, elements, seen_html):
    """
    Gets all products elements and html visible on a page
    Html is necessary for the function to halt
    """
    try:
        product_elements = driver.find_elements(By.CLASS_NAME, 'w-pie--product-tile')
    except StaleElementReferenceException:
        product_elements = []

    for product in product_elements:
        try:
            html = product.get_attribute("outerHTML")
            if html not in seen_html:
                seen_html.add(html)
                elements.append(product)
        except StaleElementReferenceException:
            continue


def get_product_elements(driver):
    """
    Scrolls through and loads all products on the 'all products' page
    Collects the products as it scrolls
    """
    product_elements = []
    seen_html = set()

    # collect products initially on the page
    get_visible_products(driver, product_elements, seen_html)
    p_count = len(product_elements)

    while True:
        # scroll
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, arguments[0]);", scroll_height - 1500)
        time.sleep(2)

        # click load more button if it is there
        try:
            load_more_btn = driver.find_element(By.CLASS_NAME, 'w-button')
            if load_more_btn.is_displayed():
                load_more_btn.click()
                time.sleep(2)
        except NoSuchElementException:
            pass

        # get the products on the page
        get_visible_products(driver, product_elements, seen_html)

        # stop when no new products are collected, note that there is a buffer at the end of the page
        if len(product_elements) == p_count:
            break

        p_count = len(product_elements)
        time.sleep(2)

    print(f"Product count: {len(product_elements)}")
    return product_elements

def get_wholefoods_products(link = "https://www.wholefoodsmarket.com/", store_id = 10044):
    """
    Given a link and store_id, finds all the products available at a given store
    and writes the name, UPC, size, and other attributes to a CSV file
    """

    store_ids = {10044 : '94109'}

    driver = webdriver.Chrome()
    driver.get(link)
    
    # find and enter the select a store menu
    driver.find_element(By.CLASS_NAME, 'bds--heading-5').click()
    iframe = driver.find_element(By.NAME, 'store-web-page')
    driver.switch_to.frame(iframe)
    time.sleep(10)

    # click the search bar and search for a specific store
    store_search = driver.find_element(By.CLASS_NAME, 'wfm-search-bar--input')
    store_search.click()
    store_search.send_keys(store_ids[store_id])
    store_search.send_keys(Keys.ENTER)
    time.sleep(10)

    # select store
    driver.find_element(By.CLASS_NAME, 'w-store-selector').click()
    time.sleep(10)

    # close store selection menu
    driver.switch_to.default_content()
    driver.find_element(By.CLASS_NAME, 'modalCloseButtonStyle').click()
    time.sleep(10)

    # enter product menu
    driver.find_element(By.CLASS_NAME, 'flex.items-center.text-kale').click()
    time.sleep(10)
    try:
        alert = driver.switch_to.alert()
        alert.dimiss()
    except NoAlertPresentException:
        print('No Alert')
    driver.find_element(By.CLASS_NAME, 'w-link.w-link--light-nav').click()
    
    # get products at specific store
    product_elements = get_product_elements(driver)

    # write product data to csv file
    with open('product_data.csv', 'w') as f:
        # under construction
        pass


    time.sleep(10)
    driver.close()
    driver.quit()

if __name__ == "__main__":
    get_wholefoods_products()

# code for technical assessment purposes only