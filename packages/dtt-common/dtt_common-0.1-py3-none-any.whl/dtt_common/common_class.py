import logging
import os
import time
from pathlib import Path
from traceback import print_stack

import common_logger as cl
import cv2
import imutils
import pytest
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from skimage.metrics import structural_similarity as compare


class SeleniumDriver:
    log = cl.customLogger(logging.DEBUG)

    def __init__(self, driver):
        self.driver = driver

    def screenShot(self, resultMessage):
        """
        Takes screenshot of the current open web page
        """
        fileName = f"{resultMessage}.{str(round(time.time() * 1000))}.png"
        screenshotDirectory = "../screenshots/"
        relativeFileName = screenshotDirectory + fileName
        currentDirectory = os.path.dirname(__file__)
        destinationFile = os.path.join(currentDirectory, relativeFileName)
        destinationDirectory = os.path.join(currentDirectory, screenshotDirectory)

        try:
            if not os.path.exists(destinationDirectory):
                os.makedirs(destinationDirectory)
            self.driver.save_screenshot(destinationFile)
            self.log.info(f"Screenshot save to directory: {destinationFile}")
        except Exception:
            self.log.error("### Exception Occurred when taking screenshot")
            print_stack()

    def getTitle(self):
        return self.driver.title

    def getByType(self, locatorType):
        locatorType = locatorType.lower()
        if locatorType == "id":
            return By.ID
        elif locatorType == "name":
            return By.NAME
        elif locatorType == "xpath":
            return By.XPATH
        elif locatorType == "css":
            return By.CSS_SELECTOR
        elif locatorType == "class":
            return By.CLASS_NAME
        elif locatorType == "link":
            return By.LINK_TEXT
        elif locatorType == "tag":
            return By.TAG_NAME
        else:
            self.log.info((f"Locator type {locatorType}" + " not correct/supported"))
        return False

    def getElement(self, locator, locatorType="name"):
        element = None
        try:
            locatorType = locatorType.lower()
            byType = self.getByType(locatorType)
            element = self.driver.find_element(byType, locator)
            self.log.info(
                (
                        (f"Element found with locator: {locator}" + " and  locatorType: ")
                        + locatorType
                )
            )
        except Exception:
            self.log.info(
                (
                        (
                                f"Element not found with locator: {locator}"
                                + " and  locatorType: "
                        )
                        + locatorType
                )
            )

        return element

    def getElementList(self, locator, locatorType="name"):
        """
        NEW METHOD
        Get list of elements
        """
        element = None
        try:
            locatorType = locatorType.lower()
            byType = self.getByType(locatorType)
            element = self.driver.find_elements(byType, locator)
            self.log.info(
                (
                        (
                                f"Element list found with locator: {locator}"
                                + " and locatorType: "
                        )
                        + locatorType
                )
            )

        except Exception:
            self.log.info(
                (
                        (
                                f"Element list not found with locator: {locator}"
                                + " and locatorType: "
                        )
                        + locatorType
                )
            )

        return element

    def elementClick(self, locator="", locatorType="name", element=None):
        """
        Click on an element -> MODIFIED
        Either provide element or a combination of locator and locatorType
        """
        try:
            if locator:  # This means if locator is not empty
                element = self.getElement(locator, locatorType)
            element.click()
            self.log.info(
                (
                        (f"Clicked on element with locator: {locator}" + " locatorType: ")
                        + locatorType
                )
            )

        except Exception:
            self.log.info(
                (
                        (
                                f"Cannot click on the element with locator: {locator}"
                                + " locatorType: "
                        )
                        + locatorType
                )
            )

            print_stack()

    def elementAttribute(self, value="", locator="", locatorType="name", element=None):
        """
        Click on an element -> MODIFIED
        Either provide element or a combination of locator and locatorType
        """
        try:
            if locator:  # This means if locator is not empty
                element = self.getElement(locator, locatorType)
            attribute_value = element.get_attribute(value)
            self.log.info(
                (
                        (f"Clicked on element with locator: {locator}" + " locatorType: ")
                        + locatorType
                )
            )
            return attribute_value
        except Exception:
            self.log.info(
                (
                        (
                                f"Cannot click on the element with locator: {locator}"
                                + " locatorType: "
                        )
                        + locatorType
                )
            )

            print_stack()

    def sendKeys(self, data, locator="", locatorType="name", element=None):
        """
        Send keys to an element -> MODIFIED
        Either provide element or a combination of locator and locatorType
        """
        try:
            if locator:  # This means if locator is not empty
                element = self.getElement(locator, locatorType)
            element.send_keys(data)
            self.log.info(
                (
                        (f"Sent data on element with locator: {locator}" + " locatorType: ")
                        + locatorType
                )
            )

        except Exception:
            self.log.info(
                "Cannot send data on the element with locator: "
                + locator
                + " locatorType: "
                + locatorType
            )
            print_stack()

    def clearField(self, locator="", locatorType="name"):
        """
        Clear an element field
        """
        element = self.getElement(locator, locatorType)
        element.clear()
        self.log.info(f"Clear field with locator: {locator} locatorType: {locatorType}")

    def getText(
            self, locator="", locatorType="name", element=None, attribute="class", info=""
    ):
        """
        NEW METHOD
        Get 'Text' on an element
        Either provide element or a combination of locator and locatorType
        """
        try:
            if locator:  # This means if locator is not empty
                element = self.getElement(locator, locatorType)
            text = element.text
            if len(text) == 0:
                text = element.get_attribute(attribute)
            if len(text) != 0:
                self.log.info(f"Getting text on element :: {info}")
                self.log.info("The text is :: '" + text + "'")
                text = text.strip()
        except Exception:
            self.log.error(f"Failed to get text on element {info}")
            print_stack()
            text = None
        return text

    def isElementPresent(self, locator="", locatorType="name", element=None):
        """
        Check if element is present -> MODIFIED
        Either provide element or a combination of locator and locatorType
        """
        try:
            if locator:  # This means if locator is not empty
                element = self.getElement(locator, locatorType)
            if element is not None:
                self.log.info(
                    (
                            (f"Element present with locator: {locator}" + " locatorType: ")
                            + locatorType
                    )
                )

                return True
            else:
                self.log.info(
                    (
                            (
                                    f"Element not present with locator: {locator}"
                                    + " locatorType: "
                            )
                            + locatorType
                    )
                )

                return False
        except Exception:
            print("Element not found")
            return False

    def isElementDisplayed(self, locator="", locatorType="name", element=None):
        """
        NEW METHOD
        Check if element is displayed
        Either provide element or a combination of locator and locatorType
        """
        isDisplayed = False
        try:
            if locator:  # This means if locator is not empty
                element = self.getElement(locator, locatorType)
            if element is not None:
                isDisplayed = element.is_displayed()
                self.log.info("Element is displayed")
            else:
                self.log.info("Element not displayed")
            return isDisplayed
        except Exception:
            print("Element not found")
            return False

    def isElementEnabled(self, locator="", locatorType="name", element=None):
        """
        NEW METHOD
        Check if element is enabled
        Either provide element or a combination of locator and locatorType
        """
        isDisplayed = False
        try:
            if locator:  # This means if locator is not empty
                element = self.getElement(locator, locatorType)
            if element is not None:
                isEnabled = element.is_enabled()
                self.log.info("Element is displayed")
            else:
                self.log.info("Element not displayed")
            return isEnabled
        except Exception:
            print("Element not found")
            return False

    def elementPresenceCheck(self, locator, byType):
        """
        Check if element is present
        """
        try:
            elementList = self.driver.find_elements(byType, locator)
            if len(elementList) > 0:
                self.log.info(
                    (f"Element present with locator: {locator}" + " locatorType: ")
                    + str(byType)
                )

                return True
            else:
                self.log.info(
                    (f"Element not present with locator: {locator}" + " locatorType: ")
                    + str(byType)
                )

                return False
        except Exception:
            self.log.info("Element not found")
            return False

    def waitForElement(
            self, locator, locatorType="name", timeout=10, pollFrequency=0.5
    ):
        element = None
        try:
            byType = self.getByType(locatorType)
            self.log.info(
                (
                        f"Waiting for maximum :: {str(timeout)}"
                        + " :: seconds for element to be clickable"
                )
            )

            wait = WebDriverWait(
                self.driver,
                timeout=timeout,
                poll_frequency=pollFrequency,
                ignored_exceptions=[
                    NoSuchElementException,
                    ElementNotVisibleException,
                    ElementNotSelectableException,
                ],
            )
            element = wait.until(EC.element_to_be_clickable((byType, locator)))
            self.log.info("Element appeared on the web page")
        except Exception:
            self.log.info("Element not appeared on the web page")
            print_stack()
        return element

    def checkValue(
            self, locator, locatorType="name", timeout=10, pollFrequency=0.5, text=""
    ):
        element = None
        try:
            byType = self.getByType(locatorType)
            self.log.info(
                (
                        f"Waiting for maximum :: {str(timeout)}"
                        + " :: seconds to compare text values"
                )
            )

            wait = WebDriverWait(
                self.driver,
                timeout=timeout,
                poll_frequency=pollFrequency,
                ignored_exceptions=[
                    NoSuchElementException,
                    ElementNotVisibleException,
                    ElementNotSelectableException,
                ],
            )
            element = wait.until(
                EC.text_to_be_present_in_element_value((byType, locator), text)
            )
            self.log.info("Element appeared on the web page")
        except Exception:
            self.log.info("Element not appeared on the web page")
            print_stack()
        return element

    def webScroll(self, direction="up"):
        """
        NEW METHOD
        """
        if direction == "up":
            # Scroll Up
            self.driver.execute_script("window.scrollBy(0, -1000);")

        if direction == "down":
            # Scroll Down
            self.driver.execute_script("window.scrollBy(0, 1000);")

    def selectFile(self):
        # Method to Select a field where a file needs to be uploaded

        self.elementClick(locator="Add data", locatorType="link")

    def uploadFile(self, data):
        # Method to upload a file at the field where it is required. This is to be used in conjunction with Step 4 methods

        self.sendKeys(data=data, locator=".react-fine-uploader-file-input", locatorType="css")
        time.sleep(2)
        self.elementClick(locator="//button[contains(.,'SAVE')]", locatorType="xpath")

    def saveFile(self):
        # Method to save the file that has been uploaded on selected field
        self.elementClick(locator="//button[contains(.,'SAVE')]", locatorType="xpath")

    def enable_download_headless(self, browser, download_dir):
        browser.command_executor._commands["send_command"] = (
            "POST",
            "/session/$sessionId/chromium/send_command",
        )
        params = {
            "cmd": "Page.setDownloadBehavior",
            "params": {"behavior": "allow", "downloadPath": download_dir},
        }
        return browser.execute("send_command", params)

    def image_Compare(self, baseline, target):
        # Get Images required for comparison
        imageA = cv2.imread(
            str(Path(f"insightbox_testing/Data/Images/Input/{baseline}.png").absolute())
        )
        imageB = cv2.imread(
            str(Path(f"insightbox_testing/Data/Images/Input/{target}.png").absolute())
        )

        # convert images to greyscale
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2RGB)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2RGB)

        # compute the Structural Similarity Index (SSIM) between the two
        # images, ensuring that the difference image is returned
        (score, diff) = compare(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")

        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        varied_count = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        varied_count = imutils.grab_contours(varied_count)
        # loop over the contours
        for c in varied_count:
            # compute the bounding box of the contour and then draw the
            # bounding box on both input images to represent where the two
            # images differ
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)
        # show the output images
        result = cv2.imshow("Modified", imageB)
        self.log.info(result)
        self.screenShot(result)
        cv2.waitKey(0)
