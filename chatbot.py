from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer

# Creating chat bot instance
chatbot = ChatBot("Chat Bot")

chatbot = ChatBot(
    'College Enquiry Chat Bot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {
        'import_path': 'chatterbot.logic.BestMatch',
        'default_response': "I am sorry, I do not have response for your query. You can give this as feedback to improve further<br><br>You can ask me the details about: <br><br>Admission<br>Courses offered<br>College facilities<br>Fees structure<br>College events/announcements<br>Faculty members<br>Examinations<br><br>Go ahead and ask me a query.",
        'maximum_similarity_threshold': 0.90
        }
    ],
    database_uri='sqlite:///database.sqlite3'
)
trainer = ListTrainer(chatbot)

# Loads training data
training_data = open("static/training_data.txt").read().splitlines()

# Training the chat bot
trainer.train(training_data)

# training_corpus = ChatterBotCorpusTrainer(chatbot)

# training_corpus.train(
#     'chatterbot.corpus.english'
# )