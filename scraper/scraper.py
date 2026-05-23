from playwright.sync_api import sync_playwright
import time
import json
'''
What this function does is that when we are scraping through the webpages, some unnecessary things load as well such as 
images of the icon of WUSA or their website fonts and medias etc, so we make a function that blocks loading these things when we're scraping
so it scraps faster and we save time. 
'''
def block_resources(route, request):
    blocked_types = ["image", "font", "media"]
    if request.resource_type in blocked_types:
        route.abort()
    else:
        route.continue_()

'''
How this scraper actually works
'''
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        page = context.new_page()

        context.route("**/*", block_resources)

        page.goto("https://clubs.wusa.ca/club_listings", wait_until="networkidle")
        time.sleep(3)

        club_listings = []

        #The while loop goes on until the end of all of the scraping
        while True:
            page.wait_for_selector(".card.card-body", timeout=10000)
            club_elements = page.locator(".card.card-body.mb-3.rounded-3").all()

            #Loops through each of the clubs shown on the club listing main website
            for club in club_elements:
                try:
                    club_name = club.locator(".col-lg-4 h4").inner_text()
                    active_term = club.locator(".col-lg-4 button").inner_text()

                    '''
                    WUSA website is weird, the main club listing webpage sometimes shows truncated description due to the length of the description
                    but we want the full description. So this try and except is fetching the "short-text" in case when fetching the "full-text"
                    something goes wrong, so at least we have a short text. 
                    '''
                    try:
                        short_desc = club.locator(".col-lg-8 .short-text").inner_text().strip()
                    except:
                        short_desc = "No description provided."

                    link_element = club.locator('a:has-text("Learn More")')
                    relative_url = link_element.get_attribute("href")
                    full_url = f"https://clubs.wusa.ca{relative_url}" if relative_url else None

                    #This just makes sure the description is the short description because if fetching the full description fails at least we still have this
                    description = short_desc

                    '''Because every club has a Learn More button that leads to the page of that club with the full description, 
                    we open up a new tab of that club and select their locator of where the "full-text" is and fetch that data.'''
                    if full_url:
                        club_page = context.new_page()
                        club_page.goto(full_url, wait_until="domcontentloaded")

                        try:
                            description_locator = club_page.locator("#full-text")
                            description_locator.wait_for(state="attached", timeout=3000)
                            description = description_locator.text_content().strip()
                            if not description:
                                description = club_page.locator("#short-text").text_content().strip()

                        except Exception:
                            pass

                        club_page.close()

                    '''This parts prints the data out for me for debug purpose and also adds the information into the club_listings list as a dictionary'''
                    print(f"Club: {club_name.strip()} | Term: {active_term.strip()} | Description: {description.strip()}")
                    club_listings.append({"name": club_name.strip(), "term": active_term.strip(), "info": description.strip(), "link": full_url if full_url else ""})
                except Exception:
                    continue

            '''When we're done with this page, we click the Next button and head to the next page and repeat what happened up there'''
            next_button = page.locator('a[rel="next"]:has-text("Next")')
            if next_button.count() > 0 and next_button.is_visible():
                print("Going to next page")
                next_button.click()
                page.wait_for_load_state("networkidle")
                time.sleep(2)
            else:
                #When there's no more pages left we just break to exit the while loop
                print("No more pages")
                break

        '''Dump everything in the JSON file'''
        with open("club_list.json", "w") as file:
            json.dump(club_listings, file, indent=4, ensure_ascii=False)
        print("Data written to json")

        context.close()
        browser.close()

if __name__ == "__main__":
    main()