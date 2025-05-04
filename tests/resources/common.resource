*** Settings ***
Library     SeleniumLibrary
Library     String

*** Variables ***
${SERVER}           localhost:5000
${BROWSER}          chrome
${DELAY}            0.1
${HOME URL}         http://${SERVER}/
${LOGIN URL}        http://${SERVER}/login
${VALID USER}       testuser
${VALID PASSWORD}   password123

*** Keywords ***
Open Browser To Home Page
    [Documentation]    Open the browser to the home page of QuickGrocer. Disabled password manager and leak detection so that the test can run without interruptions.
    ${prefs}=    Create Dictionary    credentials_enable_service=${FALSE}    profile.password_manager_enabled=${FALSE}    profile.password_manager_leak_detection=${FALSE}
    ${options}=    Evaluate    selenium.webdriver.ChromeOptions()    selenium
    Call Method    ${options}    add_experimental_option    prefs    ${prefs}
    Call Method    ${options}    add_argument    --disable-infobars
    Call Method    ${options}    add_argument    --disable-notifications
    Open Browser    ${HOME URL}    chrome    options=${options}
    Set Selenium Speed    ${DELAY}
    Maximize Browser Window
    Wait Until Page Contains Element    css=.navbar

Go To Login Page
    Go To    ${LOGIN URL}
    Wait Until Page Contains Element    id:username

Input Username
    [Arguments]    ${username}
    Input Text    id:username    ${username}

Input Password
    [Arguments]    ${password}
    Input Text    id:password    ${password}

Submit Login Form
    Click Button    xpath=//button[@type="submit"]

Login As Test User
    Go To Login Page
    Input Username    ${VALID USER}
    Input Password    ${VALID PASSWORD}
    Submit Login Form
    Wait Until Page Contains    Logged in successfully!

