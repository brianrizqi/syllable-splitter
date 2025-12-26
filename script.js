class SyllableSplitter {
    constructor(consonant = null, vocal = null, doubleConsonant = null) {
        this.consonant = [
            'b', 'c', 'd', 'f', 'g', 'h', 'j',
            'k', 'l', 'm', 'n', 'p', 'q', 'r',
            's', 't', 'v', 'w', 'x', 'y', 'z',
            'ng', 'ny', 'sy', 'ch', 'dh', 'gh',
            'kh', 'ph', 'sh', 'th'
        ].concat(consonant || []);

        this.doubleConsonant = ['ll', 'ks', 'rs', 'rt'].concat(doubleConsonant || []);
        this.vocal = ['a', 'e', 'i', 'o', 'u'].concat(vocal || []);
    }

    splitLetters(string) {
        let letters = [];
        let arrange = [];

        while (string !== '') {
            let letter = string.substring(0, 2);

            if (this.doubleConsonant.includes(letter.toLowerCase())) {
                if (string.length > 2 && this.vocal.includes(string[2].toLowerCase())) {
                    letters.push(letter[0]);
                    arrange.push('c');
                    string = string.substring(1);
                } else {
                    letters.push(letter);
                    arrange.push('c');
                    string = string.substring(2);
                }
            } else if (this.consonant.includes(letter.toLowerCase())) {
                letters.push(letter);
                arrange.push('c');
                string = string.substring(2);
            } else if (this.vocal.includes(letter.toLowerCase())) {
                letters.push(letter);
                arrange.push('v');
                string = string.substring(2);
            } else {
                letter = string[0];

                if (this.consonant.includes(letter.toLowerCase())) {
                    letters.push(letter);
                    arrange.push('c');
                    string = string.substring(1);
                } else if (this.vocal.includes(letter.toLowerCase())) {
                    letters.push(letter);
                    arrange.push('v');
                    string = string.substring(1);
                } else {
                    letters.push(letter);
                    arrange.push('s');
                    string = string.substring(1);
                }
            }
        }

        return [letters, arrange.join('')];
    }

    splitSyllablesFromLetters(letters, arrange) {
        // Pattern: vc{2,} - vocal followed by 2+ consonants
        let consonantPattern = /vc{2,}/;
        let match = arrange.match(consonantPattern);
        while (match) {
            let i = match.index + 1;
            letters.splice(i + 1, 0, '|');
            arrange = arrange.substring(0, i + 1) + '|' + arrange.substring(i + 1);
            match = arrange.match(consonantPattern);
        }

        // Pattern: v{2,} - 2+ vocals
        let vocalPattern = /v{2,}/;
        match = arrange.match(vocalPattern);
        while (match) {
            let i = match.index;
            letters.splice(i + 1, 0, '|');
            arrange = arrange.substring(0, i + 1) + '|' + arrange.substring(i + 1);
            match = arrange.match(vocalPattern);
        }

        // Pattern: vcv - vocal-consonant-vocal
        let vcvPattern = /vcv/;
        match = arrange.match(vcvPattern);
        while (match) {
            let i = match.index;
            letters.splice(i + 1, 0, '|');
            arrange = arrange.substring(0, i + 1) + '|' + arrange.substring(i + 1);
            match = arrange.match(vcvPattern);
        }

        // Pattern: [cvs]s - any letter followed by separator
        let sepPattern1 = /[cvs]s/;
        match = arrange.match(sepPattern1);
        while (match) {
            let i = match.index;
            letters.splice(i + 1, 0, '|');
            arrange = arrange.substring(0, i + 1) + '|' + arrange.substring(i + 1);
            match = arrange.match(sepPattern1);
        }

        // Pattern: s[cvs] - separator followed by any letter
        let sepPattern2 = /s[cvs]/;
        match = arrange.match(sepPattern2);
        while (match) {
            let i = match.index;
            letters.splice(i + 1, 0, '|');
            arrange = arrange.substring(0, i + 1) + '|' + arrange.substring(i + 1);
            match = arrange.match(sepPattern2);
        }

        return letters.join('').split('|');
    }

    splitSyllables(string) {
        const [letters, arrange] = this.splitLetters(string);
        return this.splitSyllablesFromLetters(letters, arrange);
    }
}

// Initialize the splitter
const splitter = new SyllableSplitter();

// DOM elements
const inputText = document.getElementById('inputText');
const splitBtn = document.getElementById('splitBtn');
const resultSection = document.getElementById('resultSection');
const resultContent = document.getElementById('resultContent');
const copyBtn = document.getElementById('copyBtn');
const exampleChips = document.querySelectorAll('.chip');

// Split button handler
splitBtn.addEventListener('click', () => {
    const text = inputText.value.trim();
    
    if (!text) {
        alert('Silakan masukkan teks terlebih dahulu!');
        return;
    }

    processText(text);
});

// Enter key handler
inputText.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        splitBtn.click();
    }
});

// Example chips handler
exampleChips.forEach(chip => {
    chip.addEventListener('click', () => {
        const text = chip.getAttribute('data-text');
        inputText.value = text;
        processText(text);
        
        // Smooth scroll to result
        setTimeout(() => {
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    });
});

// Copy button handler
copyBtn.addEventListener('click', () => {
    const text = resultContent.innerText;
    
    navigator.clipboard.writeText(text).then(() => {
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13.3333 4L6 11.3333L2.66667 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Tersalin!
        `;
        
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
        }, 2000);
    }).catch(err => {
        alert('Gagal menyalin teks');
        console.error('Copy failed:', err);
    });
});

// Process text function
function processText(text) {
    // Split by whitespace and punctuation
    const words = text.match(/\b[\w]+\b/g) || [];
    
    if (words.length === 0) {
        resultContent.innerHTML = '<p style="color: var(--text-muted);">Tidak ada kata yang dapat diproses.</p>';
        resultSection.style.display = 'block';
        return;
    }

    let html = '';
    
    words.forEach(word => {
        const syllables = splitter.splitSyllables(word);
        
        html += `
            <div class="word-result">
                <span class="original-word">${word}</span>
                <div class="syllables">
                    ${syllables.map(syl => `<span class="syllable">${syl}</span>`).join('')}
                </div>
            </div>
        `;
    });

    resultContent.innerHTML = html;
    resultSection.style.display = 'block';
}

// Add smooth animations on load
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});
