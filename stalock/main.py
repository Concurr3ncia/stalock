import json
import os
import requests
from playwright.sync_api import sync_playwright
from termcolor import colored

def main():
    # Clear the console based on the operating system
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load the JSON file containing the URLs
    try:
        with open('stalock/resources/data.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: {e}")
        return

    # List of phrases that indicate a user was not found or the page does not exist
    not_found_phrases = [
        "no está disponible", "pagina no encontrada", "Esta página no está disponible.",
        "no existe", "usuario no encontrado", "bad request", "no se encontró", "este perfil no existe", "user not found", 
        "not found", "invalid username"
    ]
    
    print("""
███████╗████████╗ █████╗ ██╗      ██████╗  ██████╗██╗  ██╗
██╔════╝╚══██╔══╝██╔══██╗██║     ██╔═══██╗██╔════╝██║ ██╔╝
███████╗   ██║   ███████║██║     ██║   ██║██║     █████╔╝ 
╚════██║   ██║   ██╔══██║██║     ██║   ██║██║     ██╔═██╗ 
███████║   ██║   ██║  ██║███████╗╚██████╔╝╚██████╗██║  ██╗
╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝
                                                          
    """)

    # Prompt the user to enter a username
    username = input("> Enter the username or ID: ")

    # Use Playwright to open the browser and check each URL
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        for key, value in data.items():
            url = value["url"].format(username)  # Format the URL with the username
            
            # Variables to store the validity of requests and playwright
            valid_requests = False
            valid_playwright = False

            # Check with Playwright first
            try:
                page = context.new_page()
                page.goto(url)
                page.wait_for_timeout(1000)  # Wait for the page to load

                # Get the content of the page and convert it to lowercase for comparison
                page_content = page.content().lower()

                # Check if any of the not found phrases are present in the page content
                found = any(phrase.lower() in page_content for phrase in not_found_phrases)

                if not found and username.lower() in page_content:
                    valid_playwright = True  # Set to True if username is found

            except Exception:
                pass
            finally:
                page.close()  # Ensure the page is closed

            # Additional verification using requests
            try:
                response = requests.get(url)
                if response.ok:
                    valid_requests = True  # Set to True if username is found

            except Exception:
                pass

            # Determine the result based on the validity of requests and Playwright
            if valid_requests and valid_playwright:
                print(colored(f"🟢 [Both Valid] {key}: {url} - Requests and Playwright both found the user.", 'green'))
            elif not valid_requests and valid_playwright:
                print(colored(f"🟡 [Requests Invalid, Playwright Valid] {key}: {url} - User found only on Playwright.", 'yellow'))
            elif valid_requests and not valid_playwright:
                print(colored(f"🟠 [Requests Valid, Playwright Invalid] {key}: {url} - User found only on Requests.", 'yellow'))  # Cambia a 'yellow'
            else:
                print(colored(f"🔴 [Both Invalid] {key}: {url} - User not found on both Requests and Playwright.", 'red'))

        context.close()  # Close the browser context
        browser.close()  # Close the browser
        print("Finish.")

if __name__ == "__main__":
    main()  # Execute the main function
