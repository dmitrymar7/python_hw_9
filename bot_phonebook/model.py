
import xml.etree.ElementTree as ET


class Record:
    def __init__(self, name, telephone, comment=None):
        self.name = name
        self.telephone = telephone
        self.comment = comment

    @property
    def comment(self):
        if self._comment is None:
            return " "
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment = value

    def toElementTree(self):
        record = ET.Element("record")
        record_name = ET.Element("name")
        record_telephone = ET.Element("telephone")
        record_comment = ET.Element("comment")

        record.append(record_name)
        record.append(record_telephone)
        record.append(record_comment)

        record_name.text = self.name
        record_telephone.text = self.telephone
        record_comment.text = self.comment

        return record

    def __str__(self):
        text = f"{self.name} {self.telephone}"
        if self.comment is not None and len(self.comment) > 0:
            text += f" {self.comment}"
        return text

    @classmethod
    def fromElementTree(cls, elem):
        if type(elem) != ET.Element:
            return None
        name = None
        telephone = None
        comment = None
        for current in elem:
            if current.tag == "name":
                name = current.text
            elif current.tag == "telephone":
                telephone = current.text
            elif current.tag == "comment":
                comment = current.text

        return cls(name, telephone, comment)
from xml.dom import minidom

class Phonebook:
    _instance = None
    _file_name = "text.txt"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.__records = list()
        self.reestablish()

    def import_text(self, text):
        with open(self._file_name, "w", encoding='utf-8') as file:
            file.write(text)

    def export_text(self):
        elem = self.toElementTree()
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def reestablish(self):
        self.__records = list()
        try:
            tree = ET.parse(self._file_name)
        except:
            return
        records = tree.findall('record')
        for record in records:
            obj_record = Record.fromElementTree(record)
            self.__records.append(obj_record)

    def __str__(self):
        records = self.get_records()
        text = ""
        for index, record in enumerate(records):

            text += f"Запись {index + 1} \n"
            text += f"Имя: {record.name} \n"
            text += f"Телефон: {record.telephone} \n"
            text += f"Комментарий: {record.comment} \n"
            text += '\n'
        return text

    def __repr__(self):
        return self.__str__()

    def dump(self):
        elem = self.toElementTree()
        tree = ET.ElementTree(elem)
        tree.write(self._file_name, encoding='utf-8')

    def toElementTree(self):
        records = self.__records
        elem_phonebook = ET.Element("phonebook")
        for record in records:
            elem_record = record.toElementTree()
            elem_phonebook.append(elem_record)
        return elem_phonebook

    def get_records(self):
        return self.__records

    def add_record(self, record):
        self.__records.append(record)

    def validate_index(self, index):
        if type(index) != int:
            raise ValueError("Тип индекса должен быть целым числом")

        if (index > 0) and index > len(self.__records) - 1:
            raise ValueError("Индекс выходит за границы")
        elif index < 0 and abs(index) > len(self.__records):
            raise ValueError("Индекс выходит за границы")

    def __getitem__(self, item):
        self.validate_index(item)
        return self.__records[item]

    def __setitem__(self, key, value):
        if type(value) is not Record:
            raise ValueError("Тип значения должен быть объект класса Record")
        self.validate_index(key)
        self.__records[key] = value

    def __delitem__(self, key):
        self.validate_index(key)
        del self.__records[key]

    def __len__(self):
        return len(self.__records)
