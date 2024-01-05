import tkinter as tk
import random
import fitz  # PyMuPDF
import re

# 定义提取问题的函数
def extract_questions(file_path):
    doc = fitz.open(file_path)
    questions = []

    for page in doc:
        text = page.get_text()
        matches = re.findall(r'(\d+、(.*?))\n(?:[A-Z]\..*?\n)+答案：([A-Z]+)', text, re.DOTALL)
        for match in matches:
            question_text = match[1]
            question_text = re.sub(r'\n', '', question_text)
            options_text = text[text.find(match[0]):text.find('答案：', text.find(match[0]))]
            options = re.findall(r'[A-Z]\.(.*?)\n', options_text, re.DOTALL)
            options = [f"{chr(65 + i)}. {opt.strip()}" for i, opt in enumerate(options)]
            question_type = "多选题" if len(match[2]) > 1 else "单选题"
            questions.append({
                'question': question_text,
                'options': options,
                'answer': match[2],
                'type': question_type
            })

    return questions

class ReviewApp:
    def __init__(self, master, questions):
        self.master = master
        master.title("选择题复习软件")
        master.attributes('-fullscreen', True)

        self.questions = questions
        self.current_question = None
        self.answer_revealed = False
        self.random_mode = True
        self.question_index = 0
        self.options_labels = []

        self.center_frame = tk.Frame(master)
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')

        font_large = ('Arial', 24)
        font_medium = ('Arial', 20)

        self.question_label = tk.Label(self.center_frame, text="", wraplength=master.winfo_screenwidth(), font=font_large)
        self.question_label.pack()

        self.type_label = tk.Label(self.center_frame, text="", fg="blue", font=font_medium)
        self.type_label.pack()

        self.options_frame = tk.Frame(self.center_frame)
        self.options_frame.pack()

        self.answer_label = tk.Label(self.center_frame, text="", fg="blue", font=font_medium)
        self.answer_label.pack()

        self.action_button = tk.Button(self.center_frame, text="显示答案", command=self.reveal_answer_or_next, font=font_medium)
        self.action_button.pack()

        self.mode_button = tk.Button(self.center_frame, text="切换顺序模式", command=self.toggle_mode, font=font_medium)
        self.mode_button.pack()

        self.exit_button = tk.Button(self.center_frame, text="退出全屏", command=self.exit_fullscreen, font=font_medium)
        self.exit_button.pack()

        master.bind('<Return>', self.reveal_answer_or_next)

        self.next_question()

    def toggle_mode(self):
        self.random_mode = not self.random_mode
        mode_text = "顺序模式" if self.random_mode else "随机模式"
        self.mode_button.config(text=f"切换到{mode_text}")
        self.question_index = 0
        self.next_question()

    def next_question(self):
        if self.random_mode:
            self.current_question = random.choice(self.questions)
        else:
            self.current_question = self.questions[self.question_index]
            self.question_index = (self.question_index + 1) % len(self.questions)

        question_number = self.questions.index(self.current_question) + 1
        question_text = f"题目 {question_number}: {self.current_question['question']}\n\n"
        self.question_label.config(text=question_text)

        for label in self.options_labels:
            label.destroy()
        self.options_labels.clear()

        for option in self.current_question['options']:
            label = tk.Label(self.options_frame, text=option, font=('Arial', 20))
            label.pack()
            self.options_labels.append(label)

        self.type_label.config(text=self.current_question['type'])
        self.answer_label.config(text="")
        self.action_button.config(text="显示答案")
        self.answer_revealed = False

    def reveal_answer_or_next(self, event=None):
        if not self.answer_revealed:
            answer = self.current_question['answer']
            for letter in answer:
                index = ord(letter) - 65
                self.options_labels[index].config(fg='green')
            self.answer_label.config(text=f"答案: {self.current_question['answer']}")
            self.action_button.config(text="下一题")
            self.answer_revealed = True
        else:
            for label in self.options_labels:
                label.config(fg='black')
            self.next_question()

    def exit_fullscreen(self):
        self.master.attributes('-fullscreen', False)

if __name__ == "__main__":
    root = tk.Tk()
    file_path = '/Users/lintengjie/Downloads/Test.pdf'  # 替换为实际的PDF文件路径
    questions = extract_questions(file_path)
    app = ReviewApp(root, questions)
    root.mainloop()
