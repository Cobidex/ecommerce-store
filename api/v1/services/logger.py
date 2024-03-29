import logging
from datetime import datetime
import os

def get_logger(name):
    current_day = datetime.now().strftime('%Y-%m-%d')
    current_directory = os.getcwd()
    log_dir = f"{current_directory}/api/v1/logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(f"{log_dir}/{current_day}_{name}.log")
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

# general loggers
login_logger = get_logger('login')
register_logger = get_logger('register')
account_activation_logger = get_logger('account_activation')
verify_email_logger = get_logger('verify_email')
update_profile_logger = get_logger('update_profile')
request_verification_logger = get_logger('request_verification')
email_update_logger = get_logger('email_update')
admin_notification_logger = get_logger('admin_notification')
logout_logger = get_logger('logout')
get_profile_logger = get_logger('get_profile')
account_deactivation_logger = get_logger('account_deactivation')
verification_complete_email_logger = get_logger('verification_complete_email')
cart_creation_logger = get_logger('cart_creation')
admin_creation_logger = get_logger('admin_creation')

# buyer loggers
get_all_buyers_logger = get_logger('get_all_buyers')

# vendor loggers
get_all_vendors_logger = get_logger('get_all_vendors')

# product loggers
get_all_products_logger = get_logger('get_all_products')
search_product_logger = get_logger('search_product')
get_product_logger = get_logger('get_product')
product_update_logger = get_logger('product_update')
upload_product_logger = get_logger('upload_product')
delete_product_logger = get_logger('delete_product')

# reviews loggers
get_all_reviews_logger = get_logger('get_all_reviews')
post_product_review_logger = get_logger('post_product_review')
update_product_review = get_logger('update_product_review')
delete_product_review_logger = get_logger('delete_product_review')