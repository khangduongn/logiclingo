document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('textarea[maxlength], input[maxlength]');
    
    inputs.forEach(input => {
        const maxLength = input.getAttribute('maxlength');
        const counter = document.createElement('div');
        counter.className = 'character-counter text-muted small mt-1';
        counter.textContent = `0/${maxLength} characters`;
        
        input.parentNode.insertBefore(counter, input.nextSibling);
        
        input.addEventListener('input', function() {
            const currentLength = this.value.length;
            counter.textContent = `${currentLength}/${maxLength} characters`;
            
            if (currentLength > maxLength * 0.9) {
                counter.classList.add('text-danger');
            } else {
                counter.classList.remove('text-danger');
            }
        });
        
        input.dispatchEvent(new Event('input'));
    });
}); 