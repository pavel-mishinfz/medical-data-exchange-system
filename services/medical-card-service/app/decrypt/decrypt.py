import json


def decrypt_card(card, cipher_suite):
    card.address = decrypt_address(card.address, cipher_suite)
    card.passport = decrypt_passport(card.passport, cipher_suite)
    if card.disability:
        card.disability = decrypt_disability(card.disability, cipher_suite)
    card.phone = cipher_suite.decrypt(card.phone).decode()
    card.number_policy = cipher_suite.decrypt(card.number_policy).decode()
    card.snils = cipher_suite.decrypt(card.snils).decode()
    card.insurance_company = cipher_suite.decrypt(card.insurance_company).decode()
    card.benefit_category_code = cipher_suite.decrypt(card.benefit_category_code).decode()
    card.workplace = cipher_suite.decrypt(card.workplace).decode()
    card.job = cipher_suite.decrypt(card.job).decode()
    card.blood_type = cipher_suite.decrypt(card.blood_type).decode()
    card.allergy = cipher_suite.decrypt(card.allergy).decode()
    return card


def decrypt_address(address, cipher_suite):
    address.subject = cipher_suite.decrypt(address.subject).decode()
    address.district = cipher_suite.decrypt(address.district).decode()
    address.locality = cipher_suite.decrypt(address.locality).decode()
    address.street = cipher_suite.decrypt(address.street).decode()
    address.house = int(cipher_suite.decrypt(address.house).decode())
    address.apartment = int(cipher_suite.decrypt(address.apartment).decode())
    return address


def decrypt_passport(passport, cipher_suite):
    passport.number = cipher_suite.decrypt(passport.number).decode()
    passport.series = cipher_suite.decrypt(passport.series).decode()
    return passport


def decrypt_disability(disability, cipher_suite):
    disability.name = cipher_suite.decrypt(disability.name).decode()
    disability.group = cipher_suite.decrypt(disability.group).decode()
    disability.create_date = cipher_suite.decrypt(disability.create_date).decode()
    return disability


def decrypt_page(page, cipher_suite):
    decoded_page_data = cipher_suite.decrypt(page.data).decode()
    page.data = json.loads(decoded_page_data)
    return page