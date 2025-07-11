# AI Chatbot with Vision 🤖

A modern, full-stack AI chatbot application that supports both text conversations and image analysis using OpenAI's GPT models.

## ✨ Features

- **Text Chat**: Natural conversation with GPT-4o-mini
- **Image Analysis**: Upload images and ask questions about them using GPT-4o
- **Real-time UI**: Responsive chat interface with typing indicators
- **Error Handling**: Robust error handling and user feedback
- **File Validation**: Secure file upload with size and type validation
- **Mobile Responsive**: Works seamlessly on desktop and mobile devices
- **Modern UI**: Clean, gradient-based design with animations

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **OpenAI API** - GPT-4o and GPT-4o-mini models
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server for production deployment
- **Python-dotenv** - Environment variable management

### Frontend
- **Next.js** - React framework for production
- **React** - Component-based UI library
- **CSS Modules** - Scoped styling
- **Modern JavaScript** - ES6+ features

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd Backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment configuration**
   ```bash
   cp config.example .env
   # Edit .env with your OpenAI API key
   ```

4. **Run the server**
   ```bash
   python main.py
   ```
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd Frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment configuration**
   ```bash
   # Create .env.local
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

## 🐳 Docker Setup

### Backend Docker
```bash
cd Backend
docker build -t chatbot-backend .
docker run -p 8000:8000 --env-file .env chatbot-backend
```

### Frontend Docker
```bash
cd Frontend
docker build -t chatbot-frontend .
docker run -p 3000:3000 chatbot-frontend
```

## 📱 API Documentation

### Health Check
```http
GET /health
```

### Text Chat
```http
POST /chat
Content-Type: application/json

{
  "prompt": "Hello, how are you?"
}
```

### Image Chat
```http
POST /chat/image
Content-Type: multipart/form-data

{
  "prompt": "What's in this image?",
  "file": [image file]
}
```

### Response Format
```json
{
  "response": "AI response text",
  "model_used": "gpt-4o-mini",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🔒 Security Features

- **Input Validation**: Comprehensive request validation
- **File Size Limits**: Maximum 10MB file uploads
- **File Type Validation**: Only image files allowed
- **CORS Configuration**: Configurable cross-origin requests
- **Error Handling**: Secure error messages without data leakage

## 🎨 UI Features

- **Gradient Background**: Modern visual design
- **Message Animations**: Smooth fade-in effects
- **Loading States**: Visual feedback during API calls
- **Image Previews**: Thumbnail previews before sending
- **Auto-scroll**: Automatic scroll to latest messages
- **Responsive Design**: Mobile-first approach
- **Error Messages**: User-friendly error notifications

## 📂 Project Structure

```
Chatbot/
├── Backend/
│   ├── app.py              # FastAPI application
│   ├── main.py             # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── config.example      # Environment configuration
├── Frontend/
│   ├── components/
│   │   ├── app.js          # Main app component
│   │   ├── messageList.js  # Chat interface
│   │   └── messageList.module.css
│   ├── pages/
│   │   └── index.js        # Home page
│   └── package.json        # Node.js dependencies
└── README.md
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
OPENAI_API_KEY=your_api_key_here
CORS_ORIGINS=http://localhost:3000,https://yourapp.com
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚀 Deployment

### Backend Deployment (Heroku)
```bash
git subtree push --prefix Backend heroku main
```

### Frontend Deployment (Vercel)
```bash
cd Frontend
vercel --prod
```

### Environment Configuration for Production
- Set `OPENAI_API_KEY` in your hosting platform
- Update `CORS_ORIGINS` with your frontend domain
- Set `NEXT_PUBLIC_API_URL` to your backend URL

## 🧪 Testing

### Backend Tests
```bash
cd Backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd Frontend
npm test
```

## 📊 Performance

- **Response Time**: < 2s for text chat
- **Image Processing**: < 10s for image analysis
- **File Upload**: Up to 10MB images
- **Concurrent Users**: Scalable with FastAPI

## 🔄 Future Enhancements

- [ ] User authentication and sessions
- [ ] Chat history persistence
- [ ] Multiple conversation threads
- [ ] Custom AI personas
- [ ] Voice input/output
- [ ] Real-time collaborative chats
- [ ] Advanced image processing features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created as a portfolio project demonstrating full-stack development skills with modern AI integration.

## 🙏 Acknowledgments

- OpenAI for the GPT models
- FastAPI team for the excellent framework
- Next.js team for the React framework
- The open-source community

---

**⭐ Star this repository if you found it helpful!** 