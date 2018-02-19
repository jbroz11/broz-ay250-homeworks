import pyaudio
import wave
import houndify
import smtplib
import scrapy
import random
import sys
import os
import logging
import my_credentials as mc

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from scrapy.crawler import CrawlerProcess
from IPython.display import clear_output

# Disable scrapy log output
logging.getLogger('scrapy').propagate = False
#####################################################################
# This section inlcudes functions for transcribing audio to txt     #
#####################################################################


def audio_to_txt(record_seconds=5):
    '''
    Whole enchilada. Prompt and get audio request and then send it to
    houndify to be transribed to string. Only argument is *record_seconds
    which determines how many seconds to record audio for (default is 5).
    '''

    # Get audio request
    audio_data_list = get_audio_clip(record_seconds)

    # Credentials for houndify
    clientKey = mc.houndify_clientKey
    clientId = mc.houndify_clientId
    userId = mc.houndify_userId

    # Send audio file to houndify and get back transcription
    client = houndify.StreamingHoundClient(clientId, clientKey, userId)
    client.start(MyListener())
    client.fill(b"".join(audio_data_list))
    result = client.finish()
    txt = result["AllResults"][0]["WrittenResponse"]
    txt = txt.replace("ah no", "")  # Get this a lot for some reason

    clear_output()  # making notebook presentation nicer

    return txt


# This will be used to transcribe audio data to txt vi houndify.
class MyListener(houndify.HoundListener):
    '''
    Extension of HoundListener, which does the simplest houndify task:
    taking an audio file and transcribing it to text.

    HoundListener is an abstract base class that defines the callbacks
    that can be received while streaming speech to the server.
    '''

    def onFinalResponse(self, response):
        '''
        onFinalResponse is fired when the server has completed processing
        the query and has a response.  'response' is the JSON object (as
        a Python dict) which the server sends back.
        '''
        print("Final response: " + str(response))

    def onError(self, err):
        '''
        onError is fired if there is an error interacting with the server.
        It contains the parsed JSON from the server.
        '''
        print("Error: " + str(err))


def get_audio_clip(record_seconds, chunk=1024):
    '''
    Records audio  and returns recorded audio data as a list of chunked binary
    data.

    parameters:
    -----------
    record_seconds: number of seconds to record.
    chunk = 1024: rate with which to chunk the recording.

    Taken directly from Berkeley AY250 class notes.
    '''

    # Required settings for houndify

    channels = 1
    audio_format = pyaudio.paInt16
    rate = 16000  # Can also be set to 8 kHz

    p = pyaudio.PyAudio()

    print("What can I help you with?\n* start recording")
    stream = p.open(format=audio_format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    all = []
    for i in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        all.append(data)

    clear_output()  # making notebook presentation nicer
    print("* done recording")
    stream.close()
    p.terminate()

    return all


# Didn't end up using this function while answering the problem, but it's
# useful for debugging.
def write_audio_to_wav(audio_data_list, filename="request.wav"):
    '''
    Takes as input a list of recorded audio data (for example, as returned
    by get_audio_clip) and then saves it as a .wav file called *filename*.

    parameters:
    -----------
    audio_data_list: list of audio data.
    filename = 'request.wav': filename to save .wav file as.

    Taken directly from Berkeley AY250 class notes.
    '''
    # Required settings for houndify

    channels = 1
    audio_format = pyaudio.paInt16
    rate = 16000  # Can also be set to 8 kHz

    p = pyaudio.PyAudio()

    data = b"".join(audio_data_list)
    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(audio_format))
    wf.setframerate(rate)
    wf.writeframes(data)
    wf.close()

    return wave.open(filename)


#####################################################################
# This section defines a function for sending email                 #
#####################################################################


def send_email(subject, body):
    '''
    Generates and sends an email.

    Parameters:
    -----------
    subject: string to be placed in subject field.
    body: string to be placed in the body of the email.
    '''

    # Credentials for gmail
    user = mc.gmail_address
    passwd = mc.gmail_passwd

    # Setup smtp server
    smtp_port = 587
    smtp_host = 'smtp.gmail.com'
    server = smtplib.SMTP()
    server.connect(smtp_host, smtp_port)
    server.ehlo()
    server.starttls()
    server.login(user, passwd)

    # Set up 'to' and 'from' fields for email
    # For now we just send an email to ourselves
    fromaddr = user
    toaddr = user

    # Format data accoring to MIME standard
    msg = MIMEMultipart()
    msg["From"] = fromaddr
    msg["To"] = toaddr
    msg["Subject"] = subject
    msg.attach(MIMEText(body))
    msg.attach(MIMEText('\n-Monty', 'plain'))

    # Here's the action that actually sends the email
    server.sendmail(user, toaddr, msg.as_string())
    print("* Email sent.")


#####################################################################
# This section defines a function for parsing strings into binary   #
# operations.                                                       #
#####################################################################


def binary_operation(operation):
    '''
    Given a binary operation described in a string (i.e. '2 times 3')
    compute the result and return it (i.e. '2 times 3' would return 6).

    Valid Operations:
    -----------------
    multiplictation: "times";
    division: "divided by";
    addition: "plus";
    subtraction: "minus";
    modulo: "mod".
    '''

    # Note: speech-to-txt isn't very good at correctly spelling 'mod'
    op_dict = {"times": lambda x,y: x * y,
               "divided by": lambda x, y: x / y,
               "plus": lambda x,y: x + y,
               "minus": lambda x,y: x - y,
               "mod": divmod}

    operation = operation.replace("-", "minus ")
    op_list = operation.split(" ")

    # Some limited amount of user error prevention. If this condition isn't
    # fulfilled code will break in proceeding lines.
    if len(op_list) < 3:
        print("Sorry, I don't recognize that operation.")
        return

    operand1, operand2 = op_list[0], op_list[-1]
    operator = " ".join(op_list[1:-1])

    try:
        f = op_dict[operator]
    except KeyError:
        # Operator isn't in opt_dict
        print("Sorry, I don't recognize that operation.")
        return

    try:
        operand1 = float(operand1)
        operand2 = float(operand2)
    except ValueError:
        # For simplicity we require that operands have the form of e.g.
        # '1' as opposed to 'one'. This will check for that problem and
        # also general speech-to-text parsing issues or user error.
        print("Sorry, I don't understand some of your operands. ",
              "Please make sure that you are telling Monty e.g. "
              "'one point zero' which will return '1' or '1.0' instead of ",
              "'one' which will return 'one'.")

    result = f(operand1, operand2)
    print(operation + " = " + str(result))

    return result


#####################################################################
# This section defines functions for finding a joke on the web      #
#####################################################################


# It seems like a little bit of overkill to scrape a website every
# time a joke is requested. But I just wanted to demonstrate/practice
# the capability. Maybe it makes more sense to just grab a single joke
# randomly from the website or something like that? Also, the website
# that I'm scraping isn't the best choice either since there aren't
# a ton of jokes although presumably they're regularly updated.

class joke_getter:
    '''
    On init, run the spider JokesSpider and save the results to a txt file.

    Then method get_joke loads the txt file and grab a single joke randomly,
    which is returned as a string.
    '''

    def __init__(self, run_crawler=True):
        if run_crawler:
            # Initialize the crawler with pipline for saving output as txt file
            process = CrawlerProcess({'ITEM_PIPELINES':
                                     {'monty.TxtWriterPipeline': 100}})

            # Set the crawler to use the JokesSpider spider
            process.crawl(JokesSpider)

            # start the process
            process.start()

    def get_joke(self):
        '''
        Return a random joke from one those returned by the scraper when
        initialized.
        '''

        with open("items.txt", "r") as file:
            jokes_list = []
            for line in file.readlines():
                # Sometimes the crawler grabs an empty string
                if len(line) > 2:
                    # Doesn't fomat strings with this char well
                    if "\xa0" not in line:
                        line = line.replace("\u2028", "")
                        line = line.replace("\n", "")
                        jokes_list.append(line)

        return random.choice(jokes_list)


class JokesSpider(scrapy.Spider):
    '''
    A web scraper for the reader's digest webpage jokes section:
    www.rd.com/jokes/
    '''

    name = "jokes"
    start_urls = ["https://www.rd.com/jokes/",
                  "https://www.rd.com/jokes/animal/",
                  "https://www.rd.com/jokes/bad-puns/",
                  "https://www.rd.com/jokes/bar/",
                  "https://www.rd.com/jokes/cat/",
                  "https://www.rd.com/jokes/coffee-jokes/",
                  "https://www.rd.com/jokes/computer/",
                  "https://www.rd.com/jokes/corny/",
                  "https://www.rd.com/jokes/dad/",
                  "https://www.rd.com/jokes/weight-loss-jokes/",
                  "https://www.rd.com/jokes/dog-puns/",
                  "https://www.rd.com/jokes/dog/",
                  "https://www.rd.com/jokes/food-jokes/",
                  "https://www.rd.com/jokes/one-liners/",
                  "https://www.rd.com/jokes/science-jokes/",
                  "https://www.rd.com/jokes/school-jokes/"
                  ]
    custom_settings = {'LOG_LEVEL': 'CRITICAL'}

    def parse(self, response):
        for joke in response.css("div.content-wrapper"):
            yield {"joke": joke.css("p::text").extract()}


# define a pipeline so that the output of the crawl is saved to the txt file
# items.txt
class TxtWriterPipeline(object):
    def __init__(self):
        self.file = open('items.txt', 'w')

    def process_item(self, item, spider):
        self.file = open('items.txt', 'a')
        # Some string formatting
        line = " ".join(item["joke"])
        line = line.replace("\n", "") + "\n"
        self.file.write(line)
        self.file.close()
        return item


#####################################################################
# Run program                                                       #
#####################################################################


if __name__ == "__main__":

    # Prompt user ask a question and let them know when recording starts.
    # Run speech-to-txt with houndify and return results.
    # Provide the option to change the number of record seconds by using
    # a command line argument.
    if len(sys.argv) > 1:
        request = audio_to_txt(int(sys.argv[1]))
    else:
        request = audio_to_txt()

    # In the following, I will initiate a response based on the string
    # contained in request. It seems easy to go down a rabbit hole
    # trying to intelligently interpret exactly what the user is asking,
    # so for now I am only going to ensure that this works provided that
    # the user's question has been transcribed to text in the exact
    # format as described in the problem description.

    request = request.lower()  # convert to lowercase
    # strip off first word since speech-to-text has trouble with 'monty'
    request = request.split(" ", 1)[1]

    s = request.split("email me with subject")
    if len(s) > 1:
        # Note: this won't work correctly if 'and body' shows up more than
        # once in *request*.
        subject, body = s[1].split("and body")
        send_email(subject, body)
        sys.exit()

    s = request.split("calculate ")
    if len(s) > 1:
        # Another reminder, this will fail if request looks like: 'two times
        # three' instead of '2 times 3'. To avoid this make sure you ask
        # Monty something like 'two point zero times three point zero'.
        binary_operation(s[1])
        sys.exit()

    if "tell me a joke" in request:
        # Checks to see if we've already crawled for jokes
        if os.path.isfile("items.txt"):
            jokes = joke_getter(run_crawler=False)
        else:
            jokes = joke_getter()

        print(jokes.get_joke())
        sys.exit()

    # If Monty can't parse the request, just return a joke instead.
    print("Sorry, I didn't understand your request. Here's a joke instead:")
    print()

    # Checks to see if we've already crawled for jokes
    if os.path.isfile("items.txt"):
        jokes = joke_getter(run_crawler=False)
    else:
        jokes = joke_getter()

    print(jokes.get_joke())
