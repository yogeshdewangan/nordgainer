from fyers_api import accessToken, fyersModel

from selenium import webdriver
import time
import conf_reader

app_id = conf_reader.props["fyers_app_id"]
app_secret = conf_reader.props["fyers_app_secret"]
FYERS_ID = conf_reader.props["fyers_login_id"]
FYERS_PASSWORD = conf_reader.props["fyers_password"]
PANCARD = conf_reader.props["pancard"]

fyers = fyersModel.FyersModel(False)

def get_access_token( accessToken):
    app_session = accessToken.SessionModel(app_id, app_secret)
    response = app_session.auth()

    if response["code"] != 200:
        print("Fyers app login successful")

    auth_code = response["data"]["authorization_code"]
    app_session.set_token(auth_code)
    generateTokenUrl = app_session.generate_token()
    driver = webdriver.Chrome("chromedriver.exe")
    driver.get(generateTokenUrl)
    driver.find_element_by_id("fyers_id").send_keys(FYERS_ID)
    driver.find_element_by_id("password").send_keys(FYERS_PASSWORD)
    driver.find_element_by_id("pancard").send_keys(PANCARD)
    driver.find_element_by_id("btn_id").click()

    time.sleep(10)

    current_url = driver.current_url
    driver.quit()
    access_token = current_url.split("access_token=")[1]
    return access_token


f= open("token.txt","r")
access_token = f.read()
if access_token == '':
    access_token = get_access_token(accessToken )
else:
    profile = fyers.get_profile(token=access_token)
    if profile["code"] != 200:
        access_token = get_access_token(accessToken)
f.close()


f= open("token.txt","w")
f.write(access_token)
f.close()


profile = fyers.get_profile(token = access_token)
print(str(profile))

funds = fyers.funds(token = access_token)
print(str(funds))





