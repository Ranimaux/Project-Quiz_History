
### Projet Histoire Quiz ###
## By Jérôme HUON Student ##

import json
import random
import difflib

## Création d'une class objet Question permettant l'initiation des prompt, answer et choices
class Question:
    def __init__(self, prompt, answer, choices=None):
        self.prompt = prompt
        self.answer = answer
        self.choices = choices if choices else []

## Création d'une class objet Quizz qui permet le fonctionnement global du script
class Quizz:
    ## Constructeur qui initialise les question, le compteur de score qu'ainsi un tableau pour les réponses fausses.
    def __init__(self, questions):
        self.questions = questions
        self.score = 0
        self.incorrectAnswers = []

    ## Méthode permettant de formater les questions et réponses de l'utilisateur.
    ## Et vérifie si la réponse donner correspond à la réponse attendu sinon le stock dans le tableau la réponse attendu de la question qui correspond.
    def processQuizz(self):
        for question in self.questions:
            response = input(question.prompt).strip().lower()
            answerCorrect = question.answer.strip().lower()
            
            similarity = difflib.SequenceMatcher(None, response, answerCorrect).ratio
            
            if similarity > 0.8:
                self.score += 1
            else:
                self.incorrectAnswers.append((question.prompt, question.answer))
                
        return self.score

    ## Méthode similaire que processQuizz mais version QCM ou l'utilisateur doit choisir entre A, B, C et D qui sont formater au format ACSII
    ## Et si l'utilisateur a faux, note dans le tableau la réponse attendu de la question qui correspondait.
    def processQCM(self):
        for question in self.questions:
            print(question.prompt)
            
            for i, choice in enumerate(question.choices):
                decode = chr(65 + i).encode("utf-8").decode("utf-8")
                print(f"{decode}. {choice}")
            
            response = input("Votre réponse (A, B, C, D): ").upper()
            
            while response not in ['A', 'B', 'C', 'D']:
                response = input("Réponse invalide ! Veulliez choisir entre A, B, C ou D: ").upper()
            
            try:
                indexResponse = ord(response.encode('utf-8').decode('utf-8')) - 65
                response = question.choices[indexResponse].strip().lower()
            except (ValueError, IndexError):
                response = ""
                print(f"ERREUR, durant le traitement de la réponse")
            
            answerCorrect = question.answer.strip().lower()
            
            
            if response == answerCorrect:
                self.score += 1
            else:
                self.incorrectAnswers.append((question.prompt, question.answer))

        return self.score

    ## Méthode qui permet l'affichage du moment a la fin du script qui indique les question avec les bonne réponse où l'utilisateur avait faux.
    ## Si l'utilisateur avait eu juste a toutes les questions.
    def showIncorrectAnswers(self):
        if self.incorrectAnswers:
            print("\nVous avez eu faux à une ou plusieurs questions suivantes :")
            for prompt, answer in self.incorrectAnswers:
                print(f"Question : {prompt}")
                print(f"Réponse correcte : {answer}")
        else:
            print("\nBravo ! Vous avez tout juste.")

## Cette fonction permet la lecture des fichiers .JSON où sont stocker les prompt, answers et choices.
def readQuestions(file):
    with open(file, "r", encoding="utf-8") as f:
        questions = json.load(f)
        return [Question(q["prompt"], q["answer"], q.get("choices")) for q in questions]

## Cette fonction permet de faire un choix alétoire d'une des question dans le fichier .JSON dans un nombre de 10.
def randomQuestion(questions, nbrQuestion=10):
    return random.sample(questions, min(nbrQuestion, len(questions)))

## Cette fonction, formate le menu principal du script.
def menu():
    print("Veulliez sélectionner une difficulté :")
    print("1 - Facile (QCM)")
    print('------')
    print("W.I.P")
    print('------')
    print("2 - Moyen (QCM)")
    print("3 - Difficile")
    print("4 - Extreme")

def main():
    print("Bienvenue au Quiz d'Histoire !")
    print()
    
    menu()
    choix = input("").strip()
        
        
    if choix == "1":
                listQuestion = readQuestions('histSimple.json')
                questionSelected = randomQuestion(listQuestion, 10)
                quizz = Quizz(questionSelected)
                scoreTotal = quizz.processQCM()
    elif choix == "2":
                listQuestion = readQuestions('histMid.json')
                questionSelected = randomQuestion(listQuestion, 10)
                quizz = Quizz(questionSelected)
                scoreTotal = quizz.processQCM()
    elif choix == "3":
                listQuestion = readQuestions('histDiff.json')
                questionSelected = randomQuestion(listQuestion, 10)
                quizz = Quizz(questionSelected)
                scoreTotal = quizz.processQuizz()
    elif choix == "4":
                listQuestion = readQuestions('histXtreme.json')
                questionSelected = randomQuestion(listQuestion, 10)
                quizz = Quizz(questionSelected)
                scoreTotal = quizz.processQuizz()
    print()
    print(f"Votre score total est de {scoreTotal}/{10}")
    quizz.showIncorrectAnswers()

if __name__ == "__main__":
    main()

