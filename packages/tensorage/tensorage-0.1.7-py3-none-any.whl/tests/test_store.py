import unittest
from unittest.mock import MagicMock, patch
import warnings

import numpy as np

from tensorage.store import TensorStore, StoreSlicer
from tensorage.types import Dataset

# when running tests, remove stuff loaded from local .env files
import os
if 'SUPABASE_URL' in os.environ:
    os.environ.pop('SUPABASE_URL')
if 'SUPABASE_KEY' in os.environ:
    os.environ.pop('SUPABASE_KEY')


class TestTensorStore(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def test_store_init(self):
        """
        Test that the store gets initialized correctly.
        """
        # create a mock backend
        backend = MagicMock()

        # create the store
        store = TensorStore(backend)
        
        # make sure schema has been checked
        backend.database.return_value.__enter__.return_value.check_schema_installed.assert_called_once()

    def test_store_init_raises_warning(self):
        """
        Test that the store raises a warning if the schema is not installed.
        """
        # create a mock backend
        backend = MagicMock()

        # mock the schema installed method
        backend.database.return_value.__enter__.return_value.check_schema_installed.return_value = False

        # create the store and catch the warning
        with warnings.catch_warnings(record=True) as w:
            store = TensorStore(backend)
            
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "The schema for the TensorStore is not installed." in str(w[-1].message)

    def test_create_tensor_single_batch(self):
        """
        Mock the backend of the DatabaseSession and assert that the correct functions
        have been called.
        """
        # create a mock backend
        backend = MagicMock()
        
        # create the store
        store = TensorStore(backend)

        # create the dataset
        data = np.random.random((10, 10, 10))
        dataset = Dataset(13, 'test', data.shape, data.ndim, 'float32', False)
        backend.database.return_value.__enter__.return_value.insert_dataset.return_value = dataset

        # create a tensor
        store['test'] = data

        # assert that the dataset has been created
        backend.database.return_value.__enter__.return_value.insert_dataset.assert_called_once_with('test', data.shape, data.ndim)
        
        # assert that the tensor has been created
        backend.database.return_value.__enter__.return_value.insert_tensor.assert_called_once()
        
        # assert that the dataset id has been passed correctly
        assert backend.database.return_value.__enter__.return_value.insert_tensor.call_args[0][0] == dataset.id

        for expected, actual in zip(data, backend.database.return_value.__enter__.return_value.insert_tensor.call_args[0][1]):
            np.testing.assert_array_almost_equal(expected, actual)
    
    def test_create_tensor_multiple_batches(self):
        """
        Mock the backend of the DatabaseSession and assert that the correct functions
        have been called.
        """
        # create a mock backend
        backend = MagicMock()

        # create the store
        store = TensorStore(backend)

        # create the dataset
        data = np.random.random((30, 10, 10))
        dataset = Dataset(14, 'test2', data.shape, data.ndim, 'float32', False)
        backend.database.return_value.__enter__.return_value.insert_dataset.return_value = dataset

        # set a smaller chunk size to simulate multiple batches
        store.chunk_size = data.shape[1] * data.shape[2] * 2  # data.shape[0] // 2 is batch size
        
        # create the tensor
        store['test2'] = data

        # assert that the dataset has been created
        backend.database.return_value.__enter__.return_value.insert_dataset.assert_called_once_with('test2', data.shape, data.ndim)

        # assert that the tensor has been created
        expected_batch_size = int(np.ceil(data.shape[0] / 2))
        assert backend.database.return_value.__enter__.return_value.insert_tensor.call_count == expected_batch_size

    def test_overwrite_dataset(self):
        """
        Mock the backend as if a key already exists and assert that the remove_dataset
        function is called, before the new dataset is inserted.
        """
        # create a mock backend
        backend = MagicMock()

        # mock the list_dataset_keys backend function
        backend.database.return_value.__enter__.return_value.list_dataset_keys.return_value = ['test']

        # create the store
        store = TensorStore(backend, allow_overwrite=True)

        # create the dataset
        data = np.random.random((10, 10, 10))
        dataset = Dataset(14, 'test', data.shape, data.ndim, 'float32', False)

        # create a tensor with a duplicated key
        store['test'] = data

        # make sure the remove_dataset function has been called
        backend.database.return_value.__enter__.return_value.remove_dataset.assert_called_once_with('test')

        # make sure the insert_dataset function has also been called
        backend.database.return_value.__enter__.return_value.insert_dataset.assert_called_once_with('test', data.shape, data.ndim)
    
    def test_overwrite_not_allowed(self):
        """
        Test that a ValueError is raised if a key already exists and allow_overwrite is False.
        """
        # create a mock backend
        backend = MagicMock()

        # mock the list_dataset_keys backend function
        backend.database.return_value.__enter__.return_value.list_dataset_keys.return_value = ['test']

        # create the store
        store = TensorStore(backend, allow_overwrite=False)

        # assert the expection is raised
        with self.assertRaises(ValueError) as err:
            store['test'] = np.random.random((10, 10, 10))
        
        assert str(err.exception) == "The key 'test' already exists in the TensorStore. Set allow_overwrite=True to overwrite the existing dataset."

    def test_transform_tensor_shape(self):
        """
        Pass a 1D numpy array and make sure, that the dataset is created using the correct shape.
        """
        # create a mock backend
        backend = MagicMock()

        # create the store
        store = TensorStore(backend)

        # create the 1D dataset
        store['test'] = np.zeros((100,))

        # make sure the dataset was created correctly
        backend.database.return_value.__enter__.return_value.insert_dataset.assert_called_once_with('test', (1, 100), 2)

        # extract the passed numpy and check the shape
        passed_numpy = backend.database.return_value.__enter__.return_value.insert_tensor.call_args[0][1][0]
        assert passed_numpy.shape == (100, )
    
    def test_cast_input_data(self):
        """
        Pass the data as plain list and make sure, that it gets casted to numpy.
        """
        # create a mock backend
        backend = MagicMock()

        # create the store
        store = TensorStore(backend)

        # create the dataset
        data = np.ones((100, 100, 100)).tolist()

        # create the tensor
        store['test'] = data

        # make sure the dataset was created correctly
        backend.database.return_value.__enter__.return_value.insert_dataset.assert_called_once_with('test', (100, 100, 100), 3)

        # extract the passed data and stick it together
        passed_data = backend.database.return_value.__enter__.return_value.insert_tensor.call_args[0][1]
        
        # assert all chunks are of type numpy.ndarray
        assert all([isinstance(chunk, np.ndarray) for chunk in passed_data])

    def test_store_contains_key(self):
        """
        Test that the __contains__ method works correctly.
        """
        # create a mock backend
        backend = MagicMock()

        # mock the list_dataset_keys backend function
        backend.database.return_value.__enter__.return_value.list_dataset_keys.return_value = ['foo', 'bar']

        # create the store
        store = TensorStore(backend)

        # assert that the store contains the key 'foo'
        assert 'foo' in store

        # assert that the store does not contain the key 'baz'
        assert 'baz' not in store

    def test_store_dataset_len(self):
        """
        Test that the __len__ method works correctly.
        """
        # create a mock backend
        backend = MagicMock()

        # mock the list_dataset_keys backend function
        backend.database.return_value.__enter__.return_value.list_dataset_keys.return_value = ['foo', 'bar']

        # create the store
        store = TensorStore(backend)

        # assert that the store contains two datasets
        assert len(store) == 2

    def test_get_full_tensor(self):
        """
        Mock the backend and check that the data is loaded correctly
        """
        # create the backend
        backend = MagicMock()
        
        # mock tge get dataset function
        backend.database.return_value.__enter__.return_value.get_dataset.return_value = Dataset(1, 'foo', [30, 100, 5], 3, 'float32', False)

        # mock the get_tensor function for the full dataset
        backend.database.return_value.__enter__.return_value.get_tensor.return_value = np.random.random((30, 100, 5))

        # create the store
        store = TensorStore(backend)

        # get the data
        data = store['foo']

        # make sure the indices were passed correctly
        backend.database.return_value.__enter__.return_value.get_tensor.assert_called_once_with('foo', 1, 31, [1, 1], [101, 6])

        # assert that the data has the correct shape
        assert data.shape == (30, 100, 5)

    def test_get_tesor_by_attr(self):
        """
        Mock the backend and check that the data is loaded correctly via attributes
        """
        # create the backend
        backend = MagicMock()
        
        # mock the list of existing datasets
        backend.database.return_value.__enter__.return_value.list_dataset_keys.return_value = ['foo']

        # mock tge get dataset function
        backend.database.return_value.__enter__.return_value.get_dataset.return_value = Dataset(1, 'foo', [30, 100, 5], 3, 'float32', False)

        # mock the get_tensor function for the full dataset
        backend.database.return_value.__enter__.return_value.get_tensor.return_value = np.random.random((30, 100, 5))

        # create the store
        store = TensorStore(backend)

        # get the data by attribute
        foo_slice = store.foo

        # make sure data is a numpy array
        assert isinstance(foo_slice, StoreSlicer)
        data = foo_slice()

        # make sure the indices were passed correctly
        backend.database.return_value.__enter__.return_value.get_tensor.assert_called_once_with('foo', 1, 31, [1, 1], [101, 6])

        # assert that the data has the correct shape
        assert data.shape == (30, 100, 5)
    
    def test_tensor_slicing(self):
        """
        """
        # create the backend
        backend = MagicMock()
        
        # mock the list of existing datasets
        backend.database.return_value.__enter__.return_value.list_dataset_keys.return_value = ['foo']

        # mock tge get dataset function
        backend.database.return_value.__enter__.return_value.get_dataset.return_value = Dataset(1, 'foo', [30, 100, 5], 3, 'float32', False)

        # mock the get_tensor function for the full dataset
        backend.database.return_value.__enter__.return_value.get_tensor.return_value = np.random.random((30, 20, 1))

        # create the store
        store = TensorStore(backend)

        # get the data by attribute
        data = store.foo[:, 10:30, 4]

        # make sure the indices were passed correctly
        backend.database.return_value.__enter__.return_value.get_tensor.assert_called_once_with('foo', 1, 31, [11, 5], [31, 5])

        # assert that the data has the correct shape
        assert data.shape == (30, 20, 1)

    def test_tensor_slice_without_attr(self):
         # create the backend
        backend = MagicMock()
        
        # mock the list of existing datasets
        backend.database.return_value.__enter__.return_value.list_dataset_keys.return_value = ['foo']

        # mock tge get dataset function
        backend.database.return_value.__enter__.return_value.get_dataset.return_value = Dataset(1, 'foo', [30, 100, 5], 3, 'float32', False)

        # mock the get_tensor function for the full dataset
        backend.database.return_value.__enter__.return_value.get_tensor.return_value = np.random.random((10, 100, 2))

        # create the store
        store = TensorStore(backend)
        
        # slice the data
        data = store['foo', :10, :, 2:3]

        # make sure the indices were passed correctly
        backend.database.return_value.__enter__.return_value.get_tensor.assert_called_once_with('foo', 1, 11, [1, 3], [101, 4])

        # assert that the data has the correct shape
        assert data.shape == (10, 100, 2)

    def test_missing_key(self):
        """
        Test that a missing key in the store raises an AttributeError informing the user.
        """
        # create the backend
        backend = MagicMock()

        # create the store
        store = TensorStore(backend)

        # call a key that does not exist
        with self.assertRaises(AttributeError) as err:
            store.foo

        self.assertTrue("'TensorStore' object has no attribute 'foo'" in str(err.exception))

        # call by slice and leave out the key
        with self.assertRaises(KeyError) as err:
            store[:, 10:20, 5]
        
        self.assertTrue("You need to pass the key as first argument" in str(err.exception))

    def test_dir_method(self):
        """
        Add a few keys and find them in in __dir__ along with instance methods.
        """
        # create the backend
        backend = MagicMock()

        # mock a few keys
        backend.database.return_value.__enter__.return_value.list_dataset_keys.return_value = ['foo', 'bar']

        # create the store
        store = TensorStore(backend)

        # get the dir
        dir_list = dir(store)

        # assert that the keys are in the dir
        assert 'foo' in dir_list
        assert 'bar' in dir_list

        # assert that the instance methods and attributes are in the dir
        assert 'chunk_size' in dir_list
        assert 'keys' in dir_list

    def test_slicing_options(self):
        """
        Test StoreSlicer indexer methods
        """
        # create a mock backend
        backend = MagicMock()

        # create the store
        store = TensorStore(backend)

        # create a dataset
        dataset = Dataset(1, 'foo', [30, 100, 20, 5], 4, 'float32', False)

        # create a StoreSlicer
        slicer = StoreSlicer(_store=store, key='foo', dataset=dataset)

        # test slice options without slicing
        _, idx, slc = slicer.get_iloc_slices()
        assert idx == [1, 31]
        assert slc == [[1, 101], [1, 21], [1, 6]]
        
        # pass only 1 argument, along first axis
        _, idx, slc = slicer.get_iloc_slices(10)
        assert idx == [11, 12]
        assert slc == [[1, 101], [1, 21], [1, 6]]

        # pass more than one argument, but lack one dimension
        _, idx, slc = slicer.get_iloc_slices(10, slice(5, 7))
        assert idx == [11, 12]
        assert slc == [[6, 8], [1, 21], [1, 6]]

    def test_slicer_argument_errors(self):
        """
        Test the slicing argument errors of the StoreSlicer
        """
        # create a mock backend
        backend = MagicMock()

        # create the store
        store = TensorStore(backend)

        # create a dataset
        dataset = Dataset(1, 'foo', [30, 100, 20, 5], 4, 'float32', False)

        # create a StoreSlicer
        slicer = StoreSlicer(_store=store, key='foo', dataset=dataset)

        # test KeyError on non-numerical key
        with self.assertRaises(KeyError) as err:
            slicer.get_iloc_slices('foo')
        assert "Batch index needs to be" in str(err.exception)

        # test slice non-numerical key error
        with self.assertRaises(KeyError) as err:
            slicer.get_iloc_slices(10, 'foobar')
        assert "Slice needs to be passed as int or slice" in str(err.exception)


if __name__ == '__main__':
    unittest.main()
