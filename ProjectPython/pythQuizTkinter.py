import tkinter as tk
from tkinter import PhotoImage, messagebox, simpledialog, filedialog
from difflib import SequenceMatcher
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
from datetime import date
import random
import os

CUSTOM_DIR = "customData"
os.makedirs(CUSTOM_DIR, exist_ok=True)

def CheckAnswer(userAnsw, correctAnsw):
    similarity = SequenceMatcher(None, userAnsw.lower(), correctAnsw.lower()).ratio()
    return similarity >= 0.8

def ReadQuestions(category, difficulty):
    file_name = os.path.join("data", f"{category}_{difficulty}.json")
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            questions = json.load(file)
            if difficulty in ["Facile", "Moyen"] and all("prompt" in q and "choices" in q and "answer" in q for q in questions):
                return questions
            elif difficulty == "difficile" and all("prompt" in q and "answer" in q for q in questions):
                return questions
            else:
                ValueError("Problème dans le fichier JSON qui ne contient pas les champs requis.")
    except FileNotFoundError:
        messagebox.showerror("Erreur", f"Le fichier {file_name} est introuvable!")
        return []

def RandomQuestion(questions, nbrQuestion=10):
    return random.sample(questions, min(nbrQuestion, len(questions)))

## Fonction pour le proccéssus du quiz 
## qui prend en paramètre la catégorie(thème) du quiz ainsi sa défficulté(facile, moyen, difficile)
def LaunchQuiz(category, difficulty, questions=[]):
    
    ## Première variable questions qui ouvre le fichier .json de la catégorie et difficulté puis prend son contenue
    ## Deuxième variable questions qui va demander un "mélange" et prendre seulement 10 question sur les 30 disponible
    if not category == "custom" and not difficulty == "custom":
        questions = ReadQuestions(category, difficulty)
    questions = RandomQuestion(questions)

    ## Si la variable tableau questions est null ou vide, le processus s'arrête
    if not questions: 
        messagebox.showerror("ERREUR", "Aucune question disponible pour ce 'quiz'.")
        return

    ## Fonction qui procédère au lecture des différent question dans une boucle et montrer à l'utilisateur
    ## De ce dernier, à chaque question répondu par l'utilisateur, vérifie si c'est ce qu'est demander ou faux
    ## Si c'est faux, alors prend la question, où la réponse était fausse pour le mettre dans une variable tableau
    ## ainsi montrer à l'utilisateur à la fin du quiz.
    ## Si c'est correcte, alors il ajoute 1 au score inité à 0.
    def NextQuestion(index=0, score=0, wrongAnswers=[]):
        if index < len(questions):
            question = questions[index]

            for widget in frame.winfo_children():
                widget.destroy()

            progress = ttk.Progressbar(frame, maximum=len(questions), value=index+1, bootstyle="info-striped")
            progress.pack(pady=10)

            ttk.Label(frame, text=f"Question {index + 1}: {question['prompt']}", bootstyle="inverse-dark").pack(side=TOP, pady=20)

            if difficulty in ["Facile", "Moyen"]:
                for choice in question["choices"]:
                    ttk.Button(frame, text=choice, bootstyle="info", width=50,
                    command=lambda c=choice: ValidateAnswer(c, index, score, wrongAnswers)).pack(pady=5)
            elif difficulty == "difficile":
                answer_entry = ttk.Entry(frame)
                answer_entry.pack()
                ttk.Button(frame, text="Valider", bootstyle="success", width=20, command=lambda: ValidateAnswer(answer_entry.get(), index, score, wrongAnswers)).pack(pady=5)
            elif difficulty == "custom":
                for choice in question["choices"]:
                    ttk.Button(frame, text=choice, bootstyle="info", width=20, 
                    command=lambda c=choice: ValidateAnswer(c, index, score, wrongAnswers)).pack(pady=5)
        else:
            for widget in frame.winfo_children():
                widget.destroy()

            result_text = f"Quiz terminé! Votre score est {score}/{len(questions)}\n"
            if wrongAnswers:
                result_text += "\nQuestions incorrectes:\n"
                for idQ, (q, correct) in enumerate(wrongAnswers, 1):
                    result_text += f"{idQ}. {q} (Réponse attendue: {correct})\n"

            ttk.Label(frame, text=result_text, justify="left", bootstyle="success").pack(pady=10)
            SaveScore(category, difficulty, score)

    ## Fonction qui vérifie si la réponse de l'utilisateur est correct ou fausse.
    ## Si vrai, alors un +1 est ajouté à la variable score
    ## sinon la question avec la bonne réponse est stocké dans une variable tableau.
    def ValidateAnswer(userAnsw, index, score, wrongAnswers):
        correctAnswer = questions[index]["answer"]
        if difficulty == "difficile":
            if CheckAnswer(userAnsw, correctAnswer):
                score += 1
            else:
                wrongAnswers.append((questions[index]["prompt"], correctAnswer))
        elif userAnsw == correctAnswer:
            score += 1
        else:
            wrongAnswers.append((questions[index]["prompt"], correctAnswer))
        NextQuestion(index + 1, score, wrongAnswers)

    NextQuestion()

    
## Fonction qui permet de "sauvegarder" le score de l'utilisateur s'il le souhaite
## Demande si l'utilisateur veut enregistrer son score qui est indiqué
## Si True alors demande un pseudonyme à l'utilisateur si laissez vide alors "anonyme" est mis
## initie la syntaxe du fichier json avec les donnée :
## pseudonyme de l'utilisateur
## la catégorie du quiz sélectionné par l'utilisateur
## la difficulté du quiz sélectionné par l'utilisateur
## Le score de l'utilisateur
## la date du quiz
## Puis essaye d'ouvrir le fichier .json du score 
## si existe alors la variable tableau listScores stock les donnée du fichier sinon crée un tableau pour la variable
## ajoute les donnée initié de data par la suite dans la variable listScores
## Puis ouvre une nouvelle fois le fichier pour écrire les nouvelles donnée qui concerne le score de l'utilisateur
## et indique un message que le score a bien été enregistré.
def SaveScore(category, difficulty, score):
    comfirm = messagebox.askyesno("Enregistrement de score", "Voulez-vous enregistrer votre score de : " + str(score) + "/10 ?")

    if comfirm:
        pseudo = simpledialog.askstring("Pseudonyme", "Entrez un Pseudonyme sinon laisser vide pour Anonyme")

        fileScores = os.path.join("data", "scores.json")

        if not pseudo:
            pseudo = "Anonyme"
        
        data = {
            "Pseudonyme": pseudo,
            "Category": category, 
            "Difficulty": difficulty, 
            "Score": str(score) + "/10", 
            "Date": date.today().isoformat()
            }
        try:
            with open(fileScores, "r", encoding="utf-8") as file:
                listScores = json.load(file)
                
        except (FileNotFoundError, json.JSONDecodeError):
            listScores = []

        listScores.append(data)
        
        with open(fileScores, "w", encoding="utf-8") as file:
            json.dump(listScores, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Score sauvegardé", "Votre score a été sauvegardé avec succès!")

def ShowScores():
    scores = LoadScores()

    WindowScore = ttk.Toplevel(root)
    WindowScore.title("Tableau des Scores")

    columns = ("Pseudonyme", "Category", "Difficulty", "Score", "Date")
    tree = ttk.Treeview(WindowScore, padding=10, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    for entry in scores:
        tree.insert("", ttk.END, values=(
            entry.get("Pseudonyme", "N/A"),
            entry.get("Category", "N/A"),
            entry.get("Difficulty", "N/A"),
            entry.get("Score", "N/A"),
            entry.get("Date", "N/A")
        ))

    tree.pack(expand=True, fill="both")

    closeButton = ttk.Button(WindowScore, text="Fermer", bootstyle="danger", command=WindowScore.destroy)
    closeButton.pack(pady=10)

def LoadScores():
    fileScores = os.path.join("data", "scores.json")
    try:
        with open(fileScores, 'r', encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        messagebox.showerror("Erreur de lecture du fichier :", e)
        return []

## def changeTheme(theme):
##    root.style.theme_use(theme)

def CreateQuiz():
    createQuizWindow = ttk.Toplevel(root)
    createQuizWindow.title("Créer un quiz")
    questions = [{"prompt" : "", "answer": "", "choices": ["", "", "", ""]} for _ in range(10)]
    currentIndex = tk.IntVar(value=0)
    frameQuestion = ttk.Frame(createQuizWindow, padding=10)
    frameQuestion.pack(fill="both", expand=True)
    def SaveCustomQuiz(questions):
        
        for i, question in enumerate(questions):
            if not question["prompt"] or not question["answer"] or not all(question["choices"]):
                messagebox.showerror("ERREUR", f"La question {i+1} est incomplète.")
                return
        
        savePath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")]
                                                , initialdir=CUSTOM_DIR)
        
        if savePath:
            with open(savePath, "w", encoding="utf-8") as f:
                json.dump(questions, f, ensure_ascii=False, indent=1)
            messagebox.showinfo("SUCCES", f"Votre Quiz a bien été enregkstré !")
            createQuizWindow.destroy()
    
    def DisplayCreate(index):
        for widget in frameQuestion.winfo_children():
            widget.destroy()

        question = questions[index]

        
        ttk.Label(frameQuestion, text=f"Question {index+1} :").pack(anchor="w")
        prompt_entry = ttk.Entry(frameQuestion, width=50)
        prompt_entry.insert(0, question["prompt"])
        prompt_entry.pack(pady=5)
        
        ttk.Label(frameQuestion, text="Réponse :").pack(anchor="w")
        answer_entry = ttk.Entry(frameQuestion, width=50)
        answer_entry.insert(0, question["answer"])
        answer_entry.pack(pady=5)

        choices = []
        ttk.Label(frameQuestion, text="Choix(une case doit correspondre à la réponse) :").pack(anchor="w")
        for i in range(4):
            choice_entry = ttk.Entry(frameQuestion, width=50)
            choice_entry.insert(0, question["choices"][i])
            choice_entry.pack(pady=4)
            choices.append(choice_entry)

        def SaveQuestion():
            question["prompt"] = prompt_entry.get().strip().lower()
            question["answer"] = answer_entry.get().strip().lower()
            question["choices"] = [choice.get().strip().lower() for choice in choices]

            if not question["prompt"]:
                messagebox.showerror("ERREUR", f"La question ne peut pas être vide.")
                return
            if not question["answer"]:
                messagebox.showerror("ERREUR", f"La réponse ne peut pas être vide.")
                return
            if not all(question["choices"]):
                messagebox.showerror("ERREUR", f"Tous les choix doivent être remplis.")
                return
            if question["answer"] not in question["choices"]:
                messagebox.showerror("ERREUR", f"La réponse doit correspondre à l'un des choix.")
                return
        
        frameNav = ttk.Frame(frameQuestion)
        frameNav.pack(pady=10)

        if index > 0:
            ttk.Button(frameNav, text="Précédent", command=lambda: PreviousIndex()).pack(side="left", padx=5)
        if index < len(questions) - 1:
            ttk.Button(frameNav, text="Suivant", command=lambda: NextIndex()).pack(side="left", padx=5)
        else:
            ttk.Button(frameNav, text="Enregistrer", command=lambda: [SaveQuestion(), SaveCustomQuiz(questions)]).pack(side="left", padx=5)
    
        def NextIndex():
            if currentIndex.get() < len(questions)-1:
                currentIndex.set(currentIndex.get()+1)
                DisplayCreate(currentIndex.get())
        def PreviousIndex():
            if currentIndex.get() > 0:
                currentIndex.set(currentIndex.get()-1)
                DisplayCreate(currentIndex.get())

    DisplayCreate(currentIndex.get())

    
def LoadOtherQuiz():
    pathFile = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")]
                                          , initialdir=CUSTOM_DIR)
    
    if pathFile:
        try:
            with open(pathFile, "r", encoding="utf-8") as f:
                questions = json.load(f)
            if not isinstance(questions, list):
                raise ValueError("Le fichier JSON doit contenir un tableau de questions.")
            if not all(isinstance(q, dict) and "prompt" in q and "answer" in q and "choices" in q for q in questions):
                raise ValueError("Chaque question doit contenir les clés 'prompt', 'answer' et 'choices'.")
            difficulty = "custom"
            category = "custom"
            LaunchQuiz(category=category, difficulty=difficulty, questions=questions)
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("ERREUR", f"Erreur de lecture du fichier JSON : {e}")
            return
        except Exception as Ex:
            messagebox.showerror("ERREUR", f"Une exception inattendu s'est produite : {Ex}")
            return

def EditOtherQuiz():
    pathFile = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON Files", "*.JSON")]
                                          , initialdir=CUSTOM_DIR)
    
    editQuizWindow = ttk.Toplevel()
    editQuizWindow.title("Modification de quiz")

    if pathFile:
        try:
            with open(pathFile, "r", encoding="utf-8") as f:
                questions = json.load(f)
            if not isinstance(questions, list):
                raise ValueError("Le fichier JSON doit contenir un tableau de questions.")
            if not all(isinstance(q, dict) and "prompt" in q and "answer" in q and "choices" in q for q in questions):
                raise ValueError("Chaque question doit contenir les clés 'prompt', 'answer' et 'choices'.")
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("ERREUR", f"Erreur de lecture du fichier JSON : {e}")
            return
        except Exception as Ex:
            messagebox.showerror("ERREUR", f"Une exception inattendu s'est produite : {Ex}")
            return
    
    currentIndex = tk.IntVar(value=0)

    def DisplayEdit(index):
        for widget in editQuizWindow.winfo_children():
            widget.destroy()
        question = questions[index]

        ttk.Label(editQuizWindow, text=f"Question {index+1} :").pack(anchor="w")
        promptEntry = ttk.Entry(editQuizWindow, width=50)
        promptEntry.insert(0, question["prompt"])
        promptEntry.pack(pady=5)
        
        ttk.Label(editQuizWindow, text="Réponse :").pack(anchor="w")
        answerEntry = ttk.Entry(editQuizWindow, width=50)
        answerEntry.insert(0, question["answer"])
        answerEntry.pack(pady=5)

        choiceEntries = []
        ttk.Label(editQuizWindow, text="Choix :").pack(anchor="w")
        for i, choice in enumerate(question["choices"]):
            choiceEntry = ttk.Entry(editQuizWindow, width=50)
            choiceEntry.insert(0, choice)
            choiceEntry.pack(pady=2)
            choiceEntries.append(choiceEntry)

        def SaveEdit(index):
            question = questions[index]
            question["prompt"] = promptEntry.get().strip().lower()
            question["answer"] = answerEntry.get().strip().lower()
            question["choices"] = [choice.get().strip().lower() for choice in choiceEntries]
        
        if index > 0:
            ttk.Button(editQuizWindow, text="Précédent", command=lambda: PreviousIndex()).pack(side="left", padx=5)
        if index < len(questions) - 1:
            ttk.Button(editQuizWindow, text="Suivant", command=lambda: NextIndex()).pack(side="left", padx=5)
        else:
            ttk.Button(editQuizWindow, text="Enregistrer", command=lambda: [SaveEdit(index), SaveCustomQuiz(questions)]).pack(pady=5)

    def SaveCustomQuiz(questions):
        
        for i, question in enumerate(questions):
            if not question["prompt"] or not question["answer"] or not all(question["choices"]):
                messagebox.showerror("ERREUR", f"La question {i+1} est incomplète.")
                return
        if pathFile:
            with open(pathFile, "w", encoding="utf-8") as f:
                json.dump(questions, f, ensure_ascii=False, indent=1)
            messagebox.showinfo("SUCCES", "Votre Quiz a bien été enregistré !")
            editQuizWindow.destroy()

    def NextIndex():
        if currentIndex.get() < len(questions)-1:
            currentIndex.set(currentIndex.get()+1)
            DisplayEdit(currentIndex.get())
    def PreviousIndex():
        if currentIndex.get() > 0:
            currentIndex.set(currentIndex.get()-1)
            DisplayEdit(currentIndex.get())
            
    DisplayEdit(currentIndex.get())

root = ttk.Window(themename="darkly")
root.title("Quiz by Ranimaux")
root.geometry("1024x768")


menu = ttk.Menu(root)
root.config(menu=menu)

categories = ["Histoire", "Géographie", "Art&Cinéma"]

for category in categories:
    submenu = ttk.Menu(menu, bd=10, tearoff=0, font="Arial")
    submenu.add_command(label="Facile", command=lambda c=category: LaunchQuiz(c, "Facile"))
    submenu.add_command(label="Moyen", command=lambda c=category: LaunchQuiz(c, "Moyen"))
    ##submenu.add_command(label="Difficile", command=lambda c=category: LaunchQuiz(c, "Difficile"))
    menu.add_cascade(label=category, menu=submenu)
otherMenu = ttk.Menu(menu, tearoff=0)
menu.add_cascade(label="Autre", menu=otherMenu)
otherMenu.add_command(label="Créer un quiz", command=CreateQuiz)
otherMenu.add_command(label="Modifier un quiz", command=EditOtherQuiz)
otherMenu.add_command(label="Sélectionner un quiz", command=LoadOtherQuiz)
##themeFrame = ttk.Frame(root, padding=10)
##themeFrame.pack(side="top", anchor="ne", padx=10, pady=10)
##darkIncoPath = os.path.join("assets", "lune.png")
##flatIncoPath = os.path.join("assets", "soleil.png")
##darkIncon = PhotoImage(file=darkIncoPath)
##flatIncon = PhotoImage(file=flatIncoPath)
##ttk.Button(themeFrame, image=darkIncon, command=lambda: changeTheme("darkly")).grid(row=0, column=0, padx=5)
##ttk.Button(themeFrame, image=flatIncon, command=lambda: changeTheme("flatly")).grid(row=0, column=1, padx=5)
##root.images = [darkIncon, flatIncon] 

frame = ttk.Frame(root, padding=20, height=115, width=375)
frame.pack(expand=True, fill="both")

score = ttk.Button(root, text="Afficher les différents score", bootstyle="info", command=ShowScores)
score.pack(pady=10)

footer = ttk.Label(root, text="Ranimaux - Tous droits réservés ", bootstyle="inverse-secondary", font=("Arial", 10))
footer.pack(side="bottom", pady=10)

root.mainloop()