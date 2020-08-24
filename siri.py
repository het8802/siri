import pyttsx3 
import speech_recognition as sr 
import datetime
import wikipedia 
import pyaudio
import webbrowser
import sys
from tkinter import *



chrome_dir = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

engine = pyttsx3.init('sapi5')

engine.setProperty('rate',150)

voices = engine.getProperty('voices')
engine.setProperty('voice',voices[1].id)


query_solved = False
energy_thres = 150

about_siri = {}
words = {}

categories = {}

categories['about_siri'] = about_siri
categories['words'] = words
    
ml_file = open('ml_file.txt', 'r')

con = False

for line in ml_file.readlines() :
    if '}' in line :
        con = False

    if con :
        key = line[:line.index(':')].strip()
        
        if '[' in line :
            categories[category][key] = [i.strip() for i in line[line.index(':')+1:].strip()[1:-1].split(',')]

        else :
            categories[category][key] = line[line.index(':')+1:].strip()

    if '{' in line :
        category = line[:line.index('=')].strip()
        con = True

ml_file.close()


def say(audio) :
    engine.say(audio)
    engine.runAndWait()


def wishClient() :
    hour = int(datetime.datetime.now().hour)

    if hour < 12 :
        say("good morning")

    elif 12 <= hour < 18 :
        say("good afternoon")

    elif 18 <= hour <24 :
        say("good evening")

def inputCommand() :

    rec = sr.Recognizer()
    # source = sr.Microphone()
    with sr.Microphone() as source :

        print("\nListening : ")
        rec.energy_threshold = energy_thres
        rec.phrase_threshold = 0.1
        
        audio = rec.listen(source)
        
        # rec.adjust_for_ambient_noise(source, duration=2)

        try :
            print("Recognizing your input... ")
            query = rec.recognize_google(audio,language='en-in')
            print("\nYou said :",query)
            return query.lower()

        except Exception :
            print("Pardon please : ")
            say("sorry sir, couldn't hear you properly")
            return "noquery"

def get_pos(category) :
    with open('ml_file.txt','r') as file :
        
        read_list = file.readlines()
        for i in range (len(read_list)) :
        
            if category in read_list[i] and '{' in read_list[i] :
                num = ''
                for j in range (read_list[i].index('=')+1, read_list[i].index('{')) :
                    num += read_list[i][j]

                return [int(num), i]


def edit_file(user_answer, keyword, category) :
    with open('ml_file.txt', 'r+') as file :
        read_list = file.readlines()
        
        length = len(read_list)
        pos = get_pos(category)

        read_list.insert(sum(pos), (" "*3) + keyword + ' : ' + user_answer + "\n" )
        file.truncate(0)

        for i in range(len(read_list)) :
            if '{' in read_list[i] and category in read_list[i] :
                read_list[i].split( str(pos[0]) ).join(pos[0]+1)

            file.write(read_list[i])


def google_search(search_query) :
    webbrowser.get(chrome_dir).open('google.com/search?q=' + search_query.strip().replace(' ','+'))


def changeEnergyThres(value) :
    sr.Recognizer().energy_threshold = value

def web_search(website_name, returnable) :
    website = [i for i in website_name.split(' ') if '.com' in i][0].strip()

    if returnable :
        return website

    else :
        webbrowser.get(chrome_dir).open(website)

def check_list(lst, query) :
    return [i for i in lst if i in query]


def query_not_solved(query) :
    say('I am so sorry sir, would you like to improve siri?')
    answer = inputCommand()

    if 'yes' in answer or 'ok' in answer :
        if check_list(categories['words']['talking_to_siri_words'], query)  :
            say('were you trying to know something about me sir?')
            answer2 = inputCommand()

            def qns2(query) :
                if 'yes' in answer2 :
                    say('okay sir, what was the keyword or what were you trying to know about me?')

                    keyword = inputCommand()
                    
                    try :
                        keyword[:4].replace('that','')

                    except Exception :
                        pass

                    if keyword in about_siri :
                        say('sir the keyword already exists in my directory!')

                    elif keyword == 'noquery' :
                        qns2(query)

                    else :
                        say('okay sir, how should I respond when this kind of query is encountered?')
                        user_answer = inputCommand()
                        prep_words = ['should', 'can', 'have', 'had', 'would', 'will']
                        say_synonyms = ['say','speak','tell']
                        
                        # to check if the user has said some english words apart from the main answer
                        
                        for i in prep_words :
                            for j in say_synonyms :
                                if 'you '+i+' '+j in user_answer :
                                    str(user_answer).replace('you '+i+' '+j,'').strip()

                        edit_file(user_answer, keyword, 'about_siri')

                elif 'no' in answer2 or check_list(categories['words']['negation'], answer2) :
                    say('ok sir, so should I search your query on google?')
                    answer3 = inputCommand()

                    if 'yes' in answer3 :
                        google_search(query)


                elif 'noquery' in keyword :
                    query_not_solved(query)

            qns2(query)

        else :
            def qns3(query) :
                say('ok sir, so should I search your query on google?')
                answer3 = inputCommand()

                if 'yes' in answer3 :
                    google_search(query)
                    edit_file('GOOGLE', query, 'general_search')


                elif answer3 == 'noquery' :
                    qns3(query)

                else :
                    pass

            qns3(query)

    elif 'no' in answer or check_list(categories['words']['negation'], answer) :
        say('okay sir, maybe we could improve it next time!')

    elif answer == 'noquery' :
        say('sir can you pardon please?')
        query_not_solved(query)

    else :
        say("sir, I didn't got an answer matching to my asked question.")
        query_not_solved(query)
                            

    

def mainProgram() :
    global query_solved
    query = inputCommand()

    if query != 'noquery' :
        print("Searching...")

    else :
        say("I didn't recognized what you said can you pardon please!")
        print('recognition failed!')

        mainProgram()


    if 'wikipedia' in query :
        query.replace('wikipedia','').strip()
        answer = wikipedia.summary(query,sentences=2)
        print(answer)

        say("According to wikipedia, "+answer)
        query_solved = True


    # if the user wants to know about siri

    elif 'you' in query or 'your' in query:
        for about_words in categories['about_siri'] :
            if about_words in query :
                say(categories['about_siri'][about_words])
                query_solved = True
                break


    elif [i for i in categories['words']['exit_status'] if i in query] :
        say('okay sir, exitting the program')
        query_solved = True
        sys.exit()

    # if the user wants to change energy threshold

    if not query_solved :
        for noise_words in categories['words']['noise_situation'] :
            if noise_words in query :
                say('your current energy threshold is ' + str(energy_thres))

                def re_answer() :
                    say('you can now set the value of energy threshold. Just say the value.')
                    answer = inputCommand()

                    try :
                        changeEnergyThres(answer)
                    
                    except Exception :
                        say('Just say the number of value you want to set!')
                        re_answer()

                re_answer()
                break
    
    # if the user wants to access photos from directory or internet

            
    if not query_solved :
        for photo_words in categories['words']['photo'] :
            if photo_words in query or photo_words+'s' in query :
                say('Are these your personal photographs saved in the device or should I search on net?')
                answer = inputCommand()

                if 'personal' in answer or 'device' in answer :
                    say('Sorry sir, the directory of photographs in not mentioned in the code!')

                elif 'net' in answer :
                    say('searching your query on google!')
                    answer_sub_part = query.replace(' ','+')
                    webbrowser.get(chrome_dir).open('google.com/search?q='+answer_sub_part)

                query_solved = True
                break

    if not query_solved :
        for web_words in categories['words']['open_website'] :
            if web_words in query and '.com' in query :
                say('Sir, do you want me to open this website or should I just search it on google?')
                answer = inputCommand()

                negation_list = check_list(categories['words']['negation'], answer)
                search_query = web_search(query, returnable = True)


                if ('yes' in answer and 'google' not in answer) or ('open' in answer and not negation_list) :
                    webbrowser.get(chrome_dir).open(search_query)

                elif 'google' in answer and not negation_list :
                    google_search(search_query)

                elif negation_list :
                    say('sir, on your command I am quitting the search')

                query_solved = True

            elif web_words in query and '.com' not in query :
                say('sir, you can type the website name in console or you can just say it!')
                say('what do you choose?')

                choice = inputCommand()
                if ('say' in choice or 'speak' in choice) and not check_list(categories['words']['negation'], choice) :
                    say('okay sir, go on I am listening')
                    answer = inputCommand()

                elif ('type' in choice or 'write' in choice) and not check_list(categories['words']['negation'], choice) :
                    say('okay sir, you can type your website name in the console!')
                    answer = input("Enter the name of website : ")

                else :
                    say("sorry sir did'nt get you")

                
                if '.com' in answer :
                    web_search(answer,returnable = False)

                elif '.com' not in answer :
                    web_search(answer+'.com', returnable = False)
                
                query_solved = True
                break

    if not query_solved :
        google_search(query)

        say('Taking you to google!')
        query_solved = True
    

    if query_solved :
        say('I think that you got the answer, is it?')
        answer = inputCommand()

        if 'yes' in answer :
            say('I am glad that I could help you sir! Have a nice day')
            query_solved = True

        elif check_list(categories['words']['negation'], answer) :
            query_solved = False
            query_not_solved(query)

        else :
            say('so I assume that your query is solved')

    else :
        say("sorry sir, I could not help you with this query")
        query_not_solved(query)

wishClient()
# say('hello sir, I am siri, how may I help you.')
# while True :
mainProgram()
