import sys

from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox

from database import Categories, Tasks
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
'''
                                TO-DO
                                1. rewrite add_tasks function
                                2. rewrite loading and adding funcs
                                3. add exception handler class
'''


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.tasks_list = QListWidget(self)
        self.button_all_tasks = QPushButton("Все задачи", self)
        self.button_active_tasks = QPushButton("Активные задачи", self)
        self.button_done_tasks = QPushButton("Выполненные задачи", self)
        self.task_name = QLineEdit(self)
        self.task_description = QTextEdit(self)
        self.button_add_task = QPushButton("Добавить задачу", self)
        self.button_edit_task = QPushButton("Изменить задачу", self)
        self.button_delete_task = QPushButton("Удалить задачу", self)
        self.categories_list = QListWidget(self)
        self.category_name = QLineEdit(self)
        self.button_add_category = QPushButton("Добавить категорию", self)
        self.button_edit_category = QPushButton("Изменить категорию", self)
        self.button_delete_category = QPushButton("Удалить категорию", self)

        self.button_add_category.clicked.connect(self.add_category)
        self.button_add_task.clicked.connect(self.add_tasks)
        self.tasks_list.itemClicked.connect(self.task_info)
        self.categories_list.itemClicked.connect(self.category_info)
        self.button_delete_category.clicked.connect(self.delete_category)
        self.button_delete_task.clicked.connect(self.delete_task)
        self.button_edit_category.clicked.connect(self.edit_category)
        self.button_edit_task.clicked.connect(self.edit_task)

        self.engine = create_engine('sqlite:///tasks.db', echo=False)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        self.init_ui()
        self.load_categories()
        self.load_tasks()


    def init_ui(self) -> None:
        self.resize(400, 500)
        self.setWindowTitle("Список задач")
        vbox = QVBoxLayout()
        self.name1 = QLabel('Список задач:', self)
        vbox.addWidget(self.name1)
        vbox.addWidget(self.tasks_list)
        hbox = QHBoxLayout()
        hbox.addWidget(self.button_all_tasks)
        hbox.addWidget(self.button_active_tasks)
        hbox.addWidget(self.button_done_tasks)
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        self.name2 = QLabel('Название задачи:', self)
        hbox.addWidget(self.name2)
        hbox.addWidget(self.task_name)
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        self.name3 = QLabel('Описание задачи:', self)
        hbox.addWidget(self.name3)
        hbox.addWidget(self.task_description)
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        self.name4 = QLabel('Категория:', self)
        hbox.addWidget(self.name4)
        hbox.addWidget(self.category_name)
        vbox.addLayout(hbox)
        self.name5 = QLabel('Список категорий:', self)
        vbox.addWidget(self.name5)
        vbox.addWidget(self.categories_list)
        hbox = QHBoxLayout()
        hbox.addWidget(self.button_add_task)
        hbox.addWidget(self.button_edit_task)
        hbox.addWidget(self.button_delete_task)
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.button_add_category)
        hbox.addWidget(self.button_edit_category)
        hbox.addWidget(self.button_delete_category)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.setStyleSheet(
            "QWidget {\n"
                                 "    color: white;\n"
                                 "    background-color: #121212;\n"
                                 "    font-family: Rubik;\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton {\n"
                                 "background-color: transparent;\n"
                                 "border: 1px solid #f66867;\n"
                                 "border-radius: 13;\n"
                                 "}\n"
                                 "QPushButton:hover {\n"
                                 "background-color: #666;\n"
                                 "}\n"
                                 "QPushButton:pressed {\n"
                                 "background-color: #FF8888;\n"
                                 "}"
        )
        
    def load_categories(self) -> None:
        result = self.session.query(Categories.name).all()
        self.categories_list.clear()
        for row in result:
            self.categories_list.addItem(QListWidgetItem(row[0]))

    def load_tasks(self) -> None:
        result = self.session.query(Tasks.name).join(Categories, Tasks.category_id == Categories.id)
        self.tasks_list.clear()
        for row in result:
            self.tasks_list.addItem(QListWidgetItem(row[0]))

    def add_category(self) -> None:
        name = self.category_name.text()
        if not name == '':
            addition = Categories(name=name)
            self.session.add(addition)
            self.session.commit()
            self.load_categories()

    def add_tasks(self) -> None:
        if self.categories_list.currentItem():
            category_name = self.categories_list.currentItem().text()
            name = self.task_name.text()
            description = self.task_description.toPlainText()
            category_id = self.get_category_id_by_name(category_name)
            if not name == '':
                addition = Tasks(name=name, description=description, active=True, category_id=category_id)
                self.session.add(addition)
                self.session.commit()
                self.load_tasks()
        
    def get_category_name_by_id(self, id: int | str,) -> tuple | None:
        result = self.session.query(Categories.name).filter(f'{int(id)}'==Categories.id).first()
        return result[0]
    
    def get_category_id_by_name(self, name: str) -> int:
        category_id = self.session.query(Categories.id).filter(Categories.name == f'{name}').first()
        return int(category_id[0])

    def _create_new_category(self, category_name: str) -> bool:
        if not category_name == '':
            instance = Categories(name = category_name)
            if self.session.add(instance):
                self.session.commit()
                self.load_categories()
                return True

    

    def task_info(self) -> None:
        currentTask = self.tasks_list.currentItem().text()
        test = self.session.query(Tasks.name, Tasks.description, Tasks.category_id).filter(f'{currentTask}'==Tasks.name).first()
        self.task_name.setText(str(test[0]))
        self.task_description.setText(str(test[1]))
        self.category_name.setText(str(self.get_category_name_by_id(str(test[2]))))

    def category_info(self) -> None:
        self.category_name.setText(self.categories_list.currentItem().text())

    def delete_category(self) -> None:
        if self.categories_list.currentItem():
            category_name = self.categories_list.currentItem().text()
            category_id = self.get_category_id_by_name(category_name)
            if self.delete_category_window(category_name):
                self.session.query(Categories).filter(Categories.id == f'{category_id}').delete(synchronize_session='evaluate')
                self.session.query(Tasks).filter(Tasks.category_id == f'{category_id}').delete(synchronize_session='evaluate')
                self.session.commit()
                self.load_categories()
                self.load_tasks()


    def delete_task(self) -> None:
        if self.tasks_list.currentItem():
            tasks_name = self.tasks_list.currentItem().text()
            self.session.query(Tasks).filter(Tasks.name == f'{tasks_name}').delete(synchronize_session='evaluate')
            self.session.commit()
            self.load_tasks()

    def delete_category_window(self, category: str) -> bool:
        window = QMessageBox()
        window.setIcon(QMessageBox.Warning)
        window.setText(f'Вы точно хотите удалить категорию "{category}" ?')
        window.setWindowTitle('Удалить категорию?')
        window.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        window.show()
        result = window.exec()
        if result == QMessageBox.Yes:
            return True
        if result == QMessageBox.No:
            return False

    def edit_task(self) -> None:
        if self.tasks_list.currentItem():
            task = self.tasks_list.currentItem().text()
            updated_name = self.task_name.text()
            updated_description = self.task_description.toPlainText()
            current_category = self.category_name.text()
            categories = self.session.query(Categories.name).all()

            for var in categories:
                if not current_category == var[0]:
                    print(f'Creating new category {current_category} ...')
                    self._create_new_category(current_category)
                    self.load_categories()
                    break

            category_id = self.get_category_id_by_name(current_category)

            self.session.query(Tasks).filter(Tasks.name == f'{task}').update({
                Tasks.name : f'{updated_name}',
                Tasks.description : f'{updated_description}',
                Tasks.category_id : f'{category_id}',
            },
            synchronize_session='evaluate')
            self.session.commit()
            self.load_tasks()

    def edit_category(self) -> None:
        if self.categories_list.currentItem():
            updated_category = self.category_name.text()
            category_id = self.get_category_id_by_name(self.categories_list.currentItem().text())
            self.session.query(Categories).filter(Categories.id == f"{category_id}").update({Categories.name : f'{updated_category}'}, synchronize_session='evaluate')
            self.session.commit()
            self.load_categories()
    '''
    def show_active_tasks(self) -> None:
        pass

    def show_completed_tasks(self) -> None:
        pass
    '''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()