# 🚀 Travel Booking AI for Remote Workers

A conversational AI platform that books complete trips (flights + accommodation) for remote workers using natural language processing.

## 🎯 Core Features (MVP)

**Step 0: Gmail OAuth Login** - Secure authentication with user's Gmail account  
**Step 2: Text Analysis** - Extract travel information from natural language using GPT API  
**Step 3: Follow-up Questions** - Ask clarifying questions until all information is collected  
**Step 5: Search & Compare** - Find best flight + accommodation options using Amadeus API  
**Step 7: Email Booking** - Send complete travel package to customer via Gmail OAuth  

## 🏗️ Simple & Modular Architecture

```
TravelChatbot/
├── app.py              # 🚀 Main application (Steps 0,2,3,5,7)
├── models.py           # 📊 Data models (TravelRequest, TravelPackage)
├── travel_ai.py        # 🧠 AI service (Steps 2 & 3)
├── search_service.py   # 🔍 Search service (Step 5)
├── email_service.py    # 📧 Email service (Step 7)
├── gmail_auth.py       # 🔐 Gmail OAuth service (Step 0)
├── config.py           # ⚙️ Configuration management
├── test_app.py         # 🧪 Simple tests
└── requirements.txt    # 📦 Dependencies
```

**Key Design Principles:**
- ✅ **Simple** - Minimal code, maximum functionality
- ✅ **Modular** - Each service handles one responsibility  
- ✅ **Scalable** - Easy to add new features (voice, hotels, payments)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env File
```bash
# OpenAI API (Required)
OPENAI_API_KEY=your_openai_api_key_here

# SMTP Email (Optional - Gmail OAuth is preferred)
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here

# Amadeus API (Optional - uses mock data without it)
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here
```

### 3. Set up Gmail OAuth (Recommended)
```bash
python gmail_auth.py
```
This will:
- Guide you through Google Cloud Console setup
- Authenticate your Gmail account
- Enable secure email sending

### 4. Run the AI
```bash
python app.py
```

### 5. Start Booking!
```
You: Book a trip from Porto to London next weekend for 3 days under 500 euros
🤖 Travel AI: Perfect! I found a great travel package for you...
```

## 💬 How It Works

### Step 0: Gmail OAuth Login
```python
# Secure Gmail authentication
gmail_auth = GmailAuthService()
gmail_auth.authenticate()  # Opens browser for OAuth flow
user_email = gmail_auth.get_user_email()  # Auto-fills user email
```

### Step 2: Text Analysis (GPT API)
```python
# Extract structured information from natural language
user_input = "Book a flight from Porto to London next Friday for 3 days"
ai_result = travel_ai.extract_travel_info(user_input)
# → origin="Porto", destination="London", departure_date="2024-01-19", duration_days=3
```

### Step 3: Follow-up Questions (GPT API)
```python
# Ask for missing information
if not ai_result["is_complete"]:
    follow_up = "What's your email address so I can send you the booking details?"
```

### Step 5: Search Best Options (Amadeus API)
```python
# Search for best flight + accommodation (1 option each)
package = search_service.search_best_package(travel_request)
# → FlightOption + AccommodationOption + total_price
```

### Step 7: Send via Gmail OAuth
```python
# Send complete travel package using authenticated Gmail
email_service.send_travel_package(travel_request, package)
# → Secure Gmail API sending with professional HTML email
```

## 🧪 Testing

```bash
# Run simple tests
python test_app.py

# Test individual components
python -c "from search_service import SearchService; print('✅ Search OK')"
```

## 🔧 Configuration

### Required:
- **OpenAI API Key** - For natural language processing
- **Email Credentials** - For sending booking confirmations

### Optional:
- **Amadeus API Keys** - For real flight data (uses mock data without it)

## 🎯 Business Model Ready

### Revenue Streams:
1. **Commission on bookings** - Partner with Kiwi.com, Booking.com
2. **Subscription model** - Premium features for frequent travelers  
3. **White label** - License to travel agencies
4. **Corporate accounts** - Bulk booking for remote teams

### Cost Optimization:
- **Smart caching** - Reduce API calls
- **Mock data fallback** - Works without expensive APIs
- **Minimal dependencies** - Low hosting costs

## 🚀 Expansion Roadmap

### Phase 1 (Current): Core MVP
- ✅ Text analysis & extraction
- ✅ Follow-up questions
- ✅ Flight + accommodation search
- ✅ Email booking confirmations

### Phase 2: Voice & UI
- 🔄 **Step 1**: Voice transcription (speech-to-text)
- 🔄 **Step 4**: Text-to-speech responses
- 🔄 **Step 0**: Gmail OAuth login
- 🔄 **Step 8**: Payment integration (Kiwi.com referrals)

### Phase 3: Advanced Features
- 🔄 **Step 6**: Hotel comparison with scraped reviews
- 🔄 Multi-city trips
- 🔄 Group bookings
- 🔄 Travel insurance
- 🔄 Visa requirements

### Phase 4: Scale
- 🔄 Mobile app
- 🔄 Corporate dashboard
- 🔄 Analytics & insights
- 🔄 Multi-language support

## 🔐 Security & Privacy

- **Environment variables** - API keys in .env (not committed)
- **Email encryption** - TLS/SSL for email sending
- **Data privacy** - No persistent storage of personal data
- **Rate limiting** - Built-in API usage optimization

## 💰 Cost Structure

### Development (Current):
- **OpenAI API**: ~$0.002 per request (GPT-3.5-turbo)
- **Amadeus API**: Free test tier (real data)
- **Email**: Free with Gmail SMTP
- **Hosting**: ~$5/month (simple VPS)

### Production Scale:
- **OpenAI**: ~$100/month for 50k requests
- **Amadeus**: ~$200/month for real bookings
- **Infrastructure**: ~$50/month for scaling

## 🎯 Why This Architecture?

### ✅ Entrepreneur-Friendly:
- **Fast to market** - Working MVP in minimal code
- **Low initial costs** - Uses free/cheap APIs
- **Easy to pitch** - Clear value proposition
- **Scalable foundation** - Add features incrementally

### ✅ Tech-Optimized:
- **Single responsibility** - Each service does one thing well
- **Loose coupling** - Easy to swap components
- **Clear interfaces** - Simple to extend
- **Battle-tested stack** - Python + OpenAI + REST APIs

### ✅ Business-Optimized:
- **Revenue ready** - Booking links integrated
- **Cost efficient** - Smart caching and fallbacks
- **Market validated** - Solves real remote worker pain points
- **Partnership ready** - Easy to integrate with booking platforms

## 🚀 Get Started

1. **Clone & setup** (5 minutes)
2. **Get API keys** (10 minutes)  
3. **Test the flow** (5 minutes)
4. **Start booking trips!** 

**Total setup time: 20 minutes to working travel AI** ✨

---

**Built for entrepreneurs who want to move fast and scale smart** 🚀 