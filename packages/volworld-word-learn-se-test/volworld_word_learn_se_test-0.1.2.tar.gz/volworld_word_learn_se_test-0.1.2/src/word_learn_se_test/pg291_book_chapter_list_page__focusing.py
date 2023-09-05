from behave import *
from selenium.webdriver.common.by import By
from volworld_common.test.behave.BehaveUtil import BehaveUtil
from volworld_aws_api_common.test.behave.selenium_utils import get_element_by_dom_id

from api.A import A
from src.word_learn_se_test.focusing_app_bar import check_focusing_circles_and_slots_on_focusing_bar, \
    remove_focusing_row_by_text, click_row_to_add_focusing_item
from volworld_aws_api_common.test.behave.selenium_utils import click_element, get_elm_text, \
    w__get_element_by_shown_dom_id, w__click_element_by_dom_id
from test.wiremock.OperationIdUrl import OperationUrl
from test.wiremock.Wiremock import Wiremock


@then('{focusing_ch} focusing Chapters and {empty_slots} empty slots shown on focusing bar')
def check_focusing_chapters_and_slot_on_focusing_bar(c, focusing_ch: str, empty_slots: str):
    check_focusing_circles_and_slots_on_focusing_bar(c, focusing_ch, empty_slots)

