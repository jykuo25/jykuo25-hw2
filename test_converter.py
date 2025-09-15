import pytest
import json
import base64
from api.index import (
    app, text_to_number, number_to_text, 
    base64_to_number, number_to_base64
)


class TestNumberConversionFunctions:
    """Test individual conversion functions"""
    
    def test_text_to_number_basic(self):
        """Test basic text to number conversions"""
        assert text_to_number("one") == 1
        assert text_to_number("two") == 2
        assert text_to_number("three") == 3
        assert text_to_number("four") == 4
        assert text_to_number("five") == 5
        assert text_to_number("six") == 6
        assert text_to_number("seven") == 7
        assert text_to_number("eight") == 8
        assert text_to_number("nine") == 9
        assert text_to_number("ten") == 10
        assert text_to_number("zero") == 0
        assert text_to_number("nil") == 0
    
    def test_text_to_number_case_insensitive(self):
        """Test text to number is case insensitive"""
        assert text_to_number("ONE") == 1
        assert text_to_number("Two") == 2
        assert text_to_number("ZERO") == 0
    
    def test_text_to_number_with_punctuation(self):
        """Test text to number handles punctuation"""
        assert text_to_number("one!") == 1
        assert text_to_number("two@") == 2
        assert text_to_number("three.") == 3
    
    def test_text_to_number_invalid(self):
        """Test text to number with invalid input"""
        with pytest.raises(ValueError, match="Unable to convert text to number"):
            text_to_number("invalid")
        with pytest.raises(ValueError, match="Unable to convert text to number"):
            text_to_number("cat")
    
    def test_number_to_text_basic(self):
        """Test basic number to text conversions"""
        assert number_to_text(0) == "zero"
        assert number_to_text(1) == "one"
        assert number_to_text(5) == "five"
        assert number_to_text(10) == "ten"
        assert number_to_text(42) == "forty-two"
        assert number_to_text(100) == "one hundred"
        assert number_to_text(123) == "one hundred and twenty-three"
    
    def test_base64_conversion_little_endian(self):
        """Test base64 conversion uses little-endian byte order"""
        # Test with number 42 (0x2A)
        # In little-endian: 42 = [42, 0] = "Kg=="
        # In big-endian: 42 = [0, 42] = "ACo="
        expected_b64 = base64.b64encode((42).to_bytes(1, byteorder='little')).decode('utf-8')
        assert number_to_base64(42) == expected_b64
        
        # Test round-trip conversion
        original = 42
        b64_str = number_to_base64(original)
        converted_back = base64_to_number(b64_str)
        assert converted_back == original
    
    def test_base64_conversion_edge_cases(self):
        """Test base64 conversion with edge cases"""
        # Test zero
        assert base64_to_number(number_to_base64(0)) == 0
        
        # Test large number
        large_num = 123456789
        assert base64_to_number(number_to_base64(large_num)) == large_num
        
        # Test single byte
        single_byte = 255
        assert base64_to_number(number_to_base64(single_byte)) == single_byte
    
    def test_base64_invalid_input(self):
        """Test base64 with invalid input"""
        with pytest.raises(ValueError, match="Invalid base64 input"):
            base64_to_number("invalid_base64!")
        
        with pytest.raises(ValueError, match="Invalid base64 input"):
            base64_to_number("")
        
        # Test with malformed base64
        with pytest.raises(ValueError, match="Invalid base64 input"):
            base64_to_number("abc!")


class TestSameTypeConversion:
    """Test that same input/output types return the input unchanged"""
    
    def test_same_type_text(self):
        """Test text to text returns original"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': 'five',
                                 'inputType': 'text',
                                 'outputType': 'text'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == 'five'
        assert data['error'] is None
    
    def test_same_type_binary(self):
        """Test binary to binary returns original"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '101010',
                                 'inputType': 'binary',
                                 'outputType': 'binary'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == '101010'
        assert data['error'] is None
    
    def test_same_type_octal(self):
        """Test octal to octal returns original"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '52',
                                 'inputType': 'octal',
                                 'outputType': 'octal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == '52'
        assert data['error'] is None
    
    def test_same_type_decimal(self):
        """Test decimal to decimal returns original"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '42',
                                 'inputType': 'decimal',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == '42'
        assert data['error'] is None
    
    def test_same_type_hexadecimal(self):
        """Test hexadecimal to hexadecimal returns original"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '2a',
                                 'inputType': 'hexadecimal',
                                 'outputType': 'hexadecimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == '2a'
        assert data['error'] is None
    
    def test_same_type_base64(self):
        """Test base64 to base64 returns original"""
        client = app.test_client()
        original_b64 = number_to_base64(42)
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': original_b64,
                                 'inputType': 'base64',
                                 'outputType': 'base64'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == original_b64
        assert data['error'] is None


class TestCrossTypeConversions:
    """Test conversions between different types"""
    
    def test_text_to_binary(self):
        """Test text to binary conversion"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': 'five',
                                 'inputType': 'text',
                                 'outputType': 'binary'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == '101'
        assert data['error'] is None
    
    def test_text_to_decimal(self):
        """Test text to decimal conversion"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': 'ten',
                                 'inputType': 'text',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == '10'
        assert data['error'] is None

        # Test bug
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': 'forty two',
                                 'inputType': 'text',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == '42'
        assert data['error'] is None
    
    def test_binary_to_text(self):
        """Test binary to text conversion"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '1010',
                                 'inputType': 'binary',
                                 'outputType': 'text'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == 'ten'
        assert data['error'] is None
    
    def test_decimal_to_binary(self):
        """Test decimal to binary conversion"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '42',
                                 'inputType': 'decimal',
                                 'outputType': 'binary'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == '101010'
        assert data['error'] is None
    
    def test_hexadecimal_to_octal(self):
        """Test hexadecimal to octal conversion"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '2a',
                                 'inputType': 'hexadecimal',
                                 'outputType': 'octal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == '52'
        assert data['error'] is None
    
    def test_base64_to_text(self):
        """Test base64 to text conversion"""
        client = app.test_client()
        b64_input = number_to_base64(7)
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': b64_input,
                                 'inputType': 'base64',
                                 'outputType': 'text'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] == 'seven'
        assert data['error'] is None
    
    def test_text_to_base64(self):
        """Test text to base64 conversion"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': 'three',
                                 'inputType': 'text',
                                 'outputType': 'base64'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        expected_b64 = number_to_base64(3)
        assert data['result'] == expected_b64
        assert data['error'] is None
    
    def test_comprehensive_round_trip(self):
        """Test comprehensive round-trip conversions"""
        test_value = 5  # Use 5 since "five" is supported in text conversion
        
        # Test all formats can convert to each other and back
        formats = {
            'decimal': str(test_value),
            'binary': bin(test_value)[2:],
            'octal': oct(test_value)[2:],
            'hexadecimal': hex(test_value)[2:],
            'base64': number_to_base64(test_value),
            'text': number_to_text(test_value)
        }
        
        client = app.test_client()
        
        # Test all combinations
        for input_format, input_value in formats.items():
            for output_format, expected_output in formats.items():
                response = client.post('/convert', 
                                     data=json.dumps({
                                         'input': input_value,
                                         'inputType': input_format,
                                         'outputType': output_format
                                     }),
                                     content_type='application/json')
                data = json.loads(response.data)
                assert data['error'] is None, f"Error converting {input_format} to {output_format}: {data.get('error')}"
                assert data['result'] == expected_output, f"Expected {expected_output}, got {data['result']} for {input_format} to {output_format}"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_zero_conversions(self):
        """Test zero in all formats"""
        client = app.test_client()
        
        zero_formats = {
            'decimal': '0',
            'binary': '0',
            'octal': '0',
            'hexadecimal': '0',
            'base64': number_to_base64(0),
            'text': 'zero'
        }
        
        for input_format, input_value in zero_formats.items():
            for output_format, expected_output in zero_formats.items():
                response = client.post('/convert', 
                                     data=json.dumps({
                                         'input': input_value,
                                         'inputType': input_format,
                                         'outputType': output_format
                                     }),
                                     content_type='application/json')
                data = json.loads(response.data)
                assert data['error'] is None, f"Error with zero conversion {input_format} to {output_format}"
                assert data['result'] == expected_output
    
    def test_invalid_binary_input(self):
        """Test invalid binary input"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '102',
                                 'inputType': 'binary',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is not None
        assert data['result'] is None
    
    def test_invalid_octal_input(self):
        """Test invalid octal input"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '89',
                                 'inputType': 'octal',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is not None
        assert data['result'] is None
    
    def test_invalid_hexadecimal_input(self):
        """Test invalid hexadecimal input"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': 'gh',
                                 'inputType': 'hexadecimal',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is not None
        assert data['result'] is None
    
    def test_invalid_base64_input(self):
        """Test invalid base64 input"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': 'invalid_base64!',
                                 'inputType': 'base64',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is not None
        assert data['result'] is None
    
    def test_invalid_text_input(self):
        """Test invalid text input"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': 'cat',
                                 'inputType': 'text',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is not None
        assert data['result'] is None
    
    def test_empty_input(self):
        """Test empty input"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '',
                                 'inputType': 'decimal',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is not None
        assert data['result'] is None
    
    def test_invalid_input_type(self):
        """Test invalid input type"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '42',
                                 'inputType': 'invalid',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is not None
        assert data['result'] is None
    
    def test_invalid_output_type(self):
        """Test invalid output type"""
        client = app.test_client()
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '42',
                                 'inputType': 'decimal',
                                 'outputType': 'invalid'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is not None
        assert data['result'] is None
    
    def test_missing_json_fields(self):
        """Test missing required JSON fields"""
        client = app.test_client()
        
        # Missing input
        response = client.post('/convert', 
                             data=json.dumps({
                                 'inputType': 'decimal',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is not None
        
        # Missing inputType
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '42',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is not None
        
        # Missing outputType
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '42',
                                 'inputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is not None


class TestFlaskEndpoints:
    """Test Flask endpoints and responses"""
    
    def test_index_route(self):
        """Test index route returns HTML"""
        client = app.test_client()
        response = client.get('/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type
        assert 'Numeric Converter' in response.get_data(as_text=True)
    
    def test_convert_route_methods(self):
        """Test convert route only accepts POST"""
        client = app.test_client()
        
        # GET should return 405 Method Not Allowed
        response = client.get('/convert')
        assert response.status_code == 405
        
        # POST should work
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': '42',
                                 'inputType': 'decimal',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        assert response.status_code == 200
    
    def test_convert_route_content_type(self):
        """Test convert route requires JSON content type"""
        client = app.test_client()
        
        # JSON content type should work
        response = client.post('/convert', 
                             data='{"input": "42", "inputType": "decimal", "outputType": "decimal"}',
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == '42'
        
        # Non-JSON content type should fail to parse properly
        response = client.post('/convert', 
                             data='{"input": "42", "inputType": "decimal", "outputType": "decimal"}',
                             content_type='text/plain')
        assert response.status_code == 200
        data = json.loads(response.data)
        # Flask may not parse non-JSON content properly, so we expect an error
        assert data['error'] is not None


class TestLargeNumbers:
    """Test with larger numbers to ensure proper handling"""
    
    def test_large_number_conversions(self):
        """Test conversions with larger numbers"""
        client = app.test_client()
        large_num = 123456789
        
        # Test decimal to all other formats
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': str(large_num),
                                 'inputType': 'decimal',
                                 'outputType': 'binary'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is None
        assert data['result'] == bin(large_num)[2:]
        
        # Test decimal to hexadecimal
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': str(large_num),
                                 'inputType': 'decimal',
                                 'outputType': 'hexadecimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is None
        assert data['result'] == hex(large_num)[2:]
        
        # Test decimal to base64
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': str(large_num),
                                 'inputType': 'decimal',
                                 'outputType': 'base64'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is None
        assert data['result'] == number_to_base64(large_num)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
