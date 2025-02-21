from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = OpenAI(model_name="gpt-4", openai_api_key="") 

prompt = PromptTemplate(
    input_variables=["status"],
    template="The LinkedIn process returned this status: {status}. What should the agent do next?",
)

chain = LLMChain(llm=llm, prompt=prompt)

def linkedin_ai_agent(username, password):
    driver = webdriver.Chrome()
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    try:
        #Login Process
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
        time.sleep(5)

        #Status
        if "feed" in driver.current_url:
            status = "Login successful"
        elif "checkpoint" in driver.current_url:
            status = "Security check required"
        else:
            status = "Login failed"
        ai_decision = chain.run(status=status)
        print(f"AI Decision: {ai_decision}")

        if "Login successful" in status:
            print("Agent is now inside LinkedIn!")

            #Ask AI if it should open dropdown
            ai_decision = chain.run(status="Agent is logged in. Should it open the dropdown?")
            if "yes" in ai_decision.lower():
                print("AI decided to open the dropdown.")

                # Locate and click the dropdown
                dropdown_xpath = "//button[contains(@class, 'global-nav__me-menu')]"
                dropdown_button = driver.find_element(By.XPATH, dropdown_xpath)
                dropdown_button.click()
                time.sleep(2)

                # Ask AI if it should log out
                ai_decision = chain.run(status="Dropdown is open. Should the agent click logout?")
                if "yes" in ai_decision.lower():
                    print("AI decided to log out.")

                    # Locate and click the Logout button
                    logout_xpath = "//a[contains(@href, 'logout')]"
                    logout_button = driver.find_element(By.XPATH, logout_xpath)
                    logout_button.click()
                    time.sleep(3)

                    if "login" in driver.current_url:
                        print("Logout successful! Agent is back on the login page.")
                    else:
                        print("Logout action did not work as expected.")

        else:
            print("Agent needs human input.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    input("Press Enter to close browser...")
    driver.quit()

#Credentials
email = input()
password = input()

linkedin_ai_agent(email, password)
