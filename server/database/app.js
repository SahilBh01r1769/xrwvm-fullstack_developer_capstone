const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');

const app = express();
const port = 3030;

app.use(cors());
app.use(express.json());                    // Better than body-parser for modern use
app.use(express.urlencoded({ extended: true }));

const reviews_data = JSON.parse(fs.readFileSync("reviews.json", 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync("dealerships.json", 'utf8'));

mongoose.connect("mongodb://mongo_db:27017/", { 'dbName': 'dealershipsDB' })
    .then(() => console.log("✅ MongoDB Connected"))
    .catch(err => console.error("❌ MongoDB Connection Error:", err));

const Reviews = require('./review');
const Dealerships = require('./dealership');

// Initialize Data (Run once)
try {
    Reviews.deleteMany({}).then(() => {
        Reviews.insertMany(reviews_data['reviews']);
        console.log("✅ Reviews data inserted");
    });

    Dealerships.deleteMany({}).then(() => {
        Dealerships.insertMany(dealerships_data['dealerships']);
        console.log("✅ Dealerships data inserted");
    });
} catch (error) {
    console.error("Error inserting initial data:", error);
}

// ====================== ROUTES ======================

// Home Route
app.get('/', async (req, res) => {
    res.send("Welcome to the Dealerships Mongoose API");
});

// Fetch all reviews
app.get('/fetchReviews', async (req, res) => {
    try {
        const documents = await Reviews.find();
        res.json(documents);
    } catch (error) {
        res.status(500).json({ error: 'Error fetching reviews' });
    }
});

// Fetch reviews by dealer ID
app.get('/fetchReviews/dealer/:id', async (req, res) => {
    try {
        const documents = await Reviews.find({ dealership: req.params.id });
        res.json(documents);
    } catch (error) {
        res.status(500).json({ error: 'Error fetching reviews' });
    }
});

// ✅ Fetch all dealerships
app.get('/fetchDealers', async (req, res) => {
    try {
        const dealers = await Dealerships.find();
        res.json(dealers);
    } catch (error) {
        res.status(500).json({ error: 'Error fetching dealerships' });
    }
});

// ✅ Fetch dealerships by state
app.get('/fetchDealers/:state', async (req, res) => {
    try {
        const dealers = await Dealerships.find({ state: req.params.state.toUpperCase() });
        res.json(dealers);
    } catch (error) {
        res.status(500).json({ error: 'Error fetching dealerships by state' });
    }
});

// ✅ Fetch single dealer by ID
app.get('/fetchDealer/:id', async (req, res) => {
    try {
        const dealer = await Dealerships.findOne({ id: parseInt(req.params.id) });
        if (!dealer) {
            return res.status(404).json({ error: 'Dealer not found' });
        }
        res.json(dealer);
    } catch (error) {
        res.status(500).json({ error: 'Error fetching dealer' });
    }
});

// Insert new review
app.post('/insert_review', async (req, res) => {
    try {
        const data = req.body;

        const documents = await Reviews.find().sort({ id: -1 });
        let new_id = documents.length > 0 ? documents[0]['id'] + 1 : 1;

        const review = new Reviews({
            id: new_id,
            name: data['name'],
            dealership: data['dealership'],
            review: data['review'],
            purchase: data['purchase'],
            purchase_date: data['purchase_date'],
            car_make: data['car_make'],
            car_model: data['car_model'],
            car_year: data['car_year'],
        });

        const savedReview = await review.save();
        res.json(savedReview);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Error inserting review' });
    }
});

// Start Server
app.listen(port, () => {
    console.log(`🚀 Server running on http://localhost:${port}`);
});