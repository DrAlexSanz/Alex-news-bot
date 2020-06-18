#This is the news bot main file

import requests
from bs4 import BeautifulSoup as bs
import redis
from Utils import password
import datetime

"""
The idea of this file is to create a scraper class, get the text of the website.
Then, look at the headlines and return a list of links corresponding to
these news. Finally, download these news and send them via email.

"""
# Keep in mind, a class is a blueprint, like in the car example.
# For a repetitive or grouped task I would use a function. Think a calculation.

class Scraper():
    def __init__(self, keywords, sites):
        self.sites = sites # Remove this and replace with string in line below
        self.markup = str([requests.get(site).text for site in sites]) # convert all to a string, not a list
        #Now I have the markup of the website, the text itself.
        # a get request is what the browser does, simply I'm not displaying the result, just getting it
        print(sites)
        self.keywords = keywords
        
    # With the previous block I have the text in a request object.
    # Now I have to parse it to see if I find the keywords
    def parse(self):
        soup = bs(self.markup, "html.parser")
        # So I get the markup from before and I pass it to bs.
        # The parser is because I will need to select certain elements,
        #Like tables or frames or whatever I want
        
        links = soup.findAll("a", {"class": "storylink"}) # a because <a href
        # I looked storylink up in the code.
        # If I wanted all the news from a site, that would be called sitestr
        
        self.saved_links = []
        for link in links:
            for keyw in self.keywords:
                if keyw in link.text:
                    self.saved_links.append(link)
                
        # Iterate through the links to see if I find the keyword. If so, save
        # Do it for all the keywords. Nested loops!! XD
        
    def store(self):
        r = redis.Redis(host = "localhost", port = 6379, db = 0) # Everything default
    # Don't forget to insall redis in my computer, not the client but the DB!!!  
    # And don't forget to run it!!
    #https://github.com/microsoftarchive/redis/releases/tag/win-3.2.100      
        for link in self.saved_links:
            r.set(link.text, str(link))
                # Use the link as a key to avoid duplicates. Chapuza but it works.
                # I'll scrape every hour for example, to catch new articles.
                # I will only send the email once or twice a day, that's why I save it.
                

    def email(self):
       # Now I can send my email :)
       r = redis.Redis(host = "localhost", port = 6379, db = 0)
       # Call it again because sending doesn't mean storing and vice-versa
       
       links = [str(r.get(k)) for k in r.keys()] # This is a select * from
       
       import smtplib
       from email.mime.multipart import MIMEMultipart
       from email.mime.text import MIMEText
       
       from_email = "alex.news.bot@gmail.com"
       to_email = "a.sanz.ull@gmail.com"
       
       msg = MIMEMultipart("alternative")
       
       msg["subject"] = "Alex's awesome news"
       
       msg["From"] = from_email
       msg["To"] = to_email
       
       html = """
               <h4> %s links you might find interesting today:</h4>
            
            %s
            
                      
       """ % (len(links), "<br></br>".join(links)) # Br is a line break tag.
       # The % above needs to be in the same line as the """!!!
       
       mime = MIMEText(html, "html")
       
       msg.attach(mime)
       
       try:
           mail = smtplib.SMTP("smtp.gmail.com", 587)
           mail.ehlo()
           mail.starttls()
           mail.login(from_email, password)
           mail.sendmail(from_email, to_email, msg.as_string())
           mail.quit()
           print("Email sent")
           
       except Exception as e:
           print("Something went wrong: %s", e)
           
       r.flushdb() # Empty every time
       
   
sites = ["https://news.ycombinator.com/", "https://news.ycombinator.com/news?p=2"]
        
        
a = Scraper(["Zoom", "Facebook", "GPT", "Goker", "1957"], sites)

if datetime.datetime.now().hour%2 == 0:
    a.parse()
    a.store()
if datetime.datetime.now().hour == 8:
    a.email()


print(a)