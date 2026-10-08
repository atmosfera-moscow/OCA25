import telebot
import config
from telebot import types

bot = telebot.TeleBot(config.botToken)

lastMarkupMessage = dict()
userState = dict()
# 0 - Ничего
# 1 - Изменить рейтинг
# 2 - Послать заморочку
# 3 - Установить коды команд

PlanText = "План дня"
RatingText = "Рейтинг"
SetRatingText = "Установить рейтинг"
ChangeRatingText = "Изменить рейтинг"
SendZamorochkiText = "Прислать заморочку"
StartVotingText = "Начать голосование"
EndVotingText = "Закончить голосование"
SeeVotingResultsText = "Посмотреть результаты голосования"
AllZamorochkiText = "Посмотреть все заморочки"
AlreadyVotedText = "Вы уже проголосовали."
VotingText = "Проголосуйте за понравившуюся команду:"
VotedText = "Ваш голос принят."
HelloText = """
Добро пожаловать!
Это бот осеннего слёта «Атмосферы». Здесь всё под контролем: информация, рейтинги, выборы и тайные операции.

📝 План дня:
Каждая минута на счету.
Здесь ты найдёшь актуальное расписание — ничего не пропусти.

👍 Рейтинг:
Баллы — это власть.
Следи, кто поднимается наверх, а кто теряет влияние.

💭 Голосование:
Город ждёт твоего решения.
Здесь ты можешь отдать голос за лучшую визитку и лучшую зону банды. 
Введи пароль, который появится рядом с названием твоей команды, и действуй.

🔊 Прислать заморочку:
Хочешь усилить позиции своей банды? Отправляй сюда заморочки, и не забудь указать название банды.

Следи за новостями — город живёт по своим правилам.
"""

ratingArr = ["0", "0", "0", "0", "0", "0", "0", "0", "0"]
TeamNames = ["Ruza Chupeps Fam", "Crips Clouds", "Only Face Sectum", "Blink Blood", "Ruza Nostra", "Влажный закон", "La rosa ferro", "Клан Пламени", "Чикокеры"]
alreadyVoted = []
isVoting = False
votingArr = [0, 0, 0, 0, 0, 0, 0, 0, 0]
votingCodes = ["", "", "", "", "", "", "", "", ""]
VotingStrings = [str(i) for i in range(len(TeamNames))]

Oleg = "AShephardGD"
Amina = "miamin4"
Marat = "mirgazev"
ZamorochkiGroupID = -1002576113604

keyPlan = types.KeyboardButton(PlanText)
keyRating = types.KeyboardButton(RatingText)
keyChangeRating = types.KeyboardButton(ChangeRatingText)
keyStartVoting = types.KeyboardButton(StartVotingText)
keyEndVoting = types.KeyboardButton(EndVotingText)
keySeeVotingResults = types.KeyboardButton(SeeVotingResultsText)
keySendZamorochki = types.KeyboardButton(SendZamorochkiText)

mainMenu = types.ReplyKeyboardMarkup(True)
mainMenuAdmin = types.ReplyKeyboardMarkup(True)
mainMenu.add(keyPlan, keyRating, keySendZamorochki)
mainMenuAdmin.add(keyPlan, keyRating, keyChangeRating, 
                  keyStartVoting, keyEndVoting, keySeeVotingResults,
                  keySendZamorochki)

teamKeys = [types.InlineKeyboardButton(TeamNames[i], callback_data=str(i)) for i in range(len(TeamNames))]
teamVotingKeyboards = [types.InlineKeyboardMarkup() for i in range(len(TeamNames))]

ending = types.InlineKeyboardMarkup()
yes = types.InlineKeyboardButton("Да", callback_data="yes")
no = types.InlineKeyboardButton("Нет", callback_data="no")
ending.add(yes)
ending.add(no)

for i in range(len(TeamNames)):
    for j in range(len(TeamNames)):
        if i != j:
            teamVotingKeyboards[i].add(teamKeys[j])

@bot.message_handler(func=lambda message: message.text == PlanText)
def plan(message):
    userID = message.from_user.id
    try:
        with open("images/plan.png", "rb") as img:
            bot.send_photo(userID, img)
    except Exception as e:
        print("plan: send_photo")
        print(e)
        try:
            bot.send_message(userID, "Плана пока нет.")
        except Exception as e1:
            print("plan: no phono")
            print(e)

@bot.message_handler(func=lambda message: message.text == RatingText)
def rating(message):
    userID = message.from_user.id
    try:
        with open("images/map.jpg", "rb") as img:
            bot.send_photo(userID, img, ratingToString())
    except Exception as e:
        print("rating: send_photo")
        print(e)

@bot.message_handler(func=lambda message: message.text == ChangeRatingText and isAdmin(message))
def askForRating(message):
    try:
        userID = message.from_user.id
        userState[userID] = 1
        bot.send_message(userID, "Введите рейтинг в формате:\n1-1\n2-2...")
    except Exception as e:
        print("askForRating")
        print(e)

@bot.message_handler(func=lambda message: userState.get(message.from_user.id) == 1 and isAdmin(message))
def setRating(message):
    try:
        userID = message.from_user.id
        userState[userID] = 0
        updateRating = list(map(lambda x: "".join(x.split()).split("-"), message.text.split("\n")))
        updateRating = list(map(lambda x: [int(x[0]) - 1, x[1]], updateRating))
        for i in updateRating:
            ratingArr[i[0]] = i[1]
    except Exception as e:
        print("setRating: set rating")
        print(e)
        try:
            bot.send_message(userID, "Формат не соответствует.")
            return
        except Exception as e1:
            print("setRating: Exception: send_message")
            print(e1)
            return
    bot.send_message(userID, "Установленный рейтинг:\n" + ratingToString())

@bot.message_handler(func=lambda message: message.text == StartVotingText and isAdmin(message))
def getVotingCodes(message):
    global isVoting
    userID = message.from_user.id
    if isVoting:
        try:
            bot.send_message(userID, "Голосование уже запущено. Коды команд:\n" + codesToString())
        except Exception as e:
            print("getVotingCodes: isVoting")
            print(e)
    else:
        try:
            bot.send_message(userID, "Введи коды команд в виде:\nНуль\nОдин\nДва...")
            userState[userID] = 3
        except Exception as e:
            print("getVotingCodes: isNotVoting")
            print(e)

@bot.message_handler(func=lambda message: userState.get(message.from_user.id) == 3 and isAdmin(message))
def startVoting(message):
    userID = message.from_user.id
    userState[userID] = 0
    codes = message.text.split("\n")
    if len(codes) != 9:
        try:
            bot.send_message(userID, "Формат не соответствует.")
        except Exception as e:
            print("startVoting: no")
            print(e)
    else:
        global isVoting
        isVoting = True
        try:
            global votingArr
            global votingCodes
            votingCodes = codes
            bot.send_message(userID, "Голосование запущено. Коды команд:\n" + codesToString())
            votingArr = [0 for i in range(len(votingArr))]
        except Exception as e:
            print("startVoting: yes")
            print(e)

@bot.message_handler(func=lambda message: message.text == EndVotingText and isAdmin(message))
def isEndVoting(message):
    userID = message.from_user.id
    global isVoting
    if isVoting:
        try:
            m = bot.send_message(userID, "Вы действительно хотите завершить голосование?", reply_markup=ending)
            lastMarkupMessage[userID] = m.message_id
        except Exception as e:
            print("isEndVoting: isVoting")
            print(e)
    else:
        try:
            bot.send_message(userID, "Голосование уже завершилось. Результаты:\n" + votingResultsToString())
        except Exception as e:
            print("isEndVoting: not")
            print(e)

@bot.callback_query_handler(func=lambda call: call.data == "yes")
def endVoting(message):
    userID = message.from_user.id
    global isVoting
    try:
        isVoting = False
        bot.send_message(userID, "Голосование завершено. Результаты:\n" + votingResultsToString())
        bot.edit_message_text("Вы действительно хотите завершить голосование?", userID, lastMarkupMessage[userID], reply_markup=None)
    except Exception as e:
        print("endVoting")
        print(e)

@bot.callback_query_handler(func=lambda call: call.data == "no")
def notEndVoting(message):
    userID = message.from_user.id
    try:
        bot.edit_message_text("Вы действительно хотите завершить голосование?", userID, lastMarkupMessage[userID], reply_markup=None)
    except Exception as e:
        print("notEndVoting")
        print(e)

@bot.message_handler(func=lambda message: message.text == SeeVotingResultsText and isAdmin(message))
def seeVotingResults(message):
    userID = message.from_user.id
    try:
        bot.send_message(userID, "Результаты голосования:\n" + votingResultsToString())
    except Exception as e:
        print("seeVotingResults")
        print(e)

@bot.message_handler(func=lambda message: message.text == SendZamorochkiText)
def sendZamorochki(message):
    userID = message.from_user.id
    try:
        bot.send_message(userID, "Подпиши название команды.")
        userState[userID] = 2
    except Exception as e:
        print("sendZamorochki")
        print(e)

@bot.message_handler(func=lambda message: userState.get(message.from_user.id) == 2, content_types=['photo'])
def getZamorochki(message):
    userID = message.from_user.id
    if not message.caption:
        try:
            bot.send_message(userID, "А где подпись?")
        except Exception as e:
            print("getZamorochki: no text")
            print(e)
    else:
        try:
            bot.forward_message(ZamorochkiGroupID, userID, message.message_id)
            bot.send_message(userID, "Ваша заморочка принята.")
            userState[message.from_user.id] = 0
        except Exception as e:
            print("getZamorochki: forward")
            print(e)

@bot.message_handler(func=lambda message: message.text in votingCodes and isVoting)
def sendVoting(message):
    for i in range(len(votingCodes)):
        if votingCodes[i] == message.text:
            getVote(message, teamVotingKeyboards[i])

def getVote(message, reply_markup):
    userID = message.from_user.id
    if userID in alreadyVoted:
        try:
            bot.send_message(userID, AlreadyVotedText)
        except Exception as e:
            print("voting: alreadyVoted")
            print(e)
    else:
        try:
            if lastMarkupMessage.get(userID):
                bot.delete_message(userID, lastMarkupMessage[userID])
        except Exception as e:
            print("voting: delete_message")
            print(e)
        try:
            m = bot.send_message(userID, VotingText, reply_markup=reply_markup)
            lastMarkupMessage[userID] = m.message_id
        except Exception as e:
            print("voting: send_message")
            print(e)

@bot.callback_query_handler(func=lambda call: call.data in VotingStrings)
def voteCallback(call):
    for i in range(len(VotingStrings)):
        if VotingStrings[i] == call.data:
            vote(call, i)

def vote(call, index):
    userID = call.from_user.id
    if userID in alreadyVoted:
        try:
            bot.edit_message_text(AlreadyVotedText, userID, lastMarkupMessage[userID], reply_markup=None)
        except Exception as e:
            print("vote1: alreadyVoted: edit_message_text")
            print(e)
            try:
                bot.send_message(userID, AlreadyVotedText)
            except Exception as e1:
                print("vote1: alreadyVoted: send_message")
                print(e1)
    else:
        try:
            votingArr[index] = votingArr[index] + 1
            alreadyVoted.append(userID)
            bot.edit_message_text(VotedText, userID, lastMarkupMessage[userID], reply_markup=None)
        except Exception as e:
            print("vote1: voting: edit_message_text")
            print(e)
            try:
                bot.send_message(userID, VotedText)
            except Exception as e1:
                print("vote1: voting: send_message")
                print(e1)

@bot.message_handler(func=lambda message: True)
def sendWelcomeMessage(message):
    username = message.from_user.username
    userID = message.from_user.id
    try:
        if username == Oleg:
            bot.send_message(userID, "Привет, Олег", reply_markup=mainMenuAdmin)
        elif username == Amina:
            bot.send_message(userID, "Привет, Амина.", reply_markup=mainMenuAdmin)
        elif username == Marat:
            bot.send_message(userID, "Привет, Марат.", reply_markup=mainMenuAdmin)
        else:
            bot.send_message(userID, HelloText, reply_markup=mainMenu)
    except Exception as e:
        print("sendWelcomeMessage")
        print(e)

def ratingToString():
    res = TeamNames[0] + " - " + ratingArr[0]
    for i in range(len(ratingArr[1:])):
        res = res + "\n" + TeamNames[i+1] + " - " + ratingArr[i+1]
    return res

def isAdmin(message):
    return (message.from_user.username == Marat or
            message.from_user.username == Oleg or
            message.from_user.username == Amina)

def votingResultsToString():
    res = TeamNames[0] + " - " + str(votingArr[0])
    for i in range(len(TeamNames[1:])):
        res = res + "\n" + TeamNames[i+1] + " - " + str(votingArr[i+1])
    return res

def codesToString():
    res = TeamNames[0] + " - " + votingCodes[0]
    for i in range(len(TeamNames[1:])):
        res = res + "\n" + TeamNames[i+1] + " - " + votingCodes[i+1]
    return res

print("Start OCA bot")
bot.infinity_polling()