from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def logical_symbols_buttons():
    symbols = {
        '∧': 'AND',
        '∨': 'OR',
        '¬': 'NOT',
        '→': 'IMPLIES',
        '↔': 'IFF',
        '∀': 'FORALL',
        '∃': 'EXISTS',
        '⊤': 'TRUE',
        '⊥': 'FALSE',
        '≡': 'EQUIVALENT',
        '≠': 'NOT_EQUAL',
        '∈': 'IN',
        '∉': 'NOT_IN',
        '⊂': 'SUBSET',
        '⊃': 'SUPERSET',
        '∪': 'UNION',
        '∩': 'INTERSECTION',
        '∅': 'EMPTY_SET'
    }
    
    buttons = []
    for symbol, name in symbols.items():
        button = f'<button type="button" class="logical-symbol-button" title="{name}" onclick="insertSymbol(this, \'{symbol}\')">{symbol}</button>'
        buttons.append(button)
    
    return mark_safe(f'<div class="logical-symbols-buttons">{"".join(buttons)}</div>') 