*** Settings ***
Documentation     Test cart functionality in QuickGrocer
Resource          common.resource
Test Setup        Setup Cart Test
Test Teardown     Close All Browsers

*** Keywords ***
Setup Cart Test
    Open Browser To Home Page
    Login As Test User
    Navigate To Empty Cart

Navigate To Empty Cart
    Go To    ${HOME URL}cart
    ${cart_empty}=    Run Keyword And Return Status    Page Should Contain    Your Cart is Empty
    Run Keyword If    not ${cart_empty}    Empty Cart

Empty Cart
    Click Link    Clear Cart
    Wait Until Page Contains    Cart is Empty

Add Product To Cart By Index
    [Arguments]    ${index}=1    ${quantity}=2
    Go To    ${HOME URL}products
    Wait Until Page Contains Element    xpath=(//a[contains(@href, '/add_to_cart/')])[${index}]
    Click Link    xpath=(//a[contains(@href, '/add_to_cart/')])[${index}]
    Wait Until Page Contains Element    id:quantity
    Select From List By Value    id:quantity    ${quantity}
    Click Button    Add to Cart
    Wait Until Page Contains    Product added to cart!

*** Test Cases ***
Add Product To Cart
    [Documentation]    Test adding a product to cart
    Add Product To Cart By Index    1    2
    Go To    ${HOME URL}cart
    Page Should Not Contain    Your Cart is Empty
    Page Should Contain Element    xpath=//h5/strong[contains(text(), 'Quantity:')]
    Page Should Contain Element    xpath=//h5/strong[contains(text(), 'Total Price')]

Update Cart Quantity
    [Documentation]    Test updating cart quantity
    Add Product To Cart By Index    1    1
    Go To    ${HOME URL}cart
    Wait Until Page Contains Element    xpath=//a[contains(text(), 'Edit Cart')]
    Click Link    Edit Cart
    Wait Until Page Contains Element    id:quantity
    Select From List By Value    id:quantity    3
    Click Button    Add to Cart
    Wait Until Page Contains    Cart updated!
    Page Should Contain Element    xpath=//h5/strong[contains(text(), 'Quantity:')]

Remove Product From Cart
    [Documentation]    Test removing a product from cart
    Add Product To Cart By Index    1    1
    Go To    ${HOME URL}cart
    Wait Until Page Contains Element    xpath=//a[contains(text(), 'Remove from Cart')]
    Click Link    Remove from Cart
    Wait Until Page Contains    Product removed from cart!
    Page Should Contain    Your Cart is Empty