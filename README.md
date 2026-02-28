# DigitVision – ML-based Digit Recognition System

---

## About

**DigitVision** is a machine learning project that recognizes handwritten digits.  
It features a web interface where users can draw digits and get real-time predictions from the trained ML model.  

This project was built to combine **machine learning** and **frontend development**, providing a practical, interactive application.

---

## Features

- Recognizes handwritten digits (0-9) using a trained ML model  
- Interactive web interface to draw digits  
- Real-time predictions  
- Basic frontend-backend integration  

---

## Technologies Used

- **Machine Learning:** Python, TensorFlow / Keras
- **Frontend:** React, TypeScript, Tailwind CSS  
- **Backend:** Django (Python) / MySql  
- **Development Tools:** Vite, npm  

---

## Getting Started

To run the project locally, follow these steps:

1. **Clone the repository**  
   Download a copy of the project to your computer:

   ```bash
   git clone <Yhttps://github.com/asuCON/Digit-Recognition-system>

2. **Open the project folder**

   ```bash
   cd <Digit Recognition>
   ```

3. **Install frontend dependencies**

   ```bash
   npm install
   ```

4. **Start the frontend development server**

   ```bash
   npm run dev
   ```

5. **Run the backend (if applicable)**
   Make sure your ML model server is running. For example, with Python Flask:

   ```bash
   python manage.py
   ```

Now the application should be running locally. Open your browser to see the interface and start testing digit recognition.

---

## Project Structure

* **frontend/** – React application
* **backend/** – ML model server and API (if applicable)

---

## How It Works

1. User draws a digit on the web interface.
2. Frontend sends the drawing to the backend.
3. The ML model processes the input and predicts the digit.
4. The result is displayed instantly on the interface.

---

## Deployment

To deploy this project:

1. Build the frontend for production:

```bash
npm run build
```

2. Deploy the frontend using any static hosting platform (Vercel, Netlify).
3. Make sure the backend server (ML model API) is running and accessible if required.

---

## Contributing

Contributions are welcome! You can:

* Open an issue if you find bugs or have suggestions
* Submit pull requests for improvements
* Ensure your code is clean and follows best practices

---

## Author

**Sudip Rasaili**
Bachelor’s Student | Aspiring Software Developer
