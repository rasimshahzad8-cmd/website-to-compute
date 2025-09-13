import os
import zipfile

# Define project structure
files = {
    "README.md": """# E-commerce App
This is a full-stack marketplace (Amazon/Daraz style).
## Tech
- Backend: Node.js + Express + MongoDB
- Frontend: Next.js (React)
- Auth: JWT + Google OAuth
- Payments: COD, PayPal, Easypaisa, JazzCash (stubs)
- Chat: Socket.io
- Role system: CEO, Admin, Seller, Buyer
## Setup
1. cd backend && npm install
2. cd frontend && npm install
3. docker-compose up
""",

    "docker-compose.yml": """version: "3.9"
services:
  mongo:
    image: mongo:6
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - MONGO_URI=mongodb://mongo:27017/ecommerce
      - JWT_SECRET=supersecret
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  mongo_data:
""",

    "backend/package.json": """{
  "name": "ecommerce-backend",
  "version": "1.0.0",
  "main": "server.js",
  "type": "module",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "bcrypt": "^5.1.0",
    "cors": "^2.8.5",
    "dotenv": "^16.0.3",
    "express": "^4.18.2",
    "jsonwebtoken": "^9.0.0",
    "mongoose": "^7.0.0",
    "nodemailer": "^6.9.1",
    "socket.io": "^4.6.1"
  },
  "devDependencies": {
    "nodemon": "^2.0.22"
  }
}""",

    "backend/server.js": """import express from "express";
import mongoose from "mongoose";
import cors from "cors";
import dotenv from "dotenv";
import authRoutes from "./routes/auth.js";
import productRoutes from "./routes/product.js";

dotenv.config();
const app = express();
app.use(express.json());
app.use(cors());

// Routes
app.use("/api/auth", authRoutes);
app.use("/api/products", productRoutes);

app.get("/", (req, res) => res.send("E-commerce backend running"));

mongoose.connect(process.env.MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => app.listen(5000, () => console.log("Backend on http://localhost:5000")))
  .catch(err => console.error(err));
""",

    "backend/models/User.js": """import mongoose from "mongoose";

const userSchema = new mongoose.Schema({
  name: String,
  email: { type: String, unique: true },
  password: String,
  role: { type: String, enum: ["CEO", "Admin", "Seller", "Buyer"], default: "Buyer" },
  verified: { type: Boolean, default: false }
});

export default mongoose.model("User", userSchema);
""",

    "backend/models/Product.js": """import mongoose from "mongoose";

const productSchema = new mongoose.Schema({
  name: String,
  description: String,
  price: Number,
  stock: Number,
  images: [String],
  seller: { type: mongoose.Schema.Types.ObjectId, ref: "User" },
  rating: { type: Number, default: 0 }
});

export default mongoose.model("Product", productSchema);
""",

    "backend/routes/auth.js": """import express from "express";
import User from "../models/User.js";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

const router = express.Router();

router.post("/register", async (req, res) => {
  const { name, email, password, role } = req.body;
  const hashed = await bcrypt.hash(password, 10);
  try {
    const user = await User.create({ name, email, password: hashed, role });
    res.json(user);
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

router.post("/login", async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user) return res.status(400).json({ error: "User not found" });
  const valid = await bcrypt.compare(password, user.password);
  if (!valid) return res.status(400).json({ error: "Invalid password" });
  const token = jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET);
  res.json({ token, role: user.role });
});

export default router;
""",

    "backend/routes/product.js": """import express from "express";
import Product from "../models/Product.js";

const router = express.Router();

router.post("/", async (req, res) => {
  try {
    const product = await Product.create(req.body);
    res.json(product);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.get("/", async (req, res) => {
  const products = await Product.find();
  res.json(products);
});

export default router;
""",

    "frontend/package.json": """{
  "name": "ecommerce-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "13.4.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "axios": "^1.3.4"
  }
}""",

    "frontend/pages/index.js": """import axios from "axios";
import { useEffect, useState } from "react";

export default function Home() {
  const [products, setProducts] = useState([]);
  useEffect(() => {
    axios.get("http://localhost:5000/api/products")
      .then(res => setProducts(res.data));
  }, []);

  return (
    <div>
      <h1>E-commerce Store</h1>
      {products.map(p => (
        <div key={p._id}>
          <h2>{p.name}</h2>
          <p>{p.description}</p>
          <p>${p.price}</p>
        </div>
      ))}
    </div>
  );
}
"""
}

# Write ZIP file
with zipfile.ZipFile("ecommerce-app.zip", "w") as zipf:
    for path, content in files.items():
        zipf.writestr(path, content)

print("✅ ecommerce-app.zip generated successfully!")
