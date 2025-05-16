document.addEventListener('DOMContentLoaded', function() {
    const logicalSymbols = {
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
    };

    const logicalSymbolsInputs = document.querySelectorAll('.logical-symbols-input');
    
    logicalSymbolsInputs.forEach(input => {
        const container = document.createElement('div');
        container.className = 'logical-symbols-container';
        
        const symbolsContainer = document.createElement('div');
        symbolsContainer.className = 'logical-symbols-buttons';
        
        const label = document.createElement('div');
        label.className = 'logical-symbols-label';
        label.textContent = 'Click a symbol to insert it at cursor position';
        symbolsContainer.appendChild(label);
        
        Object.entries(logicalSymbols).forEach(([symbol, name]) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'logical-symbol-button';
            button.textContent = symbol;
            button.title = name;
            
            button.addEventListener('click', function(e) {
                e.preventDefault();
                insertSymbol(input, symbol);
            });
            
            symbolsContainer.appendChild(button);
        });
        
        container.appendChild(symbolsContainer);
        input.parentNode.insertBefore(container, input);
    });
});

function insertSymbol(input, symbol) {
    const start = input.selectionStart;
    const end = input.selectionEnd;
    const text = input.value;
    
    input.value = text.substring(0, start) + symbol + text.substring(end);
    
    input.focus();
    input.selectionStart = input.selectionEnd = start + symbol.length;
    
    const button = document.querySelector(`.logical-symbol-button[title="${symbol}"]`);
    if (button) {
        button.classList.add('symbol-inserted');
        setTimeout(() => button.classList.remove('symbol-inserted'), 200);
    }
} 