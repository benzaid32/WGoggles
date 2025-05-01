# Whisky Goggles - BAXATHON Challenge Entry

![Whisky Goggles](https://github.com/username/whisky-goggles/raw/main/public/logo.png)

## [Live Demo](http://whiskygoggles.vercel.app/) | [Demo Video](https://youtube.com/shorts/6DkKxBOj9V8?feature=share)

## Overview
Whisky Goggles is an advanced computer vision application that allows users to instantly identify and track whisky bottles by simply taking a photo. Built for the BAXATHON challenge, this system combines state-of-the-art image recognition with a sleek, mobile-first user interface to create a seamless whisky identification experience.

The application accurately matches bottle images against BAXUS's database of 500 premium whisky bottles, providing users with precise identification and up-to-date market pricing information.

## Key Features
- **Instant Whisky Recognition**: Identify bottles by taking a photo or uploading an image
- **Precise Batch Code Detection**: Accurately identifies specific batch variants (e.g., Larceny Barrel Proof C924 vs B522)
- **Price Comparison**: View market and retail pricing data for identified bottles
- **Mobile-First Design**: Premium UI optimized for in-store use on mobile devices
- **Scan History**: Track previously scanned bottles with timestamps
- **Camera Integration**: Use your device camera to capture bottle images directly
- **Responsive UI**: Beautiful interface that works across all device sizes

## Technical Architecture

### System Overview
- **Frontend**: Next.js with TypeScript, deployed on Vercel
- **Backend**: Python Flask API with OpenAI GPT-4o vision model integration, hosted on EC2
- **API Communication**: RESTful API with structured JSON responses
- **Data Storage**: SQLite database for whisky bottle information

### Frontend (Next.js)
- **Framework**: React with Next.js and TypeScript
- **Styling**: Tailwind CSS with custom whisky-themed components
- **State Management**: Context API for application state
- **UI Components**: Custom components with Framer Motion animations
- **API Integration**: Axios for backend communication with error handling

### Backend (Flask)
- **API Framework**: Python Flask with RESTful endpoints
- **Computer Vision**: OpenAI GPT-4o vision model integration
- **Bottle Database**: SQLite with 500+ premium whisky entries
- **Batch Recognition**: Advanced regex pattern matching for batch codes
- **Variant Mapping**: Comprehensive system to map detected names to exact BAXUS entries

### Computer Vision Approach
The recognition system uses a sophisticated approach:

1. **Image Analysis Pipeline**:
   - Image submission via web interface or direct API call
   - Base64 encoding and optimization for API processing
   - Comprehensive prompt engineering to guide the vision model

2. **Advanced Recognition System**:
   - GPT-4o vision model for initial bottle detection
   - Custom post-processing to standardize detected bottle names
   - Proprietary bottle mapping system for variant identification
   - Specialized batch code extraction with regex pattern matching

3. **Exact BAXUS Database Matching**:
   - Direct mapping system for all 500 BAXUS bottle entries
   - Advanced key identifier extraction for brand, batch code, and age statement
   - Special handling for challenging bottle variants

## Installation & Setup

### Prerequisites
- Node.js 18+
- Python 3.8+
- OpenAI API key with access to GPT-4o

### Backend Setup
```bash
# Navigate to backend directory
cd bwgy-main

# Install required packages
pip install -r requirements.txt

# Add your OpenAI API key to direct_key.env
echo "OPENAI_API_KEY=your_api_key_here" > direct_key.env

# Start the backend server
python app.py
```

### Frontend Setup
```bash
# Navigate to root directory
cd ..

# Install dependencies
npm install

# Start the development server
npm run dev
```

## Project Structure
```
whisky-goggles/
├── app/                    # Next.js frontend application
│   ├── components/         # UI components
│   ├── context/            # React context providers
│   └── types/              # TypeScript definitions
├── public/                 # Static assets
│   └── logo.png            # Whisky Goggles logo
├── bwgy-main/              # Flask backend application
│   ├── app.py              # Main Flask API endpoints
│   ├── data/               # Database and bottle annotations
│   │   ├── db/             # SQLite database files
│   │   └── bottle_annotations/ # JSON files for all bottles
│   └── modules/            # Core components
│       ├── whisky_service.py    # Unified whisky recognition service
│       ├── bottle_variants.py   # Bottle variant handler
│       ├── config.py            # Configuration settings
│       └── utils.py             # Utility functions
└── package.json            # Frontend dependencies
```

## API Integration
The frontend communicates with the backend through a RESTful API:

- **Recognition Endpoint**: `/recognize` accepts image uploads and returns structured whisky data
- **Response Format**: Nested JSON with `results[0].matches[0]` containing bottle information
- **Error Handling**: Comprehensive error handling for API failures, invalid images, and server errors

## Deployment
- **Frontend**: Deployed on Vercel at [whiskygoggles.vercel.app](http://whiskygoggles.vercel.app/)
- **Backend**: Hosted on Amazon EC2 instance at `http://16.16.65.102:5000`

## Future Enhancements
- Multi-bottle detection in a single image
- Price trend analysis and historical data
- User collections and wishlists
- Barcode scanning integration
- Community tasting notes and ratings

## Contributors
- [Your Name] - Full Stack Developer

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- BAXUS for providing the whisky bottle database
- OpenAI for the GPT-4o vision model
- The BAXATHON competition for the opportunity
