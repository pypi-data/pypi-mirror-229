# import pytest
# from requests_helpers_jimmykvick.firestore import add_document

# def test_add_document_valid(mocker):
  
#   # mockear firestore_instance para que retorne un objeto falso
#   mock_db = mocker.MagicMock()
#   mock_doc_ref = mocker.MagicMock()
#   mock_db.collection().document.return_value = mock_doc_ref
#   mocker.patch('requests_helpers_jimmykvick.firestore.firestore_instance', return_value=mock_db)
  
#   collection = "collection"
#   body = { 'key': 'content' }
  
#   doc_id = add_document(collection, body)
  
#   assert mock_db.collection.call_count == 2
#   mock_doc_ref.set.assert_called_once_with(body)
  
#   assert doc_id is not None
  
# def test_add_document_invalid_collection(mocker):
#   print("Testing add_document invalid_collection")
#   with pytest.raises(ValueError, match="collection not defined"):
#     add_document(None, { "key": "value" })
    
# def test_add_document_invalid_body(mocker):
#   with pytest.raises(ValueError, match="body must be a non-empty dictionary"):
#     add_document("a", None)
