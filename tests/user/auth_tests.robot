*** Settings ***
Documentation     Login and product browsing test for QuickGrocer
Resource          common.resource
Test Setup        Open Browser To Home Page
Test Teardown     Close All Browsers

*** Test Cases ***
Valid User Login
    [Documentation]    Test user can successfully login
    Go To Login Page
    Input Username     testuser
    Input Password     password123
    Submit Login Form
    Page Should Contain    Logged in successfully!
    
Browse Products And Add To Cart
    [Documentation]    Test browsing products and adding to cart
    Login As Test User
    Click Link    Products
    Wait Until Page Contains Element    css=.card-title
    ${product_name}=    Get Text    css=.card-title
    Click Link    xpath=(//a[contains(@href, '/product/')])[1]
    Wait Until Page Contains Element    xpath=//h1
    Page Should Contain    ${product_name}
    Click Link    Add to Cart
    Wait Until Page Contains Element    id:quantity
    Select From List By Value    id:quantity    2
    Click Button    Add to Cart
    Page Should Contain    Product added to cart!
    
Search For Product
    [Documentation]    Test product search functionality
    Login As Test User
    Input Text    name=query    Milk
    Click Button    xpath=//button[@type='submit'][contains(text(), '🔍')]
    Wait Until Page Contains Element    css=.card-title
    Page Should Contain Element    xpath=//h4[contains(text(), 'Search Results for "Milk"')]