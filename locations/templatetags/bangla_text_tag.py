from django import template

register = template.Library()

@register.filter(is_safe=True)
def en_to_bn_number(value):
    """
    Convert English digits to Bengali digits
    """
    if not value:
        return value
    
    # Convert to string if not already
    value = str(value)
    
    # Mapping of English to Bengali digits
    digit_map = {
        '0': '০',
        '1': '১',
        '2': '২',
        '3': '৩',
        '4': '৪',
        '5': '৫',
        '6': '৬',
        '7': '৭',
        '8': '৮',
        '9': '৯'
    }
    
    # Replace each English digit with its Bengali equivalent
    result = ""
    for char in value:
        if char in digit_map:
            result += digit_map[char]
        else:
            result += char
    
    return result


@register.filter(name='unicode_class', is_safe=True)
def unicode_class(value, default_style=''):
    """
    Determines if text contains Bengali characters and returns appropriate CSS class
    """
    if not value:
        return default_style
    
    # Convert to string if not already
    value = str(value)
    
    # Check if the text contains Bengali characters

    bengali_range = [chr(i) for i in range(0x0980, 0x09FF)]
    has_bengali = any(char in bengali_range for char in value)
    
    if has_bengali:
        return f"'Kalpurush', 'SolaimanLipi', 'BanglaFontNikosh'; letter-spacing: 0.05em; word-spacing: 0.15em;"
    
    return default_style

@register.filter(name='bangla_text_span', is_safe=True)
def bangla_text_span(value, default_style='b_fontekush'):
    if not value:
        return value
    
    value = str(value.strip())
    
    # Check if the text contains Bengali characters
    bengali_range = [chr(i) for i in range(0x0980, 0x09FF)]
    has_bengali = any(char in bengali_range for char in value)
    if has_bengali:
        space = ""
        all_text = ""
        text_bn = ""
        last_char = len(value)
        i = 0
        for char in value:
            i += 1
            if char in bengali_range:
                text_bn += space + char
                if i == last_char:
                    all_text +=f'<span style="font-family: Kalpurush, SolaimanLipi, BanglaFontNikosh;">{text_bn}</span>'
            else:
                if text_bn:
                    all_text +=f'<span style="font-family: Kalpurush, SolaimanLipi, BanglaFontNikosh;">{text_bn}</span>'
                    text_bn = ""
                    if i == last_char:
                        all_text += space + char
                else:
                    all_text += space + char
            space = " " if char == " " else ""
        return all_text
    return value



