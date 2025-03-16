#!/usr/bin/python3
"""
Contains the TestFileStorageDocs classes
"""

import os
import pep8
import unittest
from datetime import datetime
import inspect
import models
from models import engine
from models.engine.file_storage import file_storage
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
import json
from os import environ, stat, remove, path


STORAGE_TYPE = environ.get('HBNB_TYPE_STORAGE')
classes = {"Amenity": Amenity, "BaseModel": BaseModel, "City": City,
           "Place": Place, "Review": Review, "State": State, "User": User}

if STORAGE_TYPE != 'db':
    FileStorage = models.file_storage.FileStorage
storage = models.storage
F = './dev/file.json'


@unittest.skipIf(STORAGE_TYPE == 'db', 'skip if environ is not db')
class TestFileStorageDocs(unittest.TestCase):
    """Tests to check the documentation and style of FileStorage class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.fs_f = inspect.getmembers(FileStorage, inspect.isfunction)

    def tearDownClass():
        """ Resets the tests storage objects"""
        storage.delete_all()

    def test_pep8_conformance_file_storage(self):
        """Test that models/engine/file_storage.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['models/engine/file_storage.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_file_storage(self):
        """Test tests/test_models/test_file_storage.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        path_to_test = 'tests/test_models/test_engine/test_file_storage.py'
        result = pep8s.check_files([path_to_test])
        self.assertEqual(result.total_errors, 0, result.messages)

    def test_file_storage_module_docstring(self):
        """Test for the file_storage.py module docstring"""
        self.assertIsNot(file_storage.__doc__, None,
                         "file_storage.py needs a docstring")
        self.assertTrue(len(file_storage.__doc__) >= 1,
                        "file_storage.py needs a docstring")

    def test_file_storage_class_docstring(self):
        """Test for the FileStorage class docstring"""
        self.assertIsNot(FileStorage.__doc__, None,
                         "FileStorage class needs a docstring")
        self.assertTrue(len(FileStorage.__doc__) >= 1,
                        "FileStorage class needs a docstring")

    def test_fs_func_docstrings(self):
        """Test for the presence of docstrings in FileStorage methods"""
        for func in self.fs_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


@unittest.skipIf(STORAGE_TYPE == 'db', 'skip if environ is not db')
class TestFileStorage(unittest.TestCase):
    """Test the FileStorage class"""
    @unittest.skipIf(models.storage_t == 'db', "not testing file storage")
    def test_all_returns_dict(self):
        """Test that all returns the FileStorage.__objects attr"""
        storage = FileStorage()
        new_dict = storage.all()
        self.assertEqual(type(new_dict), dict)
        self.assertIs(new_dict, storage._FileStorage__objects)

    @unittest.skipIf(models.storage_t == 'db', "not testing file storage")
    def test_new(self):
        """test that new adds an object to the FileStorage.__objects attr"""
        storage = FileStorage()
        save = FileStorage._FileStorage__objects
        FileStorage._FileStorage__objects = {}
        test_dict = {}
        for key, value in classes.items():
            with self.subTest(key=key, value=value):
                instance = value()
                instance_key = instance.__class__.__name__ + "." + instance.id
                storage.new(instance)
                test_dict[instance_key] = instance
                self.assertEqual(test_dict, storage._FileStorage__objects)
        FileStorage._FileStorage__objects = save

    @unittest.skipIf(models.storage_t == 'db', "not testing file storage")
    def test_save(self):
        """Test that save properly saves objects to file.json"""
        storage = FileStorage()
        new_dict = {}
        for key, value in classes.items():
            instance = value()
            instance_key = instance.__class__.__name__ + "." + instance.id
            new_dict[instance_key] = instance
        save = FileStorage._FileStorage__objects
        FileStorage._FileStorage__objects = new_dict
        storage.save()
        FileStorage._FileStorage__objects = save
        for key, value in new_dict.items():
            new_dict[key] = value.to_dict()
        string = json.dumps(new_dict)
        with open("file.json", "r") as f:
            js = f.read()
        self.assertEqual(json.loads(string), json.loads(js))


@unittest.skipIf(STORAGE_TYPE == 'db', 'skip if environ is not db')
class TestFileStorageGetCount(unittest.TestCase):
    """ Test for `get` and `count` methods of FileStorage """
    @classmethod
    def setUpClass(cls):
        """ Sets up FileStorage get and count """
        cls.storage = storage
        cls.storage.reload()
        cls.start = cls.storage.count()

    def test_get(self):
        """Test `get` with new State instance and save"""
        state = State(name="NewState")
        self.storage.new(state)
        self.storage.save()
        retrieved = self.storage.get(State, state.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, state.id)

    def test_count(self):
        """ Test `count` method with current State objects """
        start = self.storage.count(State)
        state = State(name="NewerState")
        self.storage.new(state)
        self.storage.save()
        new_count = self.storage.count(State)
        self.assertEqual(new_count, start + 1)
        self.assertEqual(self.storage.count(), self.storage.count())


if __name__ == '__main__':
    unittest.main()
