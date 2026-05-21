from playwright.sync_api import sync_playwright
import time
import json

def block_resources(route, request):
    blocked_types = ["image", "font", "media"]
    if request.resource_type in blocked_types:
        route.abort()
    else:
        route.continue_()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        page = context.new_page()

        page.route("**/*", block_resources)

        page.goto("https://clubs.wusa.ca/club_listings", wait_until="networkidle")
        time.sleep(3)

        club_listings = []
        page_num = 1

        while True:
            page.wait_for_selector(".card.card-body", timeout=10000)
            club_elements = page.locator(".card.card-body.mb-3.rounded-3").all()
            for club in club_elements:
                try:
                    club_name = club.locator(".col-lg-4 h4").inner_text()
                    active_term = club.locator(".col-lg-4 button").inner_text()
                    description = club.locator(".col-lg-8 .short-text").inner_text()

                    link_element = club.locator('a:has-text("Learn More")')
                    relative_url = link_element.get_attribute("href")
                    full_url = f"https://clubs.wusa.ca{relative_url}" if relative_url else None


                    print(f"Club: {club_name.strip()} | Term: {active_term.strip()} | Description: {description.strip()}")
                    club_listings.append({"name": club_name.strip(), "term": active_term.strip(), "info": description.strip(), "link": full_url.strip()})
                except Exception as e:
                    continue

            next_button = page.locator('a[rel="next"]:has-text("Next")')
            if next_button.count() > 0 and next_button.is_visible():
                print("Going to next page")
                next_button.click()
                page.wait_for_load_state("networkidle")
                time.sleep(2)
                page_num += 1
            else:
                print("No more pages")
                break

        with open("club_list.json", "w") as file:
            json.dump(club_listings, file, indent=4, ensure_ascii=False)
        print("Data written to json")

        context.close()
        browser.close()

if __name__ == "__main__":
    main()