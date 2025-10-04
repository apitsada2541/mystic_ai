from flask import Flask, render_template_string, request, session
import requests
import google.genai as genai
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

ZODIAC_SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

FREQUENCIES = ["daily", "weekly", "monthly"]

def get_horoscope(sign, freq):
    try:
        if freq == 'daily':
            url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign}&day=today"
        else:
            url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/{freq}?sign={sign}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['data']['horoscope_data']
        else:
            return "Could not fetch horoscope."
    except:
        return "Could not fetch horoscope."

def get_tarot_cards(num_cards=3):
    """Get random tarot cards from API"""
    url = f"https://tarotapi.dev/api/v1/cards/random?n={num_cards}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['cards']
    except:
        pass
    return [
        {"name": "The Star", "meaning_up": "Hope, inspiration, and spiritual guidance"},
        {"name": "Three of Cups", "meaning_up": "Friendship, celebration, and community"},
        {"name": "Ace of Pentacles", "meaning_up": "New opportunities and material success"}
    ]

def combined_reading_with_gemini(horoscope_text, tarot_cards):
    """Create a structured fortune reading combining horoscope and tarot cards"""
    try:
        client = genai.Client()
        
        tarot_summary = "\n".join([f"• {card['name']}: {card['meaning_up']}" for card in tarot_cards])
        card_names = ", ".join([card['name'] for card in tarot_cards])
        
        prompt = f"""
Create a comprehensive mystical fortune reading with exactly these three sections. Keep it concise but clearly separated:

🌟 SECTION 1: Your Horoscope Foundation
Based on this horoscope: "{horoscope_text}"
Write 1-2 short paragraphs explaining the main themes in simple, personal language.

🔮 SECTION 2: Your Tarot Card Insights
Cards drawn: {card_names}

Card meanings:
{tarot_summary}

For each card, write 1-2 sentences explaining its meaning. Keep this section to 1-2 paragraphs total.

✨ SECTION 3: Your Complete Reading
Write 1-2 paragraphs showing how the horoscope and tarot align. Include specific guidance for love, career, and personal growth.

IMPORTANT FORMATTING RULES:
- Use the exact section headers with emojis as shown above
- Keep each section to 1-2 paragraphs maximum
- Separate sections with line breaks
- Do not use asterisks or special characters within the text content
- Use warm, encouraging tone
- Make sure sections are clearly distinct
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        return response.text
    except Exception as e:
        # Return None to signal error occurred
        return None

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✨ Mystic AI ✨</title>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;700&family=Cinzel:wght@400;600&display=swap" rel="stylesheet">
    <style>
        html, body {
            min-height: 100vh;
            height: 100%;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: #764ba2; /* Fallback solid purple */
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Quicksand', sans-serif;
            color: #fff;
            position: relative;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        
        h1 {
            font-family: 'Cinzel', serif;
            font-size: 3rem;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, #fff, #e0c3fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .form-container {
            background: rgba(60, 24, 90, 0.85); /* Less transparent, richer purple */
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin: 30px auto;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            color: #fff;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 10px;
            font-size: 1.2rem;
            font-weight: 500;
            color: #e0c3fc;
        }
        
        select {
            width: 100%;
            max-width: 300px;
            padding: 15px 20px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            font-size: 1rem;
            font-family: 'Quicksand', sans-serif;
            text-align: center;
            text-align-last: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            appearance: none;
            background-image: url('data:image/svg+xml;charset=US-ASCII,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 5"><path fill="%23666" d="m0 1 2 2 2-2z"/></svg>');
            background-repeat: no-repeat;
            background-position: right 15px center;
            background-size: 12px;
            padding-right: 40px;
        }
        
        .deck-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 30px 0;
            position: relative;
            height: 180px;
        }
        
        .deck-stack {
            position: relative;
            width: 120px;
            height: 180px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .deck-stack:hover {
            transform: scale(1.05);
        }
        
        .deck-card {
            position: absolute;
            width: 120px;
            height: 180px;
            background: linear-gradient(45deg, #4a148c, #7b1fa2);
            border-radius: 15px;
            border: 3px solid rgba(255,255,255,0.5);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            padding: 15px;
            color: white;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }
        
        .deck-card:nth-child(1) { transform: rotate(-2deg) translate(-2px, 2px); }
        .deck-card:nth-child(2) { transform: rotate(-1deg) translate(-1px, 1px); }
        .deck-card:nth-child(3) { transform: rotate(0deg); }
        .deck-card:nth-child(4) { transform: rotate(1deg) translate(1px, -1px); }
        .deck-card:nth-child(5) { transform: rotate(2deg) translate(2px, -2px); }
        
        .deck-text {
            font-size: 14px;
            text-align: center;
            margin-top: 10px;
            color: #fff;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        
        .card-count {
            margin: 10px 0;
            font-size: 0.9rem;
            color: #fff;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        
        .submit-btn {
            background: linear-gradient(45deg, #ff6b6b, #ee5a6f);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.2rem;
            font-weight: 600;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            font-family: 'Quicksand', sans-serif;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        .submit-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(238, 90, 111, 0.5);
        }
        
        .submit-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .zodiac-bg {
            position: absolute;
            font-size: 15rem;
            opacity: 0.1;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: -1;
        }
        
        .result-container {
            background: rgba(60, 24, 90, 0.85); /* Less transparent, richer purple */
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 30px;
            margin-top: 30px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            text-align: left;
            line-height: 1.6;
            white-space: pre-line;
            color: #fff;
        }
        
        .error-container {
            background: rgba(120, 24, 60, 0.85); /* Less transparent, richer purple-red */
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 30px;
            margin-top: 30px;
            border: 1px solid rgba(255, 107, 107, 0.4);
            text-align: center;
            line-height: 1.6;
            color: #fff;
        }
        
        .result-title {
            font-family: 'Cinzel', serif;
            font-size: 1.8rem;
            margin-bottom: 20px;
            text-align: center;
            color: #fff;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        
        .error-title {
            font-family: 'Cinzel', serif;
            font-size: 1.8rem;
            margin-bottom: 20px;
            text-align: center;
            color: #fff;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 4px solid #fff;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .stars {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -2;
        }
        
        .star {
            position: absolute;
            background: white;
            border-radius: 50%;
            animation: twinkle 3s infinite;
        }
        
        @keyframes twinkle {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 1; }
        }
        
        /* Mobile Safari specific fixes */
        @supports (-webkit-touch-callout: none) {
            .form-container,
            .result-container,
            .error-container {
                background: rgba(60, 24, 90, 0.95); /* More opaque for Safari */
            }
        }
    </style>
</head>
<body>
    <div class="stars" id="stars"></div>
    
    {% if selected_sign %}
    <div class="zodiac-bg">{{ get_zodiac_symbol(selected_sign) }}</div>
    {% endif %}
    
    <div class="container">
        <h1>✨ Mystic AI ✨</h1>
        
        <div class="form-container">
            <form method="post" id="horoscopeForm">
                <div class="form-group">
                    <label for="sign">🌟 Select your Zodiac Sign:</label>
                    <select name="sign" id="sign" required>
                        {% for sign in signs %}
                        <option value="{{sign}}" {% if sign==selected_sign %}selected{% endif %}>{{sign.capitalize()}} {{ get_zodiac_symbol(sign) }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="freq">🔮 How far in the future?:</label>
                    <select name="freq" id="freq" required>
                        {% for f in freqs %}
                        <option value="{{f}}" {% if f==selected_freq %}selected{% endif %}>{{f.capitalize()}}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>🃏 Draw 3 Cards from the Mystic Deck:</label>
                    <div class="deck-container">
                        <div class="deck-stack" onclick="drawCards()">
                            <div class="deck-card">🔮</div>
                            <div class="deck-card">🔮</div>
                            <div class="deck-card">🔮</div>
                            <div class="deck-card">🔮</div>
                            <div class="deck-card">🔮</div>
                        </div>
                    </div>
                    <div class="deck-text">Click the deck to draw your 3 cards</div>
                    
                    <div class="card-count" id="cardCount">
                        Cards drawn: <span id="drawnCount">0</span>/3
                    </div>
                </div>
                
                <input type="hidden" name="cards_drawn" id="cardsDrawnInput" value="false">
                
                <button type="submit" class="submit-btn" id="submitBtn" disabled>🔮 Reveal My Destiny</button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>✨ The universe is weaving your destiny... ✨</p>
            </div>
        </div>
        
        {% if reading %}
        <div class="result-container">
            <h3 class="result-title">🌙 Your Complete Mystical Reading 🌙</h3>
            <div>{{ reading }}</div>
        </div>
        {% endif %}
        
        {% if error_message %}
        <div class="error-container">
            <h3 class="error-title">🌟 Celestial Message 🌟</h3>
            <div>{{ error_message }}</div>
        </div>
        {% endif %}
    </div>
    
    <script>
        let cardsDrawn = false;
        
        function drawCards() {
            if (cardsDrawn) return;
            
            cardsDrawn = true;
            document.getElementById('cardsDrawnInput').value = 'true';
            document.getElementById('submitBtn').disabled = false;
            document.getElementById('drawnCount').textContent = '3';
            
            // Change deck appearance to show cards have been drawn
            const deckStack = document.querySelector('.deck-stack');
            deckStack.style.opacity = '0.7';
            deckStack.style.cursor = 'not-allowed';
        }
        
        // Create twinkling stars
        function createStars() {
            const starsContainer = document.getElementById('stars');
            for (let i = 0; i < 50; i++) {
                const star = document.createElement('div');
                star.className = 'star';
                star.style.left = Math.random() * 100 + '%';
                star.style.top = Math.random() * 100 + '%';
                star.style.width = star.style.height = Math.random() * 3 + 1 + 'px';
                star.style.animationDelay = Math.random() * 3 + 's';
                starsContainer.appendChild(star);
            }
        }
        
        // Show loading animation
        document.getElementById('horoscopeForm').addEventListener('submit', function() {
            document.getElementById('loading').style.display = 'block';
        });
        
        createStars();
    </script>
</body>
</html>
"""

def get_zodiac_symbol(sign):
    symbols = {
        'aries': '♈', 'taurus': '♉', 'gemini': '♊', 'cancer': '♋',
        'leo': '♌', 'virgo': '♍', 'libra': '♎', 'scorpio': '♏',
        'sagittarius': '♐', 'capricorn': '♑', 'aquarius': '♒', 'pisces': '♓'
    }
    return symbols.get(sign, '✨')

@app.route('/', methods=['GET', 'POST'])
def home():
    reading = None
    error_message = None
    selected_sign = "aries"
    selected_freq = "daily"
    
    if request.method == 'POST':
        try:
            selected_sign = request.form.get('sign')
            selected_freq = request.form.get('freq')
            cards_drawn = request.form.get('cards_drawn') == 'true'
            
            if cards_drawn:
                # Get horoscope
                raw_text = get_horoscope(selected_sign, selected_freq)
                
                # Get tarot cards (3 random ones from API)
                tarot_cards = get_tarot_cards(3)
                
                # Create combined reading
                reading = combined_reading_with_gemini(raw_text, tarot_cards)
                
                if reading is None:
                    error_message = "🌟 The cosmic energies are currently depleted from many seekers today. The mystical AI needs time to recharge under the starlight. Please return tomorrow when the celestial forces have realigned! ✨"
        
        except Exception as e:
            error_message = "🌟 The stars are experiencing some turbulence right now. Please try again in a moment when the cosmic winds calm. ✨"
    
    return render_template_string(
        HTML_TEMPLATE, signs=ZODIAC_SIGNS, freqs=FREQUENCIES,
        reading=reading, error_message=error_message,
        selected_sign=selected_sign, selected_freq=selected_freq, 
        get_zodiac_symbol=get_zodiac_symbol
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
