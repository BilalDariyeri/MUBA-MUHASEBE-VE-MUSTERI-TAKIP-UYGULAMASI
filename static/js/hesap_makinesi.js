// Hesap Makinesi JavaScript
let calculatorDisplay = '0';
let previousValue = null;
let operation = null;
let waitingForNewValue = false;

// Sayfa yüklendiğinde hesap makinesi butonunu göster
document.addEventListener('DOMContentLoaded', function() {
    const floatingBtn = document.getElementById('floating-calculator-btn');
    if (floatingBtn) {
        floatingBtn.style.display = 'flex';
        floatingBtn.style.visibility = 'visible';
        floatingBtn.style.opacity = '1';
    }
});

// Hesap makinesi modal'ını aç
function openCalculator() {
    const modal = document.getElementById('calculator-modal');
    if (modal) {
        modal.style.display = 'block';
        modal.classList.add('show');
        calculatorDisplay = '0';
        previousValue = null;
        operation = null;
        waitingForNewValue = false;
        updateDisplay();
    }
}

// Hesap makinesi modal'ını kapat
function closeCalculator() {
    const modal = document.getElementById('calculator-modal');
    if (modal) {
        modal.style.display = 'none';
        // Modal'ı tamamen gizle
        modal.classList.remove('show');
    }
}

// Ekranı güncelle
function updateDisplay() {
    const display = document.getElementById('calculator-display');
    if (display) {
        display.value = calculatorDisplay;
    }
}

// Sayı butonuna tıklandığında
function inputNumber(num) {
    if (waitingForNewValue) {
        calculatorDisplay = num;
        waitingForNewValue = false;
    } else {
        calculatorDisplay = calculatorDisplay === '0' ? num : calculatorDisplay + num;
    }
    updateDisplay();
}

// Nokta butonuna tıklandığında
function inputDecimal() {
    if (waitingForNewValue) {
        calculatorDisplay = '0.';
        waitingForNewValue = false;
    } else if (calculatorDisplay.indexOf('.') === -1) {
        calculatorDisplay += '.';
    }
    updateDisplay();
}

// İşlem butonuna tıklandığında
function performOperation(nextOperation) {
    const inputValue = parseFloat(calculatorDisplay);

    if (previousValue === null) {
        previousValue = inputValue;
    } else if (operation) {
        const currentValue = previousValue || 0;
        const newValue = calculate(currentValue, inputValue, operation);

        calculatorDisplay = String(newValue);
        previousValue = newValue;
    }

    waitingForNewValue = true;
    operation = nextOperation;
    updateDisplay();
}

// Hesaplama yap
function calculate(firstValue, secondValue, operation) {
    switch (operation) {
        case '+':
            return firstValue + secondValue;
        case '-':
            return firstValue - secondValue;
        case '*':
            return firstValue * secondValue;
        case '/':
            return secondValue !== 0 ? firstValue / secondValue : 0;
        case '=':
            return secondValue;
        default:
            return secondValue;
    }
}

// Eşittir butonuna tıklandığında
function calculateResult() {
    const inputValue = parseFloat(calculatorDisplay);

    if (previousValue !== null && operation) {
        const newValue = calculate(previousValue, inputValue, operation);
        calculatorDisplay = String(newValue);
        previousValue = null;
        operation = null;
        waitingForNewValue = true;
        updateDisplay();
    }
}

// Temizle (C)
function clearAll() {
    calculatorDisplay = '0';
    previousValue = null;
    operation = null;
    waitingForNewValue = false;
    updateDisplay();
}

// Son karakteri sil (CE)
function clearEntry() {
    calculatorDisplay = '0';
    waitingForNewValue = false;
    updateDisplay();
}

// Geri al (Backspace)
function backspace() {
    if (calculatorDisplay.length > 1) {
        calculatorDisplay = calculatorDisplay.slice(0, -1);
    } else {
        calculatorDisplay = '0';
    }
    updateDisplay();
}

// Klavye desteği
document.addEventListener('keydown', function(event) {
    const calculatorModal = document.getElementById('calculator-modal');
    if (calculatorModal && calculatorModal.style.display === 'block') {
        const key = event.key;
        
        if (key >= '0' && key <= '9') {
            inputNumber(key);
        } else if (key === '.') {
            inputDecimal();
        } else if (key === '+') {
            event.preventDefault();
            performOperation('+');
        } else if (key === '-') {
            event.preventDefault();
            performOperation('-');
        } else if (key === '*') {
            event.preventDefault();
            performOperation('*');
        } else if (key === '/') {
            event.preventDefault();
            performOperation('/');
        } else if (key === 'Enter' || key === '=') {
            event.preventDefault();
            calculateResult();
        } else if (key === 'Escape') {
            event.preventDefault();
            closeCalculator();
        } else if (key === 'Backspace') {
            event.preventDefault();
            backspace();
        } else if (key === 'c' || key === 'C') {
            event.preventDefault();
            clearAll();
        }
    }
});

// Modal dışına tıklanınca kapat
window.addEventListener('click', function(event) {
    const calculatorModal = document.getElementById('calculator-modal');
    if (event.target === calculatorModal) {
        closeCalculator();
    }
});

