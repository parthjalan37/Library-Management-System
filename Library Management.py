from tkinter import *
from tkinter import ttk
from ttkthemes import themed_tk as tk
import pymongo
import dns
from datetime import *

# mongodb+srv://Aryann:aryanndhir@projectx-hqir0.mongodb.net/test

constr = "mongodb+srv://Aryann:aryanndhir@projectx-hqir0.mongodb.net/test?retryWrites=true&w=majority"
myclient = pymongo.MongoClient(constr)
db = myclient.ProjectWork

root = tk.ThemedTk()
root.get_themes()
root.set_theme("clearlooks")
root.geometry("600x300")
root.title("Library Management System")


class User:
	def __init__(self):
		self.user = StringVar()
		self.pwd = StringVar()
		self.nuser = StringVar()
		self.npwd = StringVar()
		self.author = StringVar()
		self.genre = StringVar()
		self.title = StringVar()
		self.isbn = ""
		self.mylist = []

	def create(self):
		global ff
		ff = Frame(root)
		self.cannotbeempty = Label(ff, text="Fields cannot be empty!", fg="red")
		self.invaliduserpass = Label(ff, text="Invalid Password. Please try again.", fg="red")
		self.pleaseregister = Label(ff, text="Please register.", fg="red")
		self.alreadyexists = Label(ff, text="User already exists!", fg="red")
		self.registered = Label(ff, text="Registered! Try logging in!", fg="red")
		self.empty = Label(ff, text="No Books found", fg="red")
		self.noselect = Label(ff, text="Please Select An Option!", fg="red")
		self.lb = Label(ff, width="50", height="1", font=("Calibri", 17), bg="light gray")

	def die(self):
		ff.destroy()

	def forgetmessages(self):
		self.cannotbeempty.grid_forget()
		self.invaliduserpass.grid_forget()
		self.pleaseregister.grid_forget()
		self.alreadyexists.grid_forget()
		self.registered.grid_forget()
		self.empty.grid_forget()
		self.noselect.grid_forget()

	def clear(self):
		self.nuser.set("")
		self.npwd.set("")
		self.author.set("")
		self.genre.set("")
		self.title.set("")
		self.mylist = []
		self.isbn = ""

	def treefunc(self):
		self.die()
		self.create()

		self.tree = ttk.Treeview(ff, columns=3, height=5, show="headings")
		self.tree.grid(row=2, column=1, columnspan=5)
		self.tree["columns"] = (1, 2, 3)
		self.tree.heading(1, text="Title")
		self.tree.heading(2, text="Author")
		self.tree.heading(3, text="Genre")
		self.tree.column(1, width=200)
		self.tree.column(2, width=170)
		self.tree.column(3, width=170)

		scroll = ttk.Scrollbar(ff, orient="vertical", command=self.tree.yview)
		scroll.grid(row=2, column=6, sticky="ns")

		self.tree.configure(yscrollcommand=scroll.set)

		for j in self.mylist:
			isbn = j["ISBN"]
			currtitle = db.Book.find_one({"ISBN": isbn})
			self.tree.insert("", "end", values=(currtitle["Title"], currtitle["Author"], currtitle["Genre"]))

		self.tree.bind("<Double-1>", self.ondoubleclick)

		Button(ff, text="Issue", command=self.issuebook, width=10, font=("Arial", 10)).grid(row=6, column=1, pady=10)
		Button(ff, text="Back", command=self.homepage, width=10, font=("Arial", 10)).grid(row=6, column=2, pady=10)

		ff.pack(expand=1, fill=BOTH)

	def recommended(self):
		u1 = self.user.get()
		x = db.IssuedBooks.find({"Username": u1})
		s1 = set()
		l1 = [i for i in x]
		self.mylist = []

		if not l1:
			s1 = {"Self Help", "Thriller", "History"}
			for j in s1:
				z = db.Book.find({"Genre": j, "Issued": "N"})
				if z:
					for k in z:
						self.mylist.append(k)
		else:
			for i in l1:
				currisbn = i["ISBN"]
				y = db.Book.find_one({"ISBN": currisbn})
				currgen = y["Genre"]
				z = db.Book.find({"Genre": currgen, "Issued": "N"})
				if z and currgen not in s1:
					s1.add(currgen)
					for j in z:
						self.mylist.append(j)

		self.treefunc()

	def issuebook(self):
		self.forgetmessages()
		if self.isbn == "":
			self.noselect.grid(row=7, column=1, pady=10)
		else:
			db.IssuedBooks.insert_one(
				{"Username": self.user.get(), "ISBN": self.isbn, "Issue date": str(date.today()),
				 "Return date": str(date.today() + timedelta(days=7)), "Returned": "N"})
			db.Book.update_one({"ISBN": self.isbn}, {"$set": {"Issued": "Y"}})
			Label(ff, text="Issued Succesfully!").grid(row=7, column=1)

	def ondoubleclick(self, event):
		item = self.tree.selection()
		temp = "".join(self.tree.item(item, "values")[0])
		mylist1 = db.Book.find_one({"Title": {"$regex": temp}})
		self.isbn = mylist1["ISBN"]

	def checkfine(self):
		self.forgetmessages()
		isbn = self.isbn
		today = date.today()

		if isbn == "":
			self.noselect.grid(row=7, column=1, pady=15)
		else:
			myquery = {"Username": {"$regex": self.user.get()}, "ISBN": {"$regex": isbn}, "Returned": "N"}
			mylist1 = db.IssuedBooks.find(myquery)

			for mycol in mylist1:
				rdate = datetime.strptime(mycol["Return date"], '%Y-%m-%d').date()
				if today > rdate:
					Label(ff, text=f"Fine to be paid: Rs {(today-rdate).days}", fg="red").grid(row=7, column=1)
				else:
					Label(ff, text="Book returned successfully!").grid(row=7, column=1)
				db.IssuedBooks.update_one({"ISBN": isbn}, {"$set": {"Returned": "Y"}})
				db.Book.update_one({"ISBN": isbn}, {"$set": {"Issued": "N"}})

	def returnbook(self):
		self.die()
		self.create()

		mylist1 = db.IssuedBooks.find({"Username": {"$regex": self.user.get()}, "Returned": {"$regex": "N"}})
		l1 = [i for i in mylist1]

		if not l1:
			self.lb.config(bg="#F0F0F0")
			self.lb.grid()
			self.empty.grid(row=1, pady=10)
			Button(ff, text="Back", command=self.homepage, width=10).grid(row=2)
		else:
			Label(ff, text='BOOKS ISSUED ARE:').grid(row=0, column=1)

			self.tree = ttk.Treeview(ff, columns=1, height=5, show="headings")
			self.tree.grid(row=2, column=1, columnspan=5)
			self.tree.heading(1, text="Title")
			self.tree.column(1, width=200)

			scroll = ttk.Scrollbar(ff, orient="vertical", command=self.tree.yview)
			scroll.grid(row=2, column=6, sticky="ns")

			self.tree.configure(yscrollcommand=scroll.set)

			for j in l1:
				isbn = j["ISBN"]
				currtitle = db.Book.find_one({"ISBN": isbn})
				self.tree.insert("", "end", values=(currtitle["Title"],))

			self.tree.bind("<Double-1>", self.ondoubleclick)

			Button(ff, text="Return", command=self.checkfine).grid(row=6, column=1)
			Button(ff, text="Back", command=self.homepage).grid(row=6, column=2)

		ff.pack(expand=1, fill=BOTH)

	def browsebooktitle(self):
		self.forgetmessages()
		t = self.title.get()

		if t == "":
			self.cannotbeempty.grid()
		else:
			self.mylist = db.Book.find({"Title": {"$regex": t}, "Issued": "N"})
			if db.Book.count_documents({"Title": {"$regex": t}, "Issued": "N"}) == 0:
				self.empty.grid(row=5)
			else:
				self.treefunc()

	def entertitle(self):
		self.die()
		self.create()
		self.lb.config(bg="#F0F0F0")
		self.lb.grid(row=0)

		Label(ff, text="Enter Book Name").grid(row=1, pady=10)
		Entry(ff, textvariable=self.title, width=20, relief='solid', borderwidth=1).grid(row=2)
		Button(ff, text="Browse", command=self.browsebooktitle, width=10, font=("Arial", 10)).grid(row=3, pady=20)
		Button(ff, text="Back", command=self.homepage, width=10, font=("Arial", 10)).grid(row=4, pady=5)

		ff.pack(expand=1, fill=BOTH)

	def browsebookauthor(self):
		self.forgetmessages()
		a = self.author.get()

		if a == "":
			self.cannotbeempty.grid()
		else:
			self.mylist = db.Book.find({"Author": {"$regex": a}, "Issued": "N"})
			if db.Book.count_documents({"Author": {"$regex": a}, "Issued": "N"}) == 0:
				self.empty.grid(row=5, column=0)
			else:
				self.treefunc()

	def enterauthor(self):
		self.die()
		self.create()
		self.lb.config(bg="#F0F0F0")
		self.lb.grid(row=0)

		Label(ff, text="Enter Author's Name").grid(row=1, pady=10)
		Entry(ff, textvariable=self.author, width=20, relief='solid', borderwidth=1).grid(row=2)
		Button(ff, text="Browse", command=self.browsebookauthor, width=10, font=("Arial", 10)).grid(row=3, pady=20)
		Button(ff, text="Back", command=self.homepage, width=10, font=("Arial", 10)).grid(row=4, pady=5)

		ff.pack(expand=1, fill=BOTH)

	def browsebookgenre(self):
		g = self.genre.get()

		if g == "":
			self.cannotbeempty.grid()
		else:
			self.mylist = db.Book.find({"Genre": {"$regex": g}, "Issued": "N"})
			if db.Book.count_documents({"Genre": {"$regex": g}, "Issued": "N"}) == 0:
				self.empty.grid(row=8, pady=5)
			else:
				self.treefunc()

	def genreclick(self, event):
		item = self.tree.selection()
		self.genre.set("".join(self.tree.item(item, "values")[0]))

	def entergenre(self):
		self.die()
		self.create()

		s1 = set()
		x = db.Book.find({"Issued": "N"})
		for i in x:
			if i["Genre"] not in s1:
				s1.add(i["Genre"])

		self.tree = ttk.Treeview(ff, columns=1, height=5, show="headings")
		self.tree.grid(row=1, column=1, columnspan=5)
		self.tree.heading(1, text="Genre")
		self.tree.column(1, width=200)

		scroll = ttk.Scrollbar(ff, orient="vertical", command=self.tree.yview)
		scroll.grid(row=1, column=6, sticky="ns")

		self.tree.configure(yscrollcommand=scroll.set)

		for j in sorted(s1):
			self.tree.insert("", "end", values=(j,))

		self.tree.bind("<Double-1>", self.genreclick)

		Label(ff, text="", width=20).grid(row=0, column=0)
		Button(ff, text="SEARCH", command=self.browsebookgenre, width=10).grid(row=7, column=2, pady=10, padx=10)
		Button(ff, text="BACK", command=self.homepage, width=10).grid(row=7, column=1, pady=10, padx=10)

		ff.grid()

	def browsebooks(self):
		self.die()
		self.create()
		self.lb.config(bg="#F0F0F0")
		self.lb.grid(row=0)

		Button(ff, text="Browse by Book Name", command=self.entertitle, width=20, font=("Arial", 10)).grid(row=1, pady=5)
		Button(ff, text="Browse by Author", command=self.enterauthor, width=20, font=("Arial", 10)).grid(row=2, pady=5)
		Button(ff, text="Browse by Genre", command=self.entergenre, width=20, font=("Arial", 10)).grid(row=3, pady=5)
		Button(ff, text="Back", command=self.homepage, width=10, font=("Arial", 10)).grid(row=4, pady=10)

		ff.pack(expand=1, fill=BOTH)

	def validatelogin(self):
		User.forgetmessages(self)

		u = self.user.get()
		p = self.pwd.get()
		x = db.Member.find_one({"Username": u})

		if u == "" or p == "":
			self.cannotbeempty.grid()
		elif x:
			if x["Password"] == p:
				self.homepage()
			else:
				self.invaliduserpass.grid()
		else:
			self.pleaseregister.grid()

	def validatesignup(self):
		User.forgetmessages(self)
		u = self.nuser.get()
		p = self.npwd.get()

		x = db.Member.find_one({"Username": u})
		if u == "" or p == "":
			self.cannotbeempty.grid()
		elif x:
			self.alreadyexists.grid()
		else:
			db.Member.insert_one({"Username": u, "Password": p})
			self.login()

	def register(self):
		self.die()
		self.create()
		self.clear()

		self.lb.config(text="Register")
		self.lb.grid(row=0)

		Label(ff, text="New Username", font=("Arial", 12)).grid(row=2, pady=10)
		Entry(ff, textvariable=self.nuser, relief='solid', borderwidth=1).grid(row=3, ipady=2)

		Label(ff, text="New Password", font=("Arial", 12)).grid(row=4, pady=7)
		Entry(ff, textvariable=self.npwd, relief='solid', borderwidth=1).grid(row=5, ipady=2)

		Button(ff, text="REGISTER", command=self.validatesignup, width=10, font=("Arial", 10)).grid(row=6, pady=20)
		Button(ff, text="BACK", command=self.login, width=10, font=("Arial", 10)).grid(row=7, pady=5)

		ff.pack(expand=1, fill=BOTH)

	def login(self):
		self.die()
		self.create()
		self.clear()
		self.user.set("")
		self.pwd.set("")

		self.lb.config(text="Login")
		self.lb.grid(row=0)

		Label(ff, text="User Name", font=("Arial", 14)).grid(row=2, padx=10, pady=15)
		Entry(ff, textvariable=self.user, relief='solid', borderwidth=1).grid(row=3, ipady=2)

		Label(ff, text="Password", font=("Arial", 14)).grid(row=4, column=0, pady=10)
		Entry(ff, textvariable=self.pwd, show='*', relief='solid', borderwidth=1).grid(row=5, column=0, ipady=2)

		Button(ff, text="LOGIN", command=self.validatelogin, compound=CENTER, width=10).grid(row=6, column=0, pady=15)
		Button(ff, text="REGISTER", command=self.register, compound=CENTER, width=10).grid(row=7, column=0, padx=10)

		ff.pack(expand=1, fill=BOTH)

	def homepage(self):
		self.die()
		self.create()
		self.clear()
		self.lb.config(bg="#F0F0F0")
		self.lb.grid()

		Button(ff, text="RETURN BOOK", command=self.returnbook, width=20, height=2).grid(row=1, pady=7)
		Button(ff, text="RECOMMENDED BOOKS", width=20, height=2, command=self.recommended).grid(row=2, pady=7)
		Button(ff, text="SEARCH BOOK", width=20, height=2, command=self.browsebooks).grid(row=3, pady=7)
		Button(ff, text="<< LOG OUT", command=self.login, width=20, height=2).grid(row=4, pady=7)

		ff.pack(expand=1, fill=BOTH)


obj = User()
obj.create()
obj.login()
root.mainloop()
