
def test_config(app):
    assert app.config['TESTING'] == True
    assert app.config['AZURE_KEY'] == 'test_key'
    assert app.config['AZURE_ENDPOINT'] == 'https://test.azure.com'